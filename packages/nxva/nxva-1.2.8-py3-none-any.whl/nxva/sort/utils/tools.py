import numpy as np
import torch

def xyxy2xywh(x):
    """
    Convert bounding box coordinates from (x1, y1, x2, y2) format to (x, y, width, height) format.

    Args:
        x (np.ndarray) or (torch.Tensor): The input bounding box coordinates in (x1, y1, x2, y2) format.
    Returns:
       y (np.ndarray) or (torch.Tensor): The bounding box coordinates in (x, y, width, height) format.
    """
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[..., 0] = (x[..., 0] + x[..., 2]) / 2  # x center
    y[..., 1] = (x[..., 1] + x[..., 3]) / 2  # y center
    y[..., 2] = x[..., 2] - x[..., 0]  # width
    y[..., 3] = x[..., 3] - x[..., 1]  # height
    return y



def nn_cosine_distance(x, y):
    """ Helper function for nearest neighbor distance metric (cosine).
    Parameters
    ----------
    x : ndarray
        A matrix of N row-vectors (sample points).
    y : ndarray
        A matrix of M row-vectors (query points).
    Returns
    -------
    ndarray
        A vector of length M that contains for each entry in `y` the
        smallest cosine distance to a sample in `x`.
    """
    x_ = torch.from_numpy(np.asarray(x, dtype=np.float64))
    y_ = torch.from_numpy(np.asarray(y, dtype=np.float64))
    # x_ = torch.from_numpy(np.asarray(x))
    # y_ = torch.from_numpy(np.asarray(y))
    distances = _cosine_distance(x_, y_)
    distances = distances
    # return distances.min(axis=0)
    return distances.max(axis=0) #改成愈大愈好

def _cosine_distance(a, b, data_is_normalized=False): #計算特徵距離（愈大愈好）
    """Compute pair-wise cosine distance between points in `a` and `b`.
    Parameters
    ----------
    a : array_like
        An NxM matrix of N samples of dimensionality M.
    b : array_like
        An LxM matrix of L samples of dimensionality M.
    data_is_normalized : Optional[bool]
        If True, assumes rows in a and b are unit length vectors.
        Otherwise, a and b are explicitly normalized to lenght 1.
    Returns
    -------
    ndarray
        Returns a matrix of size len(a), len(b) such that eleement (i, j)
        contains the squared distance between `a[i]` and `b[j]`.
    """
    if not data_is_normalized:
        a = np.asarray(a) / np.linalg.norm(a, axis=1, keepdims=True)
        b = np.asarray(b) / np.linalg.norm(b, axis=1, keepdims=True)
    # return 1 - np.dot(a, b.T)
    return np.dot(a, b.T) #改成愈大愈好

def k_previous_obs(observations, cur_age, k):
    if len(observations) == 0:
        return [-1, -1, -1, -1, -1]
    for i in range(k):
        dt = k - i
        if cur_age - dt in observations:
            return observations[cur_age-dt]
    max_age = max(observations.keys())
    return observations[max_age]

def get_speed_direction(pre_time, cur_time, pre_box, pre_n_box, cur_box, pos_lambda, direction_type='vector'):


    pre_n_cx = (1 - pos_lambda[0]) * pre_n_box[0] + pos_lambda[0] * pre_n_box[2]
    pre_n_cy = (1 - pos_lambda[1]) * pre_n_box[1] + pos_lambda[1] * pre_n_box[3]

    pre_cx = (1 - pos_lambda[0]) * pre_box[0] + pos_lambda[0] * pre_box[2]
    pre_cy = (1 - pos_lambda[1]) * pre_box[1] + pos_lambda[1] * pre_box[3]

    cur_cx = (1 - pos_lambda[0]) * cur_box[0] + pos_lambda[0] * cur_box[2]
    cur_cy = (1 - pos_lambda[1]) * cur_box[1] + pos_lambda[1] * cur_box[3]


    delta_1_x = cur_cx - pre_cx
    delta_1_y = cur_cy - pre_cy
    
    delta_n_x = cur_cx - pre_n_cx
    delta_n_y = cur_cy - pre_n_cy
    
    # speed ( ||delta_x,delta_y|| / ( tiem.time() - pre_time) )
    delta_mov = np.sqrt(delta_1_x ** 2 + delta_1_y ** 2) #+ 1e-6
    speed = delta_mov / (cur_time - pre_time)

    if direction_type == 'angle':
        # direction (delta_y/delta_x) 水平3點鐘方向=0度, 逆時針0~360度
        velocity_direction = np.degrees(np.arctan2(delta_n_y, delta_n_x))
        if velocity_direction < 0 :
            velocity_direction +=360
        return speed, velocity_direction

    elif direction_type == 'vector':
        vector = (delta_n_x, delta_n_y)
        return speed, vector
    
    elif direction_type == 'radian':
        radian = np.arctan2(delta_n_y, delta_n_x)
        return speed, radian
    
    else:
        # TODO
        raise(ValueError("Unsupported direction type: {}".format(direction_type)))
        print('we don"t have this direction type')
        return None



