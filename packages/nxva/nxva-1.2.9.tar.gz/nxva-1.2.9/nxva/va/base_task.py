import cv2
import time
import requests
import threading
import numpy as np
import multiprocessing.resource_tracker

from nxva.streaming import MultiStreaming
from nxva.vision import images_automerge
from .shm_utils import SHMHandler
from collections import deque
from multiprocessing import shared_memory

class BaseTask:
    def __init__(self, class_names, cameras_ids, interval=0, test_mode=False, queue_size=2, namespace=None, detection_server_ip='127.0.0.1'):
        '''
        Args:
            interval: float
                the interval of task
            class_names: list
                class names = [people]
            cameras_ids: list
                the task needs to be run on which cameras
            test_mode: bool
                if test_mode is True, the task will run in single process
            queue_size: int
                the size of queue, default is 2
            namespace: str
                namespace for logger, default is None
        
        Attributes:
            register_name: str
                register name of task to detection server
                register_name = current_process().name
            test_mode: bool
                if test_mode is True, the task will run in single process
            queue: queue.Queue
                queue
            queue_lock: threading.Lock
                queue lock
            class_name_dict: dict
                the labels after label shift
                class_name_dict = {0: 'people', ...}
            cameras_num: int
                number of cameras
            width: int
                width of frame
            height: int
                height of frame
            shm_handler: SHMHandler
                SHMHandler
        
        Methods:
            _register:
                send message to detection server with socket
            _get_results_from_shm:
                get results from shared memory and put them into queue
            run:
                use frames and results to process run_once and draw_images
            get_queue:
                get frames and results from queue
            run_once:
                need to implement in subclasses to run task
            draw_images:
                need to implement in subclasses to draw images
        '''
        self.interval            = interval
        self.test_mode           = test_mode
        self.namespace           = namespace
        self.cameras_ids         = cameras_ids
        self.class_names         = class_names
        self.detection_server_ip = detection_server_ip
        
        self.queue       = deque(maxlen=queue_size)
        self.queue_lock  = threading.Lock()
        self.stop_event  = threading.Event()

        if not self.test_mode:
            shm_info = self.register_shm(cameras_ids, class_names)

            threading.Thread(
                target=self._get_results_from_shm, 
                args=(shm_info['camera_ids'],), 
                daemon=True
            ).start()

    def register_shm(self, cameras_ids, class_names):
        shm_info = self._register(cameras_ids, class_names)

        self.class_name_dict = shm_info['class_name_dict']
        self.cameras_num     = len(shm_info['camera_ids'])
        self.width           = shm_info['width']
        self.height          = shm_info['height']
        max_detection_num    = shm_info['max_detection_num']
        self.feature_dim     = shm_info['feature_dim']

        # SHMHandler
        self.shm_handler = SHMHandler(self.width, self.height, shm_info['total_cameras_num'], max_detection_num, feature_dim=self.feature_dim, namespace=self.namespace)

        return shm_info
    
    def _register(self, camera_ids, class_names):
        """
        Register task to detection server
        
        Args:
            camera_ids: list
                the task needs to be run on which cameras
                camera_ids = ['IPCAM-201', 'IPCAM-206']
            class_names: list
                class names = [people]
                
        Returns:
            shm_info: dict
                shared memory info
                {'frames_shm_name': 'frames_shm_name', 'frames_buffer_shape': (1080, 1920, 3), 'results_shm_name': 'results_shm_name', 'results_buffer_shape': (15, 6), 'class_name_dict': {0: 'people', ...}}
        """
        message = {
            'camera_ids'    : camera_ids,
            'class_names'   : class_names,
        }

        while True:
            time.sleep(5)
            try:
                response = requests.post(f"http://{self.detection_server_ip}:9453/api/detection_health", json=message)
                if response.status_code == 200:
                    break
            except:
                print("Connection to detection server failed, retrying...")

        response = requests.post(f"http://{self.detection_server_ip}:9453/api/registration_server", json=message)
        shm_info = response.json()

        return shm_info
    
    def _get_results_from_shm(self, cam_ids):
        """
        Get results from shared memory and put them into queue
        
        Args:
            cam_ids: list
                camera ids [0, 1, 2, ...]
        """
        def is_shm_alive(name):
            try:
                shm = shared_memory.SharedMemory(name=name)
                multiprocessing.resource_tracker.unregister(f'/{name}', 'shared_memory')
                shm.close()
                return True
            except:
                return False
            
        class_id = list(map(int, self.class_name_dict.keys()))
        camera_frame_counter = 0

        while True:
            health = is_shm_alive(self.shm_handler.shared_name)
            if not health:
                while True:
                    _ = self.register_shm(self.cameras_ids, self.class_names)
                    break
            frames_list = []
            results_list = []
            reid_list = []
            meta_dict = self.shm_handler.read_meta_info()
            frame_counter = meta_dict.get('frame_counter', 0)

            # 如果 frame_counter 沒有變化，則跳過
            if camera_frame_counter == frame_counter:
                time.sleep(0.01)
                continue
        
            camera_frame_counter = frame_counter

            for idx, cam_id in enumerate(cam_ids):
                frame, bbox, reid = self.shm_handler.read_frame_and_bbox(cam_id)

                results_list.append(bbox)
                frames_list.append(frame)
                reid_list.append(reid)

            filtered_results = []
            filtered_reids = []

            # Filter results and reid based on class_id
            for idx, result in enumerate(results_list):
                if result.size > 0:
                    keep_mask = np.isin(result[:, 5].astype(int), class_id)
                    filtered_result = result[keep_mask]
                    if np.any(keep_mask) and np.any(reid_list[idx]):
                        filtered_reid = reid_list[idx][keep_mask]
                    else:
                        filtered_reid = np.empty((0, self.feature_dim), dtype=reid_list[idx].dtype)
                else:
                    filtered_result = np.empty((0, 6), dtype=np.float32)
                    filtered_reid = np.empty((0, self.feature_dim), dtype=reid_list[idx].dtype)

                filtered_results.append(filtered_result)
                filtered_reids.append(filtered_reid)

            with self.queue_lock:
                self.queue.append((frames_list, filtered_results, filtered_reids))
                time.sleep(0.01)

    def run(self, show=False):
        """
        Use frames and results to process run_once and draw_images
        
        Args:
            show: bool
                if show is True, show images
        """
        next_time = time.perf_counter() + self.interval
        if show:
            cv2.namedWindow('show', cv2.WINDOW_NORMAL)
            cv2.setWindowProperty('show', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        while True:
            frames, results, reid = self.get_queue()

            if not frames:
                time.sleep(0.001)
                continue

            self.run_once(results, frames, reid)

            if show:
                if len(frames) < self.cameras_num:
                    continue
                ppl_images = self.draw_images(frames)
                if ppl_images is None:
                    continue
                m_ppl_images = images_automerge(ppl_images, (1920, 1080))
                cv2.imshow('show' ,m_ppl_images)
                key = cv2.waitKey(1)
                if key == 27:
                    break

            # Calculate the next time to send the next frame
            next_time += self.interval
            delay = next_time - time.perf_counter()
            if delay > 0:
                self.stop_event.wait(delay)
            else:
                time.sleep(0.001)

        if show:
            cv2.destroyAllWindows()

    def get_queue(self):
        """
        Get frames and results from queue
        
        Returns:
            frames: np.ndarray
                frames
            results: list
                results
        """
        if self.test_mode:
            raise NotImplementedError("Subclasses must implement 'get_queue' method")

        with self.queue_lock:
            if len(self.queue) > 0:
                frames, results, reid = self.queue.popleft()
                return frames, results, reid

        return None, None, None

    def run_once(self, results):
        raise NotImplementedError("Subclasses must implement 'run_once' method")
    
    def draw_images(self, frames):
        raise NotImplementedError("Subclasses must implement 'draw_images' method")
        

if __name__ == '__main__':
    import os
    from utilities import load_configs
    from nexva.v11 import Detector
    from dotenv import load_dotenv
    
    task_list, hyper_config, streaming_config, cameras_dict, cameras_configs_dict, all_cameras_ids = load_configs()

    load_dotenv()
    host         = os.getenv('WEB_SERVER')
    web_port     = os.getenv('WEB_SERVER_PORT')
    control_port = os.getenv('CONTROL_SERVER_PORT')
    api_config   = (host, web_port, control_port)

    # Need super_init_(test_mode = True)
    task_name = 'people_tracking'

    if task_name == 'people_tracking':
        from task.people_tracking import MultiPeopleTask
        task_manager = MultiPeopleTask(streaming_config,
                                       cameras_configs_dict[task_name],
                                       cameras_dict[task_name],
                                       hyper_config[task_name],
                                       api_config
                                       ) 

    # streaming
    stream = MultiStreaming(config='./configs/streaming.yaml',
                            reconnect_interval=30,
                            verbose=True
                            )
    stream.init_cameras()
    stream.run()

    # detector
    detector = Detector('./configs/detection_yolo11s.yaml')
    class_names = detector.class_names
    names_class = {name: class_id for class_id, name in class_names.items()}
    model_class_list = []
    class_names  = [config['class'] for _, config in hyper_config.items() if 'class' in config]
    task_class_names = list(set(name for class_name in class_names for name in class_name))
    for task_class_name in task_class_names:
        class_id = names_class.get(task_class_name)
        if class_id != None:
            model_class_list.append(class_id)
    
    detector.classes = model_class_list

    while True:
        frames, status = stream.get_frames(status=True)
        results = detector(frames)

        task_msg = task_manager.run_once(results, frames)

        ppl_images = task_manager.draw_images(frames)
        m_ppl_images = images_automerge(ppl_images, (1920, 1080))

        cv2.imshow('show' ,m_ppl_images)
        key = cv2.waitKey(1)
        if key == 27:
            break
        time.sleep(0.001)
    cv2.destroyAllWindows()