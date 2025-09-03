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
from .mmpose_estimator import MMposeEstimator

class MMposeEstimatorBuilder:
    def __init__(self, file):
        assert file.endswith(('.yaml', '.yml'))
        with open(file, 'r') as f:
            setting = yaml.safe_load(f)
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        key = list(setting.keys())[0]
        self.detector_config = setting[key]['detector']['config_path']
        self.detector_checkpoint = setting[key]['detector']['checkpoint_path']
        self.pose_config = setting[key]['pose']['config_path']
        self.pose_checkpoint = setting[key]['pose']['checkpoint_path']
        self.draw_setting_path = setting[key]['draw_setting_path']
        self.conf_thresh = setting[key]['conf_thresh']
        self.iou_thresh = setting[key]['iou_thresh']

        self.detector = init_detector(
            self.detector_config,
            self.detector_checkpoint,
            device=self.device
        )
        self.pose_estimator = init_pose_estimator(
            self.pose_config,
            self.pose_checkpoint,
            device=self.device,
            cfg_options={'model': {'test_cfg': {'output_heatmaps': False}}}
        )
        
    def __call__(self):
        self.mmpose_estimator = MMposeEstimator(self.detector, self.pose_estimator, self.draw_setting_path, self.conf_thresh, self.iou_thresh, self.device)
        return self.mmpose_estimator

    def draw_pose_results_on_images(self, images, bboxes, keypoints, show_id=False, conf_thres=0.25):
        return self.mmpose_estimator.draw_pose_results_on_images(images, bboxes, keypoints, show_id, conf_thres)