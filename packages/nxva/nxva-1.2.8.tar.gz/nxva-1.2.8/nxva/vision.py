import cv2
import copy
import math
import numpy as np

color_list = [
    [0, 0, 255],     
    [0, 255, 0],     
    [255, 0, 0],     
    [0, 255, 255],   
    [255, 255, 0],   
    [255, 0, 255],   
    [0, 165, 255],   
    [203, 192, 255], 
    [139, 0, 0],     
    [255, 228, 225], 
    [0, 0, 139],     
    [144, 238, 144], 
    [0, 128, 128],   
    [128, 0, 128],   
    [130, 0, 75],    
    [19, 69, 139],   
    [220, 220, 220], 
    [0, 215, 255],   
    [192, 192, 192], 
    [128, 128, 128], 
    [211, 211, 211], 
    [169, 169, 169], 
    [255, 191, 0],   
    [0, 255, 224],   
    [147, 112, 219], 
    [0, 100, 0],     
    [127, 255, 170], 
    [255, 105, 180],
    [0, 0, 0],       
    [255, 255, 255],  
]

def frame_cut(frame, bbox):
    """
    params:
        frame: np.ndarray
        bbox: list or 1-d array, [x1, y1, x2, y2]
    return:
        np.ndarray
    """
    cut_bbox = copy.deepcopy(bbox)
    if bbox[0] > bbox[2]:
        cut_bbox[0] = bbox[2]
        cut_bbox[2] = bbox[0]
    if bbox[1] > bbox[3]:
        cut_bbox[1] = bbox[3]
        cut_bbox[3] = bbox[1]
    return frame[int(cut_bbox[1]):int(cut_bbox[3]), int(cut_bbox[0]):int(cut_bbox[2])]


def draw_text(img, 
              text,
              font=cv2.FONT_HERSHEY_SIMPLEX,
              font_scale=0.5,
              font_thickness=1,
              text_color=(0, 0, 255),
              text_color_bg=(255, 255, 255),
              pos='tl',
              axis=(0, 0)):
    """
    This function is used to draw text on the image.
    The axis is the top-left corner of the text if the pos is 'tl'.
    params:
        img: np.ndarray
        text: str
        font: int
        font_scale: float
        font_thickness: int
        text_color: tuple
        text_color_bg: tuple
        pos: str, 'tl', 'tr', 'bl', 'br'
        axis: tuple, (x, y)
    return:
        tuple, (text_w, text_h)
    """
    axis = (int(axis[0]), int(axis[1]))
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    try:
        if pos == 'bl':
            if text_color_bg:
                cv2.rectangle(img, axis, (axis[0]+text_w, axis[1]-text_h*2), text_color_bg, -1)
            cv2.putText(img, text, (axis[0], int(axis[1] - text_h/2)), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        elif pos == 'tl':
            if text_color_bg:
                cv2.rectangle(img, axis, (axis[0]+text_w, axis[1]+text_h*2), text_color_bg, thickness=-1)
            cv2.putText(img, text, (axis[0], int(axis[1] + text_h*3/2)), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        elif pos == 'tr':
            if text_color_bg:
                cv2.rectangle(img, axis, (axis[0]-text_w, axis[1]+text_h*2), text_color_bg, thickness=-1)
            cv2.putText(img, text, (axis[0]-text_w, int(axis[1] + text_h*3/2)), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        elif pos == 'br':
            if text_color_bg:
                cv2.rectangle(img, axis, (axis[0]-text_w, axis[1]-text_h*2), text_color_bg, thickness=-1)
            cv2.putText(img, text, (axis[0]-text_w, int(axis[1] - text_h/2)), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
    except:
        print('position and axis are wrong setting')
        
    return text_w, text_h * 2
        
    
def draw_bbox(img, 
              result, 
              idxs=None, 
              classes=None, 
              str_list=[],
              score=False, 
              track_id=False,
              font=cv2.FONT_HERSHEY_SIMPLEX,
              font_scale=0.5,
              font_thickness=1,
              color=None):
    """
    Draw bounding boxes on the image according to the detection result.
    img will be modified in place.
    params:
        img: np.ndarray
        result: np.ndarray, [x1, y1, x2, y2, score, class, uid]
        classes: list
        score: bool
        str_list: list
        font: int
        font_scale: float
        font_thickness: int
        idxs: list
        color: tuple
    """
    if isinstance(result, np.ndarray):
        if result.ndim == 1:
            result = np.expand_dims(result, 0)
        for j in range(result.shape[0]):
            if idxs is None or result[j, 5] in idxs:
                _color = color if color else color_list[int(result[j, 5]) % len(color_list)]    
                    
                cv2.rectangle(img, (int(result[j, 0]), int(result[j, 1])), (int(result[j, 2]), int(result[j, 3])), _color, 2)
                
                if track_id:
                    bias_w, _ = draw_text(img, str(int(result[j, 6])),
                                          text_color=(255, 255, 255), text_color_bg=_color, 
                                          pos='bl', axis=(int(result[j, 0]), int(result[j, 1])))
                else:
                    bias_w = 0
                
                if classes:
                    text = str(classes[int(result[j, 5])])
                    if score:
                        text += ': ' + str(round(result[j, 4], 2))
                    cv2.putText(img, text, (int(result[j, 0]) + bias_w, int(result[j, 1])-5), font, font_scale, _color, font_thickness, cv2.LINE_AA)
                elif str_list:
                    cv2.putText(img, str_list[j], (int(result[j, 0]) + bias_w, int(result[j, 1])-5), font, font_scale, _color, font_thickness, cv2.LINE_AA)


def images_automerge(images, size):
    """
    Merge images into one image.
    params:
        images: list
        size: tuple
    return:
        np.ndarray
    """
    num = (math.ceil(len(images) ** 0.5))
    if isinstance(size, int):
        size = (size, size)
    w, h = size
    
    result = np.zeros((h, w, 3), dtype='uint8')
    w = int(w / num)
    h = int(h / num)
    for i, img in enumerate(images):
        r = int(i / num)
        c = int(i % num)
        result[r*h:(r+1)*h, c*w:(c+1)*w, :] = cv2.resize(img, (w, h))
        
    return result

def draw_mask_on_img(img, mask, reverse=False, alpha=0.5, color=[0, 0, 255]):
    img_uint8 = img.astype(np.uint8)
    overlay = np.zeros_like(img_uint8)
    overlay[:, :] = color
    if reverse:
        mask = ~(mask.astype(bool))
    mask_uint8 = (mask * 255).astype(np.uint8)  # ensure the mask is in uint8 not bool
    masked_overlay = cv2.multiply(overlay, np.stack([mask_uint8]*3, axis=-1))
    result = cv2.addWeighted(img_uint8, 1, masked_overlay, alpha, 0)
    
    return result