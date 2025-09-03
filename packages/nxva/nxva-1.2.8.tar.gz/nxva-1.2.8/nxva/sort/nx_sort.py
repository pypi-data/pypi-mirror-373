import numpy as np
import time
import torch
import logging

from .utils.KMmatcher import solve_km_assignment
from .nx_track import NXTracker
from .utils.association import iou_batch, giou_batch, ciou_batch, diou_batch, ct_dist
from .utils.tools import nn_cosine_distance, get_speed_direction

# 設置 logger
logger = logging.getLogger(__name__)

ASSO_FUNCS = {  
    "iou": iou_batch, # IoU計算方式選擇(in association.py)
    "giou": giou_batch,
    "ciou": ciou_batch,
    "diou": diou_batch,
    "ct_dist": ct_dist
}

class NXSort():
    def __init__(self, 
                 min_hits=3,  # 最小命中次數
                 iou_threshold=0.3,
                 max_age=10, # 最大容忍frame數，沒出現就del
                 pos_lambda=(0.5, 0.5),
                 iou_type='diou',
                 direction_type='vector',
                 dir_history_num=10,
                 use_byte=True,  # 是否使用byte分高分、中分框
                 det_threshold=0.5, # 高分框閾值, > det_threshold = 高分框, < det_threshold = 中分框
                 use_kalman_filter=True, # 是否使用Kalman filter
                 use_feature=True, # 是否使用特徵匹配
                 feature_lambda=0.3,
                 feature_threshold=0.8):
        """
        進階版本的NXSort，簡化的四階段匹配策略
        
        匹配策略：
        1. 高分框全匹配(IoU + 特徵，若有特徵)
        2. 剩餘高分框IoU匹配  
        3. 中分框IoU匹配
        4. 剩餘det與剩餘trk匹配（降低閾值）
        
        若沒有特徵，則直接執行 2,3,4 階段
        """
        self.min_hits = min_hits
        self.max_age = max_age
        self.pos_lambda = pos_lambda
        self.direction_type = direction_type
        self.dir_history_num = dir_history_num
        self.iou_func = ASSO_FUNCS.get(iou_type, diou_batch)
        self.use_byte = use_byte
        self.det_threshold = det_threshold
        self.iou_threshold = iou_threshold

        self.use_feature = use_feature
        if self.use_feature:
            self.feature_lambda = feature_lambda
            self.feature_threshold = feature_threshold
            # 有特徵時的綜合閾值
            self.cost_threshold = (1 - feature_lambda) * iou_threshold + feature_lambda * feature_threshold
        else:
            self.cost_threshold = iou_threshold
        
        self.use_kalman_filter = use_kalman_filter
        self.update_dict = {'new_ids': [], 'disappeared_ids': []}
        self.track_list = []

    def run(self, det_results, embeddings=None):
        """主要追蹤方法"""
        logger.debug(f"開始追蹤: {len(det_results)} 個檢測, {len(self.track_list)} 個現有軌跡")
        
        if self.use_feature and embeddings is None:
            raise ValueError("Embeddings must be provided when use_feature is True.")
        
        # 處理embeddings
        if embeddings is not None and isinstance(embeddings, torch.Tensor):
            embeddings = embeddings.cpu().detach().numpy()

        # 邊界情況處理
        if len(det_results) == 0:
            logger.debug("無檢測結果，處理空檢測")
            return self._handle_empty_detections()

        if len(self.track_list) == 0:
            logger.debug("無現有軌跡，創建新軌跡")
            return self._handle_no_existing_tracks(det_results, embeddings)

        # 主要追蹤流程
        return self._perform_advanced_tracking(det_results, embeddings)

    def _perform_advanced_tracking(self, det_results, embeddings):
        """執行簡化的追蹤邏輯"""
        track_results, speed_results, direction_results = self._init_result_containers(len(det_results))

        if embeddings is not None and det_results.shape[0] != embeddings.shape[0]:
            return track_results, speed_results, direction_results
        
        # 預測上ㄧ幀的框
        pre_bboxes = self._get_prev_bboxes()

        # 分離高分框和中分框
        high_dets_indices, mid_dets_indices, high_dets, mid_dets = self._separate_detections(det_results)

        # 追蹤匹配狀態
        matched_trk_indices = set()
        matched_det_indices = set()

        # === 第一階段：高分框全匹配 (IoU + 特徵，若有特徵) ===
        if len(high_dets) > 0 and self.use_feature:
            matched_dets, matched_trks = self._perform_matching(
                det_results, high_dets_indices, matched_det_indices, matched_trk_indices, pre_bboxes,
                track_results, speed_results, direction_results, embeddings=embeddings, threshold=self.cost_threshold
            )
            matched_det_indices.update(matched_dets)
            matched_trk_indices.update(matched_trks)
            logger.debug(f'1matched-det: {matched_det_indices}, matched-trk: {matched_trk_indices}')

        # === 第二階段：剩餘高分框IoU匹配 ===
        if len(high_dets) > 0:
            matched_dets, matched_trks = self._perform_matching(
                det_results, high_dets_indices, matched_det_indices, matched_trk_indices, pre_bboxes,
                track_results, speed_results, direction_results, embeddings=None, threshold=self.iou_threshold
            )
            matched_det_indices.update(matched_dets)
            matched_trk_indices.update(matched_trks)
            logger.debug(f'2matched-det: {matched_det_indices}, matched-trk: {matched_trk_indices}')

        # === 第三階段：中分框IoU匹配 ===
        if len(mid_dets) > 0:
            matched_dets, matched_trks = self._perform_matching(
                det_results, mid_dets_indices, matched_det_indices, matched_trk_indices, pre_bboxes,
                track_results, speed_results, direction_results, embeddings=None, threshold=self.iou_threshold
            )
            matched_det_indices.update(matched_dets)
            matched_trk_indices.update(matched_trks)
            logger.debug(f'3matched-det: {matched_det_indices}, matched-trk: {matched_trk_indices}')

        # === 第四階段：剩餘det與剩餘trk最終匹配（降低閾值） ===
        unmatched_det_indices = set(range(len(det_results))) - matched_det_indices
        if len(unmatched_det_indices) > 0 and self.use_byte:
            matched_dets, matched_trks = self._perform_matching(
                det_results, list(unmatched_det_indices), matched_det_indices, matched_trk_indices, pre_bboxes,
                track_results, speed_results, direction_results, embeddings=None, threshold=max(self.iou_threshold-0.1, 0.1)
            )
            matched_det_indices.update(matched_dets)
            matched_trk_indices.update(matched_trks)
            logger.debug(f'4matched-det: {matched_det_indices}, matched-trk: {matched_trk_indices}')

        # 清理和創建新追蹤
        self._cleanup_and_create_new_tracks(det_results, matched_trk_indices, matched_det_indices, embeddings)

        return track_results, speed_results, direction_results

    def _separate_detections(self, det_results):
        """分離高分框和中分框"""
        if self.use_byte:
            high_idx = det_results[:, 4] >= self.det_threshold
            mid_idx = det_results[:, 4] < self.det_threshold
            high_dets_indices = np.where(high_idx)[0]
            mid_dets_indices = np.where(mid_idx)[0]
            high_dets = det_results[high_idx]
            mid_dets = det_results[mid_idx]
        else:
            high_dets_indices = np.arange(len(det_results))
            mid_dets_indices = np.array([])
            high_dets = det_results
            mid_dets = np.array([])
        
        return high_dets_indices, mid_dets_indices, high_dets, mid_dets

    def _perform_matching(self, det_results, det_indices, matched_det_indices, matched_trk_indices, pre_bboxes,
                         track_results, speed_results, direction_results, embeddings=None, threshold=0.3):
        """統一的匹配函數"""
        # 過濾未匹配的detections和tracks
        unmatched_det_indices = set(det_indices) - matched_det_indices
        unmatched_trk_indices = set(range(len(self.track_list))) - matched_trk_indices
        
        if len(unmatched_det_indices) == 0 or len(unmatched_trk_indices) == 0:
            return set(), set()

        unmatched_det_list = sorted(list(unmatched_det_indices))
        unmatched_trk_list = sorted(list(unmatched_trk_indices))
        logger.debug(f"未匹配的detections: {unmatched_det_list}, 未匹配的tracks: {unmatched_trk_list}")
        
        # 獲取對應的bboxes
        unmatched_pre_bboxes = pre_bboxes[unmatched_trk_list]
        unmatched_det_bboxes = det_results[unmatched_det_list, :4]
        
        # 計算cost matrix
        iou_matrix = self.iou_func(unmatched_pre_bboxes, unmatched_det_bboxes)
        if self.use_feature and embeddings is not None:
            # 使用IoU + 特徵
            unmatched_embeddings = embeddings[unmatched_det_list]
            iou_gate = iou_matrix < self.iou_threshold
            iou_matrix[iou_gate] = 0
            feature_matrix = self._compute_feature_matrix_stage(unmatched_embeddings, unmatched_trk_list)
            feature_gate = feature_matrix < self.feature_threshold
            feature_matrix[feature_gate] = 0

            trk_det_cost_matrix = (1 - self.feature_lambda) * iou_matrix + self.feature_lambda * feature_matrix
        else:
            # 只使用IoU
            trk_det_cost_matrix = iou_matrix

        # 應用閾值
        trk_det_cost_matrix[trk_det_cost_matrix < threshold] = -100
        logger.debug(f"計算的cost matrix形狀: {trk_det_cost_matrix}, cost_threshold: {threshold}")
        
        # 求解匹配
        track_det_match_lst = solve_km_assignment(trk_det_cost_matrix, threshold)
        logger.debug(f"KM匹配結果: {track_det_match_lst}")
        
        # 更新匹配結果
        return self._update_matched_tracks_stage(
            det_results, track_det_match_lst, unmatched_det_list, unmatched_trk_list,
            track_results, speed_results, direction_results, embeddings
        )

    def _compute_cost_matrix_stage(self, pre_bboxes, det_bboxes, embeddings, track_indices):
        """計算綜合cost matrix (IoU + 特徵)"""
        iou_matrix = self.iou_func(pre_bboxes, det_bboxes)

        if self.use_feature and embeddings is not None and len(track_indices) > 0:
            feature_matrix = self._compute_feature_matrix_stage(embeddings, track_indices)
            cost_matrix = (1 - self.feature_lambda) * iou_matrix + self.feature_lambda * feature_matrix
        else:
            cost_matrix = iou_matrix

        return cost_matrix

    def _compute_feature_matrix_stage(self, dets_feature, track_indices):
        """計算特徵距離矩陣"""
        if dets_feature.ndim == 1:
            dets_feature = dets_feature.reshape(1, -1)
        elif dets_feature.ndim != 2:
            raise ValueError(f"Features should be 1D or 2D array, got {dets_feature.ndim}D")
        
        cost_matrix = np.zeros((len(track_indices), len(dets_feature)))
        for i, track_idx in enumerate(track_indices):
            trk_obj = self.track_list[track_idx]
            cost_matrix[i, :] = nn_cosine_distance(trk_obj.features, dets_feature)

        return cost_matrix

    def _update_matched_tracks_stage(self, det_results, track_det_match_lst, unmatched_det_indices, unmatched_track_indices,
                                     track_results, speed_results, direction_results, embeddings):
        """統一的階段匹配結果處理"""
        matched_det_indices = set()
        matched_track_indices = set()

        for i, track_idx in enumerate(unmatched_track_indices):
            det_match_idx = track_det_match_lst[i]
            if det_match_idx != -1:
                original_det_idx = unmatched_det_indices[det_match_idx]
                
                matched_det_indices.add(original_det_idx)
                matched_track_indices.add(track_idx)

                # 更新追蹤對象
                trk_obj = self.track_list[track_idx]
                det_bbox = det_results[original_det_idx, :4]
                trk_obj.update(det_bbox)

                if self.use_feature and embeddings is not None:
                    feature = embeddings[original_det_idx]
                    trk_obj.push_feature(feature)

                # 如果追蹤對象已確認，計算速度和方向
                if trk_obj.is_confirmed():
                    speed, direction = get_speed_direction(
                        pre_time=trk_obj.last_update_time,
                        cur_time=time.time(),
                        pre_box=trk_obj.history_bbox[-1],
                        pre_n_box=trk_obj.history_bbox[0],
                        cur_box=det_bbox,
                        pos_lambda=self.pos_lambda,
                        direction_type=self.direction_type
                    )

                    track_results[original_det_idx] = trk_obj.uid
                    speed_results[original_det_idx] = speed
                    direction_results[original_det_idx] = direction

        return matched_det_indices, matched_track_indices

    def _cleanup_and_create_new_tracks(self, det_results, matched_trk_indices, matched_det_indices, embeddings):
        """清理未匹配tracks並創建新tracks"""
        # 清理未匹配的追蹤對象
        unmatched_trks = set(range(len(self.track_list))) - matched_trk_indices
        self._filter_track_list(list(unmatched_trks))

        # 為未匹配的檢測創建新追蹤對象
        unmatched_dets = set(range(len(det_results))) - matched_det_indices
        unmatched_dets_bboxes = det_results[list(unmatched_dets), :4]
        unmatched_dets_embeddings = embeddings[list(unmatched_dets)] if embeddings is not None else None

        self._create_new_tracks(unmatched_dets_bboxes, unmatched_dets_embeddings)

    # === 以下是輔助方法，與原始版本相同 ===

    def _init_result_containers(self, dets_len=0):
        """重置更新列表並準備結果容器"""
        self.update_dict = {'new_ids': [], 'disappeared_ids': []}
        
        track_results = np.ones(dets_len) * (-1)
        speed_results = np.zeros(dets_len)
        direction_results = np.zeros((dets_len, 2)) if self.direction_type == 'vector' else np.zeros(dets_len)
        
        return track_results, speed_results, direction_results

    def _handle_empty_detections(self):
        """處理空檢測的情況"""
        for track in self.track_list:
            track.predict()
            track.update(None)
        self._filter_track_list()
        return self._init_result_containers()

    def _handle_no_existing_tracks(self, det_results, embeddings):
        """處理沒有現有追蹤對象的情況"""
        det_bboxes = det_results[:, :4]
        self._create_new_tracks(det_bboxes, embeddings)
        return self._init_result_containers(len(det_results))

    def _get_prev_bboxes(self):
        """獲取上一幀的預測框"""
        pre_bboxes = np.zeros((len(self.track_list), 4))
        for i, trk_obj in enumerate(self.track_list):
            pred_i_pos = trk_obj.predict()
            pre_bboxes[i, :] = pred_i_pos[:4]
        return pre_bboxes

    def _create_new_tracks(self, det_bboxes, embeddings=None):
        """創建新追蹤對象"""
        for i, det_bbox in enumerate(det_bboxes):
            trk_obj = NXTracker(bbox=det_bbox,
                                max_age=self.max_age,
                                min_hits=self.min_hits,
                                use_kalman_filter=self.use_kalman_filter,
                                dir_history_num=self.dir_history_num)
            trk_id = trk_obj.uid
            self.track_list.append(trk_obj)
            self.update_dict['new_ids'].append(trk_id)
            
            if self.use_feature and len(embeddings) > 0:
                feature = embeddings[i]
                trk_obj.push_feature(feature)

    def _filter_track_list(self, unmatched_tracks=None):
        """過濾並刪除過期的追蹤對象"""
        unmatched_tracks = sorted(unmatched_tracks) if unmatched_tracks is not None else None
        if unmatched_tracks is None:
            unmatched_idxs = list(range(len(self.track_list)))
        else:
            unmatched_idxs = unmatched_tracks if isinstance(unmatched_tracks, (list, tuple)) else list(unmatched_tracks)
        
        to_del_lst = []
        for idx in unmatched_idxs:
            track_obj = self.track_list[idx]
            track_obj.mark_missed()
            if track_obj.is_deleted():
                to_del_lst.append(idx)
                self.update_dict['disappeared_ids'].append(track_obj.uid)
        logger.debug(f'unmatched_idxs: {unmatched_idxs}, to_del_lst: {to_del_lst}')
        for i in reversed(to_del_lst):
            self.track_list.pop(i)

    def get_update_results(self):
        """獲取更新結果"""
        if len(self.update_dict['new_ids']) == 0 and len(self.update_dict['disappeared_ids']) == 0:
            return None
        else:
            return self.update_dict
