import cv2
import time
import json
import logging
import threading
import numpy as np
import torch
import orjson
import os

from pathlib import Path
from nxva.yolo.yolo import YOLO
from nxva.streaming import MultiStreaming
from .shm_utils import SHMHandler
from collections import deque
from flask import Flask, request, jsonify
from werkzeug.datastructures import FileStorage

app = Flask(__name__)

class DetectionServer:
    def __init__(self, 
                 max_detection_num, 
                 model_list, 
                 allowed_class_names, 
                 all_cameras_ids, 
                 interval=0, 
                 reid_model=None, 
                 namespace=None):
        '''
        Args:
            max_detection_num: int
                max number of detection in a frame
            model_list: list
                list of model names
                model_list = ['./configs/detection.yaml', ...]
            allowed_class_names: list
                list of class names which the task needs
                allowed_class_names = ['people', 'car', ...]
            all_cameras_ids: list
                append all cameras.yaml where in cameras's folder
            interval: int
                interval time for detection, default is 0
            namespace: str
                namespace for logger, default is None

        Attributes:
            max_detection_num: int
                max number of detection in a frame
            all_cameras_ids: list
                append all cameras.yaml where in cameras's folder
            stream: MultiStreaming
                streaming
            detector: DetectorBuilder
                detector
            model_dict: dict
                run models by model_id
                model_dict[model_id] = model
            class_name_dict: dict
                send class names to client after label shift
                class_name_dict = {0: 'people', ...}
            label_shift: dict
                merge all labels
                label_shift[model_id] = shift
            task_list: list
                list of task names
                task_list = [task1, task2, ...]
            mix_name_classes: dict
                mix_name_classes = {class_name: class_id, ...}
            frames_results_queue
                frames_results_queue = queue.Queue()
            queue_lock: threading.Lock
                lock for frames_results_queue
        '''
        self.logger = logging.getLogger(namespace) if namespace else logging.getLogger()

        self.app = Flask(__name__)
        self.setup_routes()

        self.max_detection_num     = max_detection_num
        self.interval              = interval

        self.all_cameras_ids       = all_cameras_ids
        self.cameras_num           = len(all_cameras_ids) # camera數量

        # streaming
        self.stream = MultiStreaming(config='./configs/streaming.yaml', 
                                    reconnect_interval=30,
                                    verbose=True
                                    )
        self.stream.run()

        # model yaml
        self.mix_class_names  = {}
        self.model_dict       = {}
        self.label_shift      = {}
        shift                 = 0
        
        model_id = 0
        for cfg in model_list:
            model = YOLO(cfg)
            model.classes = []
            model.max_det = max_detection_num
            model.name_classes = {name: class_id for class_id, name in model._predictor.class_names.items()}
            self.model_dict[model_id] = model
            model_id += 1

        for cls_name in allowed_class_names:
            for _, model in reversed(self.model_dict.items()):
                class_id = model.name_classes.get(cls_name)
                if class_id is not None:
                    model.classes.append(class_id)

        shift = 0
        for model_id, model in self.model_dict.items():
            for class_id, cls_name in model._predictor.class_names.items():
                self.mix_class_names[int(class_id) + shift] = cls_name
            self.label_shift[model_id] = shift
            shift = len(self.mix_class_names)

        self.mix_name_classes     = {name: class_id for class_id, name in self.mix_class_names.items()}

        # ReID model
        self.reid_model = reid_model
        img = np.zeros((1920, 1080, 3), dtype=np.uint8)
        self.feature_dim = len(self.reid_model(img)[0]) if reid_model is not None else 0
        
        # task for debug
        self.task_list            = []

        # queue
        self.frames_results_queue = deque(maxlen=1)

        # lock
        self.queue_lock           = threading.Lock()

        # SHMHandler
        self.shm_handler          = SHMHandler(self.stream.w, self.stream.h, self.cameras_num, max_detection_num, feature_dim=self.feature_dim, namespace=namespace)

        # shared memory
        self.shm_handler.build_shared_memory()

        # init control block
        self.shm_handler.write_control_info(slot_idx=0)

        # stop event
        self.stop_event           = threading.Event()
        self.interval_stop_event  = threading.Event()

        threading.Thread(target=self.api_run, daemon=True).start()
    
    
    def setup_routes(self):
        @app.route('/api/registration_server', methods=['POST'])
        def registration_server():
            '''
            Registration server.
            Listen to the client and send the shared memory info.
            body:
                {
                "camera_ids"    : camera_ids,
                "class_names"   : class_names,
                }
            '''
            self.logger.info('Waiting for connection...')

            message       = request.get_json()
            cameras_ids   = message['camera_ids']
            class_names   = message['class_names']

            task_count = len(self.task_list)
            name = f"task_{task_count}"
            
            # find camera_ids in all_cameras_ids
            camera_indices_list = [
                self.all_cameras_ids.index(task_camera) 
                for task_camera in cameras_ids
                if task_camera in self.all_cameras_ids
            ]

            # find class_id in class_names
            class_name_dict = {
                self.mix_name_classes[name]: name
                for name in class_names
                if name in self.mix_name_classes
            }

            self.task_list.append(name)
            self.logger.info(f"Register task: {self.task_list}")

            respone = {
                'shm_name':                 "frames_results_shm",
                'total_cameras_num':        self.cameras_num,
                'camera_ids':               camera_indices_list,
                'width':                    self.stream.w,
                'height':                   self.stream.h,
                'class_name_dict':          class_name_dict,
                'max_detection_num':        self.max_detection_num,
                'feature_dim':              self.feature_dim,
            }

            return jsonify(respone), 200

        @app.route('/api/watchdog_server', methods=['POST'])
        def watchdog_server():
            '''
            Check if the cameras is running.
            body:
                {
                "device_id": "CAMERA-201-1"
                }
            '''
            data      = request.get_json()
            device_id = data['device_id']

            if device_id not in self.all_cameras_ids:
                return jsonify({'indicator': False,
                                'message': f'Device ID {device_id} not found in all cameras.'
                                }), 400
            
            camera_index  = self.all_cameras_ids.index(device_id)
            status_list   = self.stream.get_status()
            camera_status = status_list[camera_index]

            server_available    = []
            server_unavailable  = []
            if camera_status:
                server_available.append(device_id)
            else:
                server_unavailable.append(device_id)

            data = {
                'server_available': server_available,
                'server_unavailable': server_unavailable
                }

            return jsonify(data), 200
        
        @app.route('/api/feature', methods=['POST'])
        def feature():
            '''
            Image feature.
            body:
                {
                "images": "image_path" or form-data,
                }
            '''
            if self.reid_model is None:
                data = {}

                return data, 204

            imgs = []
            # form-data
            files = request.files.getlist('images')
            if files:
                imgs = files
            else:
                # single form-data
                single_file = request.files.get('images')
                if single_file:
                    imgs = [single_file]

            # JSON(PATH)
            if not imgs:
                json_data = request.get_json(silent=True)
                if json_data:
                    images = json_data.get('images')
                    if images:
                        imgs = images if isinstance(images, list) else [images]
                else:
                    return_data = {
                                    'indicator': False,
                                    'message': "Missing 'images' in request"
                                    }
                
                    return return_data, 400

            images = []
            for img in imgs:
                # path
                if isinstance(img, str):
                    if not os.path.exists(img):
                        return jsonify({
                            'indicator': False,
                            'message': f'Image path {img} does not exist'
                            }), 400
                    image = cv2.imread(img)

                # form-data
                elif isinstance(img, FileStorage):
                    img_np = np.frombuffer(img.read(), np.uint8)
                    try:
                        image = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
                    except:
                        return jsonify({
                            'indicator': False,
                            'message': f'Invalid image file {img.filename}'
                            }), 400

                images.append(image)

            # Run detection
            if not images:
                data = {
                    'indicator': False,
                    'message': "No valid images provided",
                    'features': [[]]
                }
                
                return jsonify(data), 400
                
            features = self.reid_model(images)
            features = [feature.detach().cpu().numpy() for feature in features]

            data = {
                'indicator': True,
                'features': orjson.dumps(features, option=orjson.OPT_SERIALIZE_NUMPY).decode('utf-8') if features else None
            }
            
            return jsonify(data), 200
        
        @app.route('/api/detection_health', methods=['POST'])
        def detection_health():
            return jsonify({'status': 'ok'}), 200
        
    def api_run(self):
        app.run(host='0.0.0.0', port=9453)
    
    def run(self):
        '''
        Run get_frames_results_queue threading.
        Get frames and results from stream, and put them into queue.
        '''
        self.stop_event.clear()
        num_frames = self.stream.num
        threading.Thread(target=self._write_frames_results_shm, daemon=True).start()
        next_time = time.perf_counter() + self.interval
        while not self.stop_event.is_set():
            merged_results = [np.empty((0, 6), dtype=float) for _ in range(num_frames)]
            features = [np.zeros((0, self.feature_dim)) for _ in range(num_frames)]
            frames = self.stream.get_frames()

            for model_id, model in self.model_dict.items():
                results = model(frames)
                        
                # Shift class_id and merge results
                for frame_idx, result in enumerate(results):
                    if result.shape[1] >= 6:
                        result[:, 5] += self.label_shift[model_id]
                    merged_results[frame_idx] = np.vstack((merged_results[frame_idx], result))

                    # only run reid model for the yolo model
                    if any(len(r) > 0 for r in results) and self.reid_model is not None:
                        im_crops = []

                        for det in merged_results[frame_idx]:
                            x1, y1, x2, y2 = map(int, det[:4])
                            im = frames[frame_idx][y1:y2, x1:x2]
                            im_crops.append(im)

                        if im_crops:
                            features_tensor = self.reid_model(im_crops)
                            features_np = features_tensor.detach().cpu().numpy()
                            features[frame_idx] = features_np
                        else:
                            features[frame_idx] = np.zeros((0, self.feature_dim))

            with self.queue_lock:
                self.frames_results_queue.append((frames, merged_results, features))

            # Calculate the next time to send the next frame
            next_time += self.interval
            delay = next_time - time.perf_counter()
            if delay > 0:
                self.interval_stop_event.wait(delay)
            else:
                time.sleep(0.001)
            
            time.sleep(0.01)
    
    def _write_frames_results_shm(self):
        '''
        If queue is not empty, get frames and results from queue, and put them into frames_buffer and results_buffer.

        1) Get frames and results from queue
        2) Write frames and results to shared memory
        3) Write control info to shared memory
        '''

        frame_counter = 0
        while not self.stop_event.is_set():
            if len(self.frames_results_queue) > 0:
                with self.queue_lock:
                    frames, results, reid = self.frames_results_queue.popleft()
                
                for cam_id in range(self.cameras_num):

                    # write frames and metas to shared memory
                    old_slot_idx = self.shm_handler.read_control_info()

                    # buffer index (0->1 or 1->0)
                    next_slot_idx = 1 - old_slot_idx

                    self.shm_handler.write_frame_and_bbox(cam_id, next_slot_idx, frames[cam_id], results[cam_id], reid[cam_id])

                # frame_counter limit, results
                if frame_counter <= self.stream.h*self.stream.w:
                    frame_counter += 1
                else:
                    frame_counter = 0

                meta_dict = {
                    "camera_id": cam_id,
                    "frame_counter": frame_counter,
                    "timestamp": time.time()
                }
                meta_str = json.dumps(meta_dict)
                
                self.shm_handler.write_control_info(next_slot_idx)
                self.shm_handler.write_meta_info(meta_str)

                    
            time.sleep(0.001)

    def stop(self):
        '''
        Stop the detection server.
        '''
        self.stop_event.set()
        self.logger.info('Detection server stopped.')


if __name__ == "__main__":
    from utilities import load_configs

    task_list, hyper_config, streaming_config, cameras_dict, cameras_configs_dict, all_cameras_ids = load_configs()

    max_detection_num = hyper_config['shared_memory']['max_detection_num']
    model_list        = hyper_config['model']['model_list']
    class_names  = [config['class'] for _, config in hyper_config.items() if 'class' in config]
    allowed_class_names = list(set(name for class_name in class_names for name in class_name))

    dection_server = DetectionServer(max_detection_num, model_list, allowed_class_names, all_cameras_ids)
    dection_server.run()