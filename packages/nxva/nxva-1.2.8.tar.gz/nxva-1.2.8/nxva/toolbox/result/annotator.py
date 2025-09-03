import cv2, torch
import numpy as np

from nxva.yolo.utils import ops

# Color palette for visualization - hex color codes for different classes
hexs = (
    "042AFF",
    "0BDBEB",
    "F3F3F3",
    "00DFB7",
    "111F68",
    "FF6FDD",
    "FF444F",
    "CCED00",
    "00F344",
    "BD00FF",
    "00B4FF",
    "DD00BA",
    "00FFFF",
    "26C000",
    "01FFB3",
    "7D24FF",
    "7B0068",
    "FF1B6C",
    "FC6D2F",
    "A2FF0B",
)

class Annotator:
    """
    An annotation utility class for visualizing YOLO model predictions.
    
    This class provides methods to draw bounding boxes, keypoints, and segmentation
    masks on images based on YOLO model outputs. It supports multiple tasks including
    object detection, pose estimation, and instance segmentation.
    """
    def __init__(self):
        """
        Initialize the Annotator class.
        
        The annotator is ready to use without any additional setup.
        """
        pass

    def plot_detect(self, imgs, result, class_names, filter=None, save_path=None, output_dir=None):
        """
        Draw bounding boxes and labels for object detection results.
        
        This method visualizes detection results by drawing bounding boxes around
        detected objects with confidence scores and class labels.
        
        Args:
            imgs: Input images, can be:
                - Single image path (str)
                - List of image paths (list of str)
                - Single image array (np.array)
                - List of image arrays (list of np.array)
            result: Detection results from YOLO model
            cfg: Configuration object containing class_names and other settings
            filter: List of class IDs to filter, None to show all classes
            save_path: Path to save annotated images, None to not save
            output_dir: Output directory path, None to use current directory
            
        Returns:
            List of annotated images or single image if only one input
        """
        # Define color palette for different classes (BGR format)
        colors = [
            (255, 0, 0),     # Blue
            (0, 255, 0),     # Green
            (0, 0, 255),     # Red
            (255, 255, 0),   # Cyan
            (255, 0, 255),   # Magenta
            (0, 255, 255),   # Yellow
            (128, 0, 128),   # Purple
            (255, 165, 0),   # Orange
            (0, 128, 128),   # Teal
            (128, 128, 0),   # Olive
        ]
        
        # Get class names from configuration
        class_names = class_names if isinstance(class_names, dict) else {}
        
        # Ensure result is a list for consistent processing
        if not isinstance(result, list):
            result = [result]
        
        # Validate that image count matches result count
        if len(imgs) != len(result):
            if len(result) == 1:
                # If only one result, apply to all images
                result = result * len(imgs)
            else:
                raise ValueError(f"Image count ({len(imgs)}) doesn't match result count ({len(result)})")
        
        result_imgs = []
        
        # Process each image and its corresponding detection results
        for img_idx, (current_img, det) in enumerate(zip(imgs, result)):
            # Copy image to avoid modifying original
            result_img = current_img.copy()
            
            # Process detection results
            # det should be in format [boxes, confs, class_ids]
            if isinstance(det, np.ndarray):
                # Unpack detection results
                boxes, confs, class_ids = det[:, :4], det[:, 4:5], det[:, 5:6]
                
                # Draw bounding box for each detection
                for i in range(len(boxes)):
                    x1, y1, x2, y2 = boxes[i]
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    
                    confidence = confs[i]
                    class_id = int(class_ids[i])
                    
                    # Ensure confidence is a scalar value
                    if hasattr(confidence, 'item'):
                        confidence = confidence.item()
                    
                    # Apply class filter if specified
                    if filter is not None and class_id not in filter:
                        continue
                    
                    # Get class name for label
                    class_name = class_names.get(class_id, f'Class_{class_id}')
                    
                    # Select color for this class
                    color = colors[class_id % len(colors)]
                    
                    # Draw bounding box rectangle
                    cv2.rectangle(result_img, (x1, y1), (x2, y2), color, 2)
                    
                    # Prepare label text with class name and confidence
                    label = f'{class_name}: {confidence:.2f}'
                    
                    # Calculate text dimensions for proper positioning
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.3
                    font_thickness = 1
                    (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
                    
                    # Calculate label position
                    label_x = x1
                    label_y = y1 - 10
                    
                    # Ensure label doesn't go outside image boundaries
                    if label_y < text_height + 10:
                        label_y = y1 + text_height + 10
                    
                    # Draw label background rectangle
                    cv2.rectangle(result_img, 
                                (label_x, label_y - text_height - 5),
                                (label_x + text_width + 5, label_y + 5),
                                color, -1)
                    
                    # Draw label text in white
                    cv2.putText(result_img, label, 
                              (label_x + 2, label_y - 2), 
                              font, font_scale, (255, 255, 255), font_thickness)
            
            result_imgs.append(result_img)
        
        # Save images if save_path is provided, otherwise return images
        if save_path:
            # Handle output directory
            if output_dir:
                import os
                os.makedirs(output_dir, exist_ok=True)
                full_save_path = os.path.join(output_dir, save_path)
            else:
                full_save_path = save_path
            
            self._save_images(result_imgs, full_save_path)
        
        return result_imgs if len(result_imgs) > 1 else result_imgs[0]

    def plot_pose(self, imgs, result, filter=None, save_path=None, output_dir=None):
        """
        Draw pose estimation results with keypoints and skeleton connections.
        
        This method visualizes pose estimation results by drawing keypoints and
        connecting them with lines to show the human skeleton structure.
        
        Args:
            imgs: Input images (same format as plot_detect)
            result: Pose estimation results in format [bbox, kpt]
            cfg: Configuration object containing class_names and other settings
            filter: List of class IDs to filter, None to show all classes
            save_path: Path to save annotated images, None to not save
            output_dir: Output directory path, None to use current directory
            
        Returns:
            List of annotated images or single image if only one input
        """
        
        # Define body part connections and colors for COCO 17-keypoint format
        # COCO 17 keypoints: 0nose, 1-2eyes, 3-4ears, 5-6shoulders, 7-8elbows, 9-10wrists, 11-12hips, 13-14knees, 15-16ankles
        head_connections = [
            [0, 1], [0, 2],   # Nose-left eye, nose-right eye
            [1, 3], [2, 4],   # Left eye-left ear, right eye-right ear
        ]
        
        arm_shoulder_connections = [
            [5, 7], [7, 9],   # Left shoulder-left elbow-left wrist
            [6, 8], [8, 10],  # Right shoulder-right elbow-right wrist
            [5, 6]            # Left shoulder-right shoulder
        ]
        
        torso_connections = [
            [5, 11], [6, 12],  # Shoulders to hips
            [11, 12]           # Left hip-right hip
        ]
        
        leg_connections = [
            [11, 13], [13, 15],  # Left hip-left knee-left ankle
            [12, 14], [14, 16]   # Right hip-right knee-right ankle
        ]
        
        # Define keypoint colors based on body parts (BGR format)
        kpt_color = [
            (0, 255, 0),     # 0: Nose - Green
            (0, 255, 0),     # 1: Left eye - Green
            (0, 255, 0),     # 2: Right eye - Green
            (0, 255, 0),     # 3: Left ear - Green
            (0, 255, 0),     # 4: Right ear - Green
            (255, 0, 0),     # 5: Left shoulder - Blue
            (255, 0, 0),     # 6: Right shoulder - Blue
            (255, 0, 0),     # 7: Left elbow - Blue
            (255, 0, 0),     # 8: Right elbow - Blue
            (255, 0, 0),     # 9: Left wrist - Blue
            (255, 0, 0),     # 10: Right wrist - Blue
            (0, 255, 255),   # 11: Left hip - Yellow
            (0, 255, 255),   # 12: Right hip - Yellow
            (255, 0, 255),   # 13: Left knee - Purple
            (255, 0, 255),   # 14: Right knee - Purple
            (255, 0, 255),   # 15: Left ankle - Purple
            (255, 0, 255),   # 16: Right ankle - Purple
        ]
        
        # Get class names from configuration
        class_names = {0: 'person'}
        
        # Ensure result is a list for consistent processing
        if not isinstance(result, list):
            result = [result]
        
        # Validate that image count matches result count
        if len(imgs) != len(result):
            if len(result) == 1:
                # If only one result, apply to all images
                result = result * len(imgs)
            else:
                raise ValueError(f"Image count ({len(imgs)}) doesn't match result count ({len(result)})")
        
        result_imgs = []
        
        # Process each image and its corresponding pose results
        for img_idx, (current_img, det) in enumerate(zip(imgs, result)):
            # Copy image to avoid modifying original
            result_img = current_img.copy()
            
            # Process pose estimation results
            if isinstance(det, dict):
                # Result format: [bbox, kpt]
                bbox_results, kpt_results = det['boxes'], det['keypoints']
                
                # Convert to numpy format if needed
                if hasattr(bbox_results, 'cpu'):
                    bbox_results = bbox_results.cpu().numpy()
                if hasattr(kpt_results, 'cpu'):
                    kpt_results = kpt_results.cpu().numpy()
                
                # Process bounding box results
                if bbox_results is not None and len(bbox_results) > 0:
                    # bbox format: [N, 4] or [N, 5] or [N, 6]
                    for i in range(len(bbox_results)):
                        if len(bbox_results[i]) >= 4:
                            x1, y1, x2, y2 = bbox_results[i][:4]
                            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                            
                            # Extract confidence and class_id if available
                            confidence = bbox_results[i][4] if len(bbox_results[i]) > 4 else 1.0
                            class_id = int(bbox_results[i][5]) if len(bbox_results[i]) > 5 else 0
                            
                            # Ensure confidence is a scalar value
                            if hasattr(confidence, 'item'):
                                confidence = confidence.item()
                            
                            # Apply class filter if specified
                            if filter is not None and class_id not in filter:
                                continue
                            
                            # Get class name for label
                            class_name = class_names.get(class_id, f'Class_{class_id}')
                            
                            # Draw bounding box
                            cv2.rectangle(result_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            
                            # Draw label
                            label = f'{class_name}: {confidence:.2f}'
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            font_scale = 0.3
                            font_thickness = 1
                            (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
                            
                            label_x = x1
                            label_y = y1 - 10
                            
                            if label_y < text_height + 10:
                                label_y = y1 + text_height + 10
                            
                            cv2.rectangle(result_img, 
                                        (label_x, label_y - text_height - 5),
                                        (label_x + text_width + 5, label_y + 5),
                                        (0, 255, 0), -1)
                            
                            cv2.putText(result_img, label, 
                                      (label_x + 2, label_y - 2), 
                                      font, font_scale, (255, 255, 255), font_thickness)
                
                # Process keypoint results
                if kpt_results is not None and len(kpt_results) > 0:
                    # kpt format: [N, 17, 3] (N persons, 17 keypoints, each with x,y,visibility)
                    for person_idx in range(len(kpt_results)):
                        person_kpts = kpt_results[person_idx]  # [17, 3]
                        if np.all(person_kpts == 0):
                            continue
                        
                        # Draw keypoints - following the image effect
                        for kpt_idx in range(len(person_kpts)):
                            if kpt_idx < len(kpt_color):
                                x, y, vis = person_kpts[kpt_idx]
                                if vis > 0.5:  # Only draw visible keypoints
                                    x, y = int(x), int(y)
                                    if 0 <= x < result_img.shape[1] and 0 <= y < result_img.shape[0]:
                                        color = kpt_color[kpt_idx]
                                        # Draw keypoint circle
                                        cv2.circle(result_img, (x, y), 3, color, -1)
                        
                        # Draw skeleton connections
                        # Head connections - Green
                        for start_idx, end_idx in head_connections:
                            if (start_idx < len(person_kpts) and end_idx < len(person_kpts)):
                                start_kpt = person_kpts[start_idx]
                                end_kpt = person_kpts[end_idx]
                                
                                if start_kpt[2] > 0.5 and end_kpt[2] > 0.5:  # Both points visible
                                    start_point = (int(start_kpt[0]), int(start_kpt[1]))
                                    end_point = (int(end_kpt[0]), int(end_kpt[1]))
                                    
                                    # Check if points are within image boundaries
                                    if (0 <= start_point[0] < result_img.shape[1] and 
                                        0 <= start_point[1] < result_img.shape[0] and
                                        0 <= end_point[0] < result_img.shape[1] and 
                                        0 <= end_point[1] < result_img.shape[0]):
                                        
                                        cv2.line(result_img, start_point, end_point, (0, 255, 0), 2)  # Green
                        
                        # Arm and shoulder connections - Blue
                        for start_idx, end_idx in arm_shoulder_connections:
                            if (start_idx < len(person_kpts) and end_idx < len(person_kpts)):
                                start_kpt = person_kpts[start_idx]
                                end_kpt = person_kpts[end_idx]
                                
                                if start_kpt[2] > 0.5 and end_kpt[2] > 0.5:  # Both points visible
                                    start_point = (int(start_kpt[0]), int(start_kpt[1]))
                                    end_point = (int(end_kpt[0]), int(end_kpt[1]))
                                    
                                    # Check if points are within image boundaries
                                    if (0 <= start_point[0] < result_img.shape[1] and 
                                        0 <= start_point[1] < result_img.shape[0] and
                                        0 <= end_point[0] < result_img.shape[1] and 
                                        0 <= end_point[1] < result_img.shape[0]):
                                        
                                        cv2.line(result_img, start_point, end_point, (255, 0, 0), 2)  # Blue
                        
                        # Torso connections - Yellow
                        for start_idx, end_idx in torso_connections:
                            if (start_idx < len(person_kpts) and end_idx < len(person_kpts)):
                                start_kpt = person_kpts[start_idx]
                                end_kpt = person_kpts[end_idx]
                                
                                if start_kpt[2] > 0.5 and end_kpt[2] > 0.5:  # Both points visible
                                    start_point = (int(start_kpt[0]), int(start_kpt[1]))
                                    end_point = (int(end_kpt[0]), int(end_kpt[1]))
                                    
                                    # Check if points are within image boundaries
                                    if (0 <= start_point[0] < result_img.shape[1] and 
                                        0 <= start_point[1] < result_img.shape[0] and
                                        0 <= end_point[0] < result_img.shape[1] and 
                                        0 <= end_point[1] < result_img.shape[0]):
                                        
                                        cv2.line(result_img, start_point, end_point, (0, 255, 255), 2)  # Yellow
                        
                        # Leg connections - Purple
                        for start_idx, end_idx in leg_connections:
                            if (start_idx < len(person_kpts) and end_idx < len(person_kpts)):
                                start_kpt = person_kpts[start_idx]
                                end_kpt = person_kpts[end_idx]
                                
                                if start_kpt[2] > 0.5 and end_kpt[2] > 0.5:  # Both points visible
                                    start_point = (int(start_kpt[0]), int(start_kpt[1]))
                                    end_point = (int(end_kpt[0]), int(end_kpt[1]))
                                    
                                    # Check if points are within image boundaries
                                    if (0 <= start_point[0] < result_img.shape[1] and 
                                        0 <= start_point[1] < result_img.shape[0] and
                                        0 <= end_point[0] < result_img.shape[1] and 
                                        0 <= end_point[1] < result_img.shape[0]):
                                        
                                        cv2.line(result_img, start_point, end_point, (255, 0, 255), 2)  # Purple
            
            result_imgs.append(result_img)
        
        # Save images if save_path is provided, otherwise return images
        if save_path:
            # Handle output directory
            if output_dir:
                import os
                os.makedirs(output_dir, exist_ok=True)
                full_save_path = os.path.join(output_dir, save_path)
            else:
                full_save_path = save_path
            
            self._save_images(result_imgs, full_save_path)
        
        return result_imgs if len(result_imgs) > 1 else result_imgs[0]

    def plot_segment(self, source_img, results, filter=None, save_path=None, output_dir=None):
        """
        Draw segmentation masks and save annotated images.
        
        This method visualizes instance segmentation results by overlaying
        colored masks on the original images with transparency.
        
        Args:
            source_img: List of original images
            results: List of detection results with masks
            cfg: Configuration object containing settings
            filter: Filter options for classes
            save_path: Path to save annotated images
            output_dir: Output directory for saving images
        """
        import os
        import cv2
        from pathlib import Path
        
        def hex2rgb(h):
            """Convert hex color codes to RGB values (PIL order)."""
            return tuple(int(h[1 + i : 1 + i + 2], 16) for i in (0, 2, 4))
        
        # Create color palette from hex codes
        palette = [hex2rgb(f"#{c}") for c in hexs]
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Collect all processed images
        processed_images = []
        
        # Process each image and its segmentation results
        for i, (img, result) in enumerate(zip(source_img, results)):
            boxes, masks = result['boxes'], result['mask']
            if len(boxes) == 0:
                # If no objects detected, add original image
                processed_images.append(img)
                continue
            else:
                # Apply letterbox transformation to match mask dimensions
                img = ops.letterbox(img, masks.shape[1:])
                
                # Prepare image for GPU processing
                im_gpu = (
                    torch.as_tensor(img, dtype=torch.float16, device=masks.device)
                    .permute(2, 0, 1)
                    .flip(0)
                    .contiguous()
                    / 255
                )
                
                # Get class indices for color assignment
                idx = [int(id) for id in boxes[:, -1]]
                
                # Apply masks to image
                self.masks(img, masks, colors=[palette[x] for x in idx], im_gpu=im_gpu)
                
                # Add processed image to list
                processed_images.append(img)
        
        # Save all images if save path or output directory is specified
        if (save_path or output_dir) and processed_images:
            # Determine final save path
            if output_dir:
                # Use output_dir as directory, generate filename
                final_save_path = os.path.join(output_dir, save_path if save_path else "segment_result.jpg")
            else:
                # Use save_path directly
                final_save_path = save_path
            
            # Use existing _save_images method to save
            self._save_images(processed_images, final_save_path)
        return processed_images if len(processed_images) > 1 else processed_images[0]

    def masks(self, im, masks, colors, im_gpu, alpha=0.5, retina_masks=False):
        """
        Plot masks on image with transparency overlay.
        
        This method overlays segmentation masks on the original image with
        specified transparency and colors for each instance.
        
        Args:
            masks (tensor): Predicted masks on GPU, shape: [n, h, w]
            colors (List[List[Int]]): Colors for predicted masks, [[r, g, b] * n]
            im_gpu (tensor): Image on GPU, shape: [3, h, w], range: [0, 1]
            alpha (float): Mask transparency: 0.0 fully transparent, 1.0 opaque
            retina_masks (bool): Whether to use high resolution masks. Defaults to False.
        """
        # Handle empty masks case
        if len(masks) == 0:
            im[:] = im_gpu.permute(1, 2, 0).contiguous().cpu().numpy() * 255
            
        # Ensure masks and image are on same device
        if im_gpu.device != masks.device:
            im_gpu = im_gpu.to(masks.device)
            
        # Normalize colors to [0, 1] range and prepare for broadcasting
        colors = torch.tensor(colors, device=masks.device, dtype=torch.float32) / 255.0  # shape(n,3)
        colors = colors[:, None, None]  # shape(n,1,1,3)
        
        # Prepare masks for color multiplication
        masks = masks.unsqueeze(3)  # shape(n,h,w,1)
        masks_color = masks * (colors * alpha)  # shape(n,h,w,3)

        # Calculate cumulative inverse alpha for proper blending
        inv_alpha_masks = (1 - masks * alpha).cumprod(0)  # shape(n,h,w,1)
        mcs = masks_color.max(dim=0).values  # shape(n,h,w,3)

        # Prepare image for blending
        im_gpu = im_gpu.flip(dims=[0])  # flip channel
        im_gpu = im_gpu.permute(1, 2, 0).contiguous()  # shape(h,w,3)
        
        # Blend masks with original image
        im_gpu = im_gpu * inv_alpha_masks[-1] + mcs
        im_mask = im_gpu * 255
        im_mask_np = im_mask.byte().cpu().numpy()
        
        # Apply final result to image
        im[:] = im_mask_np if retina_masks else ops.scale_image(im_mask_np, im.shape)
        
        return im
        

    def _save_images(self, result_imgs, save_path):
        """
        Generic method to save images to disk.
        
        This method handles saving single or multiple images with proper
        file naming and directory creation.
        
        Args:
            result_imgs: List of images to save or single image
            save_path: Path where to save the images
        """
        # Convert to list format for consistent processing
        if not isinstance(result_imgs, list):
            result_imgs = [result_imgs]
        
        # Process all images using for loop
        for i, result_img in enumerate(result_imgs):
            if len(result_imgs) == 1:
                # Single image, use original path
                cv2.imwrite(save_path, result_img)
                print(f"Image saved to: {save_path}")
            else:
                # Multiple images, generate indexed filenames
                if '.' in save_path:
                    # Case with file extension
                    name, ext = save_path.rsplit('.', 1)
                    save_file = f"{name}_{i}.{ext}"
                else:
                    # Case without file extension, default to .jpg
                    save_file = f"{save_path}_{i}.jpg"
                
                cv2.imwrite(save_file, result_img)
                print(f"Image saved to: {save_file}")

