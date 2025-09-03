import cv2
import os
from PIL import Image
import matplotlib.pyplot as plt
import torch
import mmcv
import numpy as np
import time
import yaml
from mmcv import imread
import mmengine
from mmengine.registry import init_default_scope

from mmpose.apis import inference_topdown
from mmpose.apis import init_model as init_pose_estimator
from mmpose.evaluation.functional import nms
from mmpose.registry import VISUALIZERS
from mmpose.structures import merge_data_samples
from mmdet.apis import inference_detector, init_detector





class MMposeEstimator:
    """
    Class for performing pose estimation using a detector and pose estimator.

    Args:
        detector (object): The object representing the detector model.
        pose_estimator (object): The object representing the pose estimator model.
        draw_settings_path (str): The path to the draw settings file.
        conf_thresh (float, optional): Confidence threshold for object detection. Defaults to 0.5.
        iou_thresh (float, optional): IoU threshold for non-maximum suppression. Defaults to 0.3.
        device (str, optional): The device to run the models on. Defaults to None.

    Attributes:
        device (str): The device to run the models on.
        conf_thres (float): Confidence threshold for object detection.
        iou_thres (float): IoU threshold for non-maximum suppression.
        detector (object): The object representing the detector model.
        pose_estimator (object): The object representing the pose estimator model.
        draw_settings_path (str): The path to the draw settings file.
        bbox_color (tuple): The color of the bounding box.
        bbox_thickness (int): The thickness of the bounding box.
        kpt_color_map (dict): The color map for keypoints.
        skeleton_map (list): The map for drawing skeletons.

    Methods:
        run(imgs): Runs pose estimation on the given images.
        draw_skeleton_on_image(img, bbox_keypoints): Draws the skeleton on the image.
        draw_keypoints_on_image(img, bbox_keypoints, show_id): Draws the keypoints on the image.
        draw_pose_results_on_images(image, bboxes, keypoints): Draws the pose results on the images.
    """

    def __init__(self, detector, pose_estimator, draw_settings_path, conf_thresh=0.5, iou_thresh=0.3, device=None):
        self.device = device if device is not None else torch.device('cuda:0' if torch.cuda.is_available() else 'cpu') 
        self.conf_thres = conf_thresh
        self.iou_thres = iou_thresh
        self.detector = detector
        self.pose_estimator = pose_estimator
        self.draw_settings_path = draw_settings_path
        self._initialize_draw_settings()
    
    
    def _initialize_draw_settings(self):
        """
        Initializes the draw settings from the draw settings file.
        """
        with open(self.draw_settings_path, 'r') as f:
            draw_settings = yaml.safe_load(f)
        self.bbox_color = tuple(draw_settings['bbox_color'])
        self.bbox_thickness = draw_settings['bbox_thickness']
        self.kpt_color_map = draw_settings['kpt_color_map']
        self.skeleton_map = draw_settings['skeleton_map']
        self.kpt_labelstr = draw_settings['kpt_labelstr']

    def __call__(self, imgs):
        """
        Runs pose estimation on the given images.

        Args:
            imgs (list or object): The images to perform pose estimation on.

        Returns:
            tuple: A tuple containing the keypoints and bounding box results for each image.
        """
        init_default_scope(self.detector.cfg.get('default_scope', 'mmdet'))
        # check if imgs is a list of images
        if not isinstance(imgs, list):
            imgs = [imgs]

        pre_imgs = [self._preprocess(img) for img in imgs]
        detect_results = inference_detector(self.detector, pre_imgs)

        all_keypoints = []
        all_bbox_results = []
        start_time = time.time()
        for img, detect_result in zip(imgs, detect_results):
            bbox_results, keypoints_in_image = self._pose_estimation(img, detect_result)
            all_keypoints.append(keypoints_in_image)
            all_bbox_results.append(bbox_results)

        return all_keypoints, all_bbox_results
    
    def _preprocess(self, img):
        """
        Preprocesses the image.

        Args:
            img (object): The image to preprocess.

        Returns:
            object: The preprocessed image.
        """
        return img
    
    def _pose_estimation(self, img, detect_result):
        """
        Performs pose estimation on the image using the detected results.

        Args:
            img (object): The image to perform pose estimation on.
            detect_result (object): The detection results for the image.

        Returns:
            tuple: A tuple containing the bounding box results and keypoints in the image.
        """
        pred_instance = detect_result.pred_instances.cpu().numpy()
        bboxes = np.concatenate(
            (pred_instance.bboxes, pred_instance.scores[:, None]),
            axis=1
        )
        bboxes = bboxes[np.logical_and(pred_instance.labels == 0, pred_instance.scores > self.conf_thres)]
        bboxes = bboxes[nms(bboxes, self.iou_thres)][:, :4].astype('int')

        if len(bboxes) == 0:
            return [], []

        pose_results = inference_topdown(self.pose_estimator, img, bboxes)
        
        combined_keypoints_info = []
        for pose in pose_results:
            keypoints = pose.pred_instances.keypoints[0].astype('int').tolist()
            scores = pose.pred_instances.keypoint_scores[0].tolist()

            combined_info = [kp + [sc] for kp, sc in zip(keypoints, scores)]
            combined_keypoints_info.append(combined_info)

        return bboxes, combined_keypoints_info
    
    def draw_skeleton_on_image(self, img, bbox_keypoints, conf_thres=0.5):
        """
        Draws the skeleton on the image.

        Args:
            img (object): The image to draw the skeleton on.
            bbox_keypoints (list): The keypoints associated with the bounding box.

        Returns:
            object: The image with the skeleton drawn on it.
        """
        for skeleton in self.skeleton_map:
            srt_kpt_id = skeleton['srt_kpt_id']
            srt_kpt_x = bbox_keypoints[srt_kpt_id][0]
            srt_kpt_y = bbox_keypoints[srt_kpt_id][1]
            srt_kpt_conf = bbox_keypoints[srt_kpt_id][2]
            if srt_kpt_conf < conf_thres:
                continue

            if srt_kpt_x == 0 and srt_kpt_y == 0:
                continue

            dst_kpt_id = skeleton['dst_kpt_id']
            dst_kpt_x = bbox_keypoints[dst_kpt_id][0]
            dst_kpt_y = bbox_keypoints[dst_kpt_id][1]
            dst_kpt_conf = bbox_keypoints[dst_kpt_id][2]
            if dst_kpt_conf < conf_thres:
                continue

            if dst_kpt_x == 0 and dst_kpt_y == 0:
                continue

            skeleton_color = skeleton['color']
            skeleton_thickness = skeleton['thickness']

            img = cv2.line(
                img,
                (srt_kpt_x, srt_kpt_y),
                (dst_kpt_x, dst_kpt_y),
                color=skeleton_color,
                thickness=skeleton_thickness
            )

        return img
    
    def draw_keypoints_on_image(self, img, bbox_keypoints, show_id=False, conf_thres=0.5):
        """
        Draws the keypoints on the image.

        Args:
            img (object): The image to draw the keypoints on.
            bbox_keypoints (list): The keypoints associated with the bounding box.
            show_id (bool, optional): Whether to show the ID of the keypoints. Defaults to False.

        Returns:
            object: The image with the keypoints drawn on it.
        """
        for kpt_id in self.kpt_color_map:
            kpt_color_info = self.kpt_color_map[kpt_id]
            kpt_color = kpt_color_info['color']
            kpt_radius = kpt_color_info['radius']
            kpt_x = bbox_keypoints[kpt_id][0]
            kpt_y = bbox_keypoints[kpt_id][1]
            kpt_conf = bbox_keypoints[kpt_id][2]
            if kpt_conf < conf_thres:
                continue

            img = cv2.circle(
                img,
                (kpt_x, kpt_y),
                radius=kpt_radius,
                color=kpt_color,
                thickness=-1
            )

            if show_id:
                kpt_label = str(kpt_id)
                offset_x = self.kpt_labelstr.get('offset_x', 0)
                offset_y = self.kpt_labelstr.get('offset_y', 0)
                font_size = self.kpt_labelstr.get('font_size', 2)
                font_thickness = self.kpt_labelstr.get('font_thickness', 2)
                img = cv2.putText(
                    img,
                    kpt_label,
                    (kpt_x + offset_x, kpt_y + offset_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_size,
                    kpt_color,
                    font_thickness
                )

        return img
    
    def draw_pose_results_on_images(self, image, bboxes, keypoints, show_id=False, conf_thres=0.5): 
        """
        Draws the pose results on the images.

        Args:
            image (object): The image to draw the pose results on.
            bboxes (list): The bounding box results.
            keypoints (list): The keypoints for each bounding box.

        Returns:
            object: The image with the pose results drawn on it.
        """
        for bbox in bboxes:
            cv2.rectangle(
                image,
                (int(bbox[0]), int(bbox[1])),
                (int(bbox[2]), int(bbox[3])),
                color=self.bbox_color,
                thickness=self.bbox_thickness
            )
        for kpts in keypoints:
            image = self.draw_keypoints_on_image(image, kpts, show_id=show_id, conf_thres=conf_thres)
            image = self.draw_skeleton_on_image(image, kpts, conf_thres=conf_thres)
        
        return image