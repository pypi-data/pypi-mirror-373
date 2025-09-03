import math, contextlib, re
from pathlib import Path
from typing import Union, Optional, Dict, Any, List, Callable

import functools, threading

from PIL import Image, ImageDraw, ImageFont
from PIL import __version__ as pil_version

import cv2
import numpy as np

import torch

from nxva.yolo.utils import ops


class ThreadingLocked:
    """
    A decorator class for ensuring thread-safe execution of a function or method.

    This class can be used as a decorator to make sure that if the decorated function is called from multiple threads,
    only one thread at a time will be able to execute the function.

    Attributes:
        lock (threading.Lock): A lock object used to manage access to the decorated function.

    Examples:
        >>> from ultralytics.utils import ThreadingLocked
        >>> @ThreadingLocked()
        >>> def my_function():
        ...    # Your code here
    """

    def __init__(self):
        """Initialize the decorator class with a threading lock."""
        self.lock = threading.Lock()

    def __call__(self, f):
        """Run thread-safe execution of function or method."""
        from functools import wraps

        @wraps(f)
        def decorated(*args, **kwargs):
            """Apply thread-safety to the decorated function or method."""
            with self.lock:
                return f(*args, **kwargs)

        return decorated

def increment_path(path: Union[str, Path], exist_ok: bool = False, sep: str = "", mkdir: bool = False) -> Path:
    """
    Increment a file or directory path, i.e., runs/exp --> runs/exp{sep}2, runs/exp{sep}3, ... etc.

    If the path exists and `exist_ok` is not True, the path will be incremented by appending a number and `sep` to
    the end of the path. If the path is a file, the file extension will be preserved. If the path is a directory, the
    number will be appended directly to the end of the path.

    Args:
        path (str | Path): Path to increment.
        exist_ok (bool, optional): If True, the path will not be incremented and returned as-is.
        sep (str, optional): Separator to use between the path and the incrementation number.
        mkdir (bool, optional): Create a directory if it does not exist.

    Returns:
        (Path): Incremented path.

    Examples:
        Increment a directory path:
        >>> from pathlib import Path
        >>> path = Path("runs/exp")
        >>> new_path = increment_path(path)
        >>> print(new_path)
        runs/exp2

        Increment a file path:
        >>> path = Path("runs/exp/results.txt")
        >>> new_path = increment_path(path)
        >>> print(new_path)
        runs/exp/results2.txt
    """
    path = Path(path)  # os-agnostic
    if path.exists() and not exist_ok:
        path, suffix = (path.with_suffix(""), path.suffix) if path.is_file() else (path, "")

        # Method 1
        for n in range(2, 9999):
            p = f"{path}{sep}{n}{suffix}"  # increment path
            if not os.path.exists(p):
                break
        path = Path(p)

    if mkdir:
        path.mkdir(parents=True, exist_ok=True)  # make directory

    return path



def plt_settings(rcparams=None, backend="Agg"):
    """
    Decorator to temporarily set rc parameters and the backend for a plotting function.

    Args:
        rcparams (dict, optional): Dictionary of rc parameters to set.
        backend (str, optional): Name of the backend to use.

    Returns:
        (Callable): Decorated function with temporarily set rc parameters and backend.

    Examples:
        >>> @plt_settings({"font.size": 12})
        >>> def plot_function():
        ...     plt.figure()
        ...     plt.plot([1, 2, 3])
        ...     plt.show()

        >>> with plt_settings({"font.size": 12}):
        ...     plt.figure()
        ...     plt.plot([1, 2, 3])
        ...     plt.show()
    """
    if rcparams is None:
        rcparams = {"font.size": 11}

    def decorator(func):
        """Decorator to apply temporary rc parameters and backend to a function."""

        def wrapper(*args, **kwargs):
            """Set rc parameters and backend, call the original function, and restore the settings."""
            import matplotlib.pyplot as plt  # scope for faster 'import ultralytics'

            original_backend = plt.get_backend()
            switch = backend.lower() != original_backend.lower()
            if switch:
                plt.close("all")  # auto-close()ing of figures upon backend switching is deprecated since 3.8
                plt.switch_backend(backend)

            # Plot with backend and always revert to original backend
            try:
                with plt.rc_context(rcparams):
                    result = func(*args, **kwargs)
            finally:
                if switch:
                    plt.close("all")
                    plt.switch_backend(original_backend)
            return result

        return wrapper

    return decorator

def threaded(func):
    """
    Multi-thread a target function by default and return the thread or function result.

    This decorator provides flexible execution of the target function, either in a separate thread or synchronously.
    By default, the function runs in a thread, but this can be controlled via the 'threaded=False' keyword argument
    which is removed from kwargs before calling the function.

    Args:
        func (callable): The function to be potentially executed in a separate thread.

    Returns:
        (callable): A wrapper function that either returns a daemon thread or the direct function result.

    Examples:
        >>> @threaded
        ... def process_data(data):
        ...     return data
        >>>
        >>> thread = process_data(my_data)  # Runs in background thread
        >>> result = process_data(my_data, threaded=False)  # Runs synchronously, returns function result
    """

    def wrapper(*args, **kwargs):
        """Multi-thread a given function based on 'threaded' kwarg and return the thread or function result."""
        if kwargs.pop("threaded", True):  # run in thread
            thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
            thread.start()
            return thread
        else:
            return func(*args, **kwargs)

    return wrapper

def is_ascii(s) -> bool:
    """
    Check if a string is composed of only ASCII characters.

    Args:
        s (str | list | tuple | dict): Input to be checked (all are converted to string for checking).

    Returns:
        (bool): True if the string is composed only of ASCII characters, False otherwise.
    """
    return all(ord(c) < 128 for c in str(s))

def parse_version(version="0.0.0") -> tuple:
    """
    Convert a version string to a tuple of integers, ignoring any extra non-numeric string attached to the version. This
    function replaces deprecated 'pkg_resources.parse_version(v)'.

    Args:
        version (str): Version string, i.e. '2.0.1+cpu'

    Returns:
        (tuple): Tuple of integers representing the numeric part of the version and the extra string, i.e. (2, 0, 1)
    """
    try:
        return tuple(map(int, re.findall(r"\d+", version)[:3]))  # '2.0.1+cpu' -> (2, 0, 1)
    except Exception as e:
        return 0, 0, 0

@functools.lru_cache
def check_version(
    current: str = "0.0.0",
    required: str = "0.0.0",
    name: str = "version",
    hard: bool = False,
    verbose: bool = False,
    msg: str = "",
) -> bool:
    """
    Check current version against the required version or range.

    Args:
        current (str): Current version or package name to get version from.
        required (str): Required version or range (in pip-style format).
        name (str): Name to be used in warning message.
        hard (bool): If True, raise an AssertionError if the requirement is not met.
        verbose (bool): If True, print warning message if requirement is not met.
        msg (str): Extra message to display if verbose.

    Returns:
        (bool): True if requirement is met, False otherwise.

    Examples:
        Check if current version is exactly 22.04
        >>> check_version(current="22.04", required="==22.04")

        Check if current version is greater than or equal to 22.04
        >>> check_version(current="22.10", required="22.04")  # assumes '>=' inequality if none passed

        Check if current version is less than or equal to 22.04
        >>> check_version(current="22.04", required="<=22.04")

        Check if current version is between 20.04 (inclusive) and 22.04 (exclusive)
        >>> check_version(current="21.10", required=">20.04,<22.04")
    """
    if not current:  # if current is '' or None
        LOGGER.warning(f"invalid check_version({current}, {required}) requested, please check values.")
        return True
    elif not current[0].isdigit():  # current is package name rather than version string, i.e. current='ultralytics'
        try:
            name = current  # assigned package name to 'name' arg
            current = metadata.version(current)  # get version string from package name
        except metadata.PackageNotFoundError as e:
            if hard:
                raise ModuleNotFoundError(f"{current} package is required but not installed") from e
            else:
                return False

    if not required:  # if required is '' or None
        return True

    if "sys_platform" in required and (  # i.e. required='<2.4.0,>=1.8.0; sys_platform == "win32"'
        (WINDOWS and "win32" not in required)
        or (LINUX and "linux" not in required)
        or (MACOS and "macos" not in required and "darwin" not in required)
    ):
        return True

    op = ""
    version = ""
    result = True
    c = parse_version(current)  # '1.2.3' -> (1, 2, 3)
    for r in required.strip(",").split(","):
        op, version = re.match(r"([^0-9]*)([\d.]+)", r).groups()  # split '>=22.04' -> ('>=', '22.04')
        if not op:
            op = ">="  # assume >= if no op passed
        v = parse_version(version)  # '1.2.3' -> (1, 2, 3)
        if op == "==" and c != v:
            result = False
        elif op == "!=" and c == v:
            result = False
        elif op == ">=" and not (c >= v):
            result = False
        elif op == "<=" and not (c <= v):
            result = False
        elif op == ">" and not (c > v):
            result = False
        elif op == "<" and not (c < v):
            result = False
    if not result:
        warning = f"{name}{required} is required, but {name}=={current} is currently installed {msg}"
        if hard:
            raise ModuleNotFoundError(warning)  # assert version requirements met
        if verbose:
            LOGGER.warning(warning)
    return result

@ThreadingLocked()
@functools.lru_cache
def check_font(font="Arial.ttf"):
    """
    Find font locally or download to user's configuration directory if it does not already exist.

    Args:
        font (str): Path or name of font.

    Returns:
        (Path): Resolved font file path.
    """
    from matplotlib import font_manager  # scope for faster 'import ultralytics'

    # Check USER_CONFIG_DIR
    name = Path(font).name
    file = USER_CONFIG_DIR / name
    if file.exists():
        return file

    # Check system fonts
    matches = [s for s in font_manager.findSystemFonts() if font in s]
    if any(matches):
        return matches[0]

    # Download to USER_CONFIG_DIR if missing
    url = f"https://github.com/ultralytics/assets/releases/download/v0.0.0/{name}"
    if downloads.is_url(url, check=True):
        downloads.safe_download(url=url, file=file)
        return file


class TryExcept(contextlib.ContextDecorator):
    """
    Ultralytics TryExcept class for handling exceptions gracefully.

    This class can be used as a decorator or context manager to catch exceptions and optionally print warning messages.
    It allows code to continue execution even when exceptions occur, which is useful for non-critical operations.

    Attributes:
        msg (str): Optional message to display when an exception occurs.
        verbose (bool): Whether to print the exception message.

    Examples:
        As a decorator:
        >>> @TryExcept(msg="Error occurred in func", verbose=True)
        >>> def func():
        >>> # Function logic here
        >>>     pass

        As a context manager:
        >>> with TryExcept(msg="Error occurred in block", verbose=True):
        >>> # Code block here
        >>>     pass
    """

    def __init__(self, msg="", verbose=True):
        """Initialize TryExcept class with optional message and verbosity settings."""
        self.msg = msg
        self.verbose = verbose

    def __enter__(self):
        """Execute when entering TryExcept context, initialize instance."""
        pass

    def __exit__(self, exc_type, value, traceback):
        """Define behavior when exiting a 'with' block, print error message if necessary."""
        if self.verbose and value:
            LOGGER.warning(f"{self.msg}{': ' if self.msg else ''}{value}")
        return True
        

class Colors:
    """
    Ultralytics color palette for visualization and plotting.

    This class provides methods to work with the Ultralytics color palette, including converting hex color codes to
    RGB values and accessing predefined color schemes for object detection and pose estimation.

    Attributes:
        palette (List[tuple]): List of RGB color tuples for general use.
        n (int): The number of colors in the palette.
        pose_palette (np.ndarray): A specific color palette array for pose estimation with dtype np.uint8.

    Examples:
        >>> from ultralytics.utils.plotting import Colors
        >>> colors = Colors()
        >>> colors(5, True)  # Returns BGR format: (221, 111, 255)
        >>> colors(5, False)  # Returns RGB format: (255, 111, 221)

    ## Ultralytics Color Palette

    | Index | Color                                                             | HEX       | RGB               |
    |-------|-------------------------------------------------------------------|-----------|-------------------|
    | 0     | <i class="fa-solid fa-square fa-2xl" style="color: #042aff;"></i> | `#042aff` | (4, 42, 255)      |
    | 1     | <i class="fa-solid fa-square fa-2xl" style="color: #0bdbeb;"></i> | `#0bdbeb` | (11, 219, 235)    |
    | 2     | <i class="fa-solid fa-square fa-2xl" style="color: #f3f3f3;"></i> | `#f3f3f3` | (243, 243, 243)   |
    | 3     | <i class="fa-solid fa-square fa-2xl" style="color: #00dfb7;"></i> | `#00dfb7` | (0, 223, 183)     |
    | 4     | <i class="fa-solid fa-square fa-2xl" style="color: #111f68;"></i> | `#111f68` | (17, 31, 104)     |
    | 5     | <i class="fa-solid fa-square fa-2xl" style="color: #ff6fdd;"></i> | `#ff6fdd` | (255, 111, 221)   |
    | 6     | <i class="fa-solid fa-square fa-2xl" style="color: #ff444f;"></i> | `#ff444f` | (255, 68, 79)     |
    | 7     | <i class="fa-solid fa-square fa-2xl" style="color: #cced00;"></i> | `#cced00` | (204, 237, 0)     |
    | 8     | <i class="fa-solid fa-square fa-2xl" style="color: #00f344;"></i> | `#00f344` | (0, 243, 68)      |
    | 9     | <i class="fa-solid fa-square fa-2xl" style="color: #bd00ff;"></i> | `#bd00ff` | (189, 0, 255)     |
    | 10    | <i class="fa-solid fa-square fa-2xl" style="color: #00b4ff;"></i> | `#00b4ff` | (0, 180, 255)     |
    | 11    | <i class="fa-solid fa-square fa-2xl" style="color: #dd00ba;"></i> | `#dd00ba` | (221, 0, 186)     |
    | 12    | <i class="fa-solid fa-square fa-2xl" style="color: #00ffff;"></i> | `#00ffff` | (0, 255, 255)     |
    | 13    | <i class="fa-solid fa-square fa-2xl" style="color: #26c000;"></i> | `#26c000` | (38, 192, 0)      |
    | 14    | <i class="fa-solid fa-square fa-2xl" style="color: #01ffb3;"></i> | `#01ffb3` | (1, 255, 179)     |
    | 15    | <i class="fa-solid fa-square fa-2xl" style="color: #7d24ff;"></i> | `#7d24ff` | (125, 36, 255)    |
    | 16    | <i class="fa-solid fa-square fa-2xl" style="color: #7b0068;"></i> | `#7b0068` | (123, 0, 104)     |
    | 17    | <i class="fa-solid fa-square fa-2xl" style="color: #ff1b6c;"></i> | `#ff1b6c` | (255, 27, 108)    |
    | 18    | <i class="fa-solid fa-square fa-2xl" style="color: #fc6d2f;"></i> | `#fc6d2f` | (252, 109, 47)    |
    | 19    | <i class="fa-solid fa-square fa-2xl" style="color: #a2ff0b;"></i> | `#a2ff0b` | (162, 255, 11)    |

    ## Pose Color Palette

    | Index | Color                                                             | HEX       | RGB               |
    |-------|-------------------------------------------------------------------|-----------|-------------------|
    | 0     | <i class="fa-solid fa-square fa-2xl" style="color: #ff8000;"></i> | `#ff8000` | (255, 128, 0)     |
    | 1     | <i class="fa-solid fa-square fa-2xl" style="color: #ff9933;"></i> | `#ff9933` | (255, 153, 51)    |
    | 2     | <i class="fa-solid fa-square fa-2xl" style="color: #ffb266;"></i> | `#ffb266` | (255, 178, 102)   |
    | 3     | <i class="fa-solid fa-square fa-2xl" style="color: #e6e600;"></i> | `#e6e600` | (230, 230, 0)     |
    | 4     | <i class="fa-solid fa-square fa-2xl" style="color: #ff99ff;"></i> | `#ff99ff` | (255, 153, 255)   |
    | 5     | <i class="fa-solid fa-square fa-2xl" style="color: #99ccff;"></i> | `#99ccff` | (153, 204, 255)   |
    | 6     | <i class="fa-solid fa-square fa-2xl" style="color: #ff66ff;"></i> | `#ff66ff` | (255, 102, 255)   |
    | 7     | <i class="fa-solid fa-square fa-2xl" style="color: #ff33ff;"></i> | `#ff33ff` | (255, 51, 255)    |
    | 8     | <i class="fa-solid fa-square fa-2xl" style="color: #66b2ff;"></i> | `#66b2ff` | (102, 178, 255)   |
    | 9     | <i class="fa-solid fa-square fa-2xl" style="color: #3399ff;"></i> | `#3399ff` | (51, 153, 255)    |
    | 10    | <i class="fa-solid fa-square fa-2xl" style="color: #ff9999;"></i> | `#ff9999` | (255, 153, 153)   |
    | 11    | <i class="fa-solid fa-square fa-2xl" style="color: #ff6666;"></i> | `#ff6666` | (255, 102, 102)   |
    | 12    | <i class="fa-solid fa-square fa-2xl" style="color: #ff3333;"></i> | `#ff3333` | (255, 51, 51)     |
    | 13    | <i class="fa-solid fa-square fa-2xl" style="color: #99ff99;"></i> | `#99ff99` | (153, 255, 153)   |
    | 14    | <i class="fa-solid fa-square fa-2xl" style="color: #66ff66;"></i> | `#66ff66` | (102, 255, 102)   |
    | 15    | <i class="fa-solid fa-square fa-2xl" style="color: #33ff33;"></i> | `#33ff33` | (51, 255, 51)     |
    | 16    | <i class="fa-solid fa-square fa-2xl" style="color: #00ff00;"></i> | `#00ff00` | (0, 255, 0)       |
    | 17    | <i class="fa-solid fa-square fa-2xl" style="color: #0000ff;"></i> | `#0000ff` | (0, 0, 255)       |
    | 18    | <i class="fa-solid fa-square fa-2xl" style="color: #ff0000;"></i> | `#ff0000` | (255, 0, 0)       |
    | 19    | <i class="fa-solid fa-square fa-2xl" style="color: #ffffff;"></i> | `#ffffff` | (255, 255, 255)   |

    !!! note "Ultralytics Brand Colors"

        For Ultralytics brand colors see [https://www.ultralytics.com/brand](https://www.ultralytics.com/brand).
        Please use the official Ultralytics colors for all marketing materials.
    """

    def __init__(self):
        """Initialize colors as hex = matplotlib.colors.TABLEAU_COLORS.values()."""
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
        self.palette = [self.hex2rgb(f"#{c}") for c in hexs]
        self.n = len(self.palette)
        self.pose_palette = np.array(
            [
                [255, 128, 0],
                [255, 153, 51],
                [255, 178, 102],
                [230, 230, 0],
                [255, 153, 255],
                [153, 204, 255],
                [255, 102, 255],
                [255, 51, 255],
                [102, 178, 255],
                [51, 153, 255],
                [255, 153, 153],
                [255, 102, 102],
                [255, 51, 51],
                [153, 255, 153],
                [102, 255, 102],
                [51, 255, 51],
                [0, 255, 0],
                [0, 0, 255],
                [255, 0, 0],
                [255, 255, 255],
            ],
            dtype=np.uint8,
        )

    def __call__(self, i: int, bgr: bool = False) -> tuple:
        """
        Convert hex color codes to RGB values.

        Args:
            i (int): Color index.
            bgr (bool, optional): Whether to return BGR format instead of RGB.

        Returns:
            (tuple): RGB or BGR color tuple.
        """
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h: str) -> tuple:
        """Convert hex color codes to RGB values (i.e. default PIL order)."""
        return tuple(int(h[1 + i : 1 + i + 2], 16) for i in (0, 2, 4))


colors = Colors()  # create instance for 'from utils.plots import colors'


class Annotator:
    """
    Ultralytics Annotator for train/val mosaics and JPGs and predictions annotations.

    Attributes:
        im (Image.Image | np.ndarray): The image to annotate.
        pil (bool): Whether to use PIL or cv2 for drawing annotations.
        font (ImageFont.truetype | ImageFont.load_default): Font used for text annotations.
        lw (float): Line width for drawing.
        skeleton (List[List[int]]): Skeleton structure for keypoints.
        limb_color (List[int]): Color palette for limbs.
        kpt_color (List[int]): Color palette for keypoints.
        dark_colors (set): Set of colors considered dark for text contrast.
        light_colors (set): Set of colors considered light for text contrast.

    Examples:
        >>> from ultralytics.utils.plotting import Annotator
        >>> im0 = cv2.imread("test.png")
        >>> annotator = Annotator(im0, line_width=10)
        >>> annotator.box_label([10, 10, 100, 100], "person", (255, 0, 0))
    """

    def __init__(
        self,
        im,
        line_width: Optional[int] = None,
        font_size: Optional[int] = None,
        font: str = "Arial.ttf",
        pil: bool = False,
        example: str = "abc",
    ):
        """Initialize the Annotator class with image and line width along with color palette for keypoints and limbs."""
        non_ascii = not is_ascii(example)  # non-latin labels, i.e. asian, arabic, cyrillic
        input_is_pil = isinstance(im, Image.Image)
        self.pil = pil or non_ascii or input_is_pil
        self.lw = line_width or max(round(sum(im.size if input_is_pil else im.shape) / 2 * 0.003), 2)
        if not input_is_pil:
            if im.shape[2] == 1:  # handle grayscale
                im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
            elif im.shape[2] > 3:  # multispectral
                im = np.ascontiguousarray(im[..., :3])
        if self.pil:  # use PIL
            self.im = im if input_is_pil else Image.fromarray(im)
            if self.im.mode not in {"RGB", "RGBA"}:  # multispectral
                self.im = self.im.convert("RGB")
            self.draw = ImageDraw.Draw(self.im, "RGBA")
            try:
                font = check_font("Arial.Unicode.ttf" if non_ascii else font)
                size = font_size or max(round(sum(self.im.size) / 2 * 0.035), 12)
                self.font = ImageFont.truetype(str(font), size)
            except Exception:
                self.font = ImageFont.load_default()
            # Deprecation fix for w, h = getsize(string) -> _, _, w, h = getbox(string)
            if check_version(pil_version, "9.2.0"):
                self.font.getsize = lambda x: self.font.getbbox(x)[2:4]  # text width, height
        else:  # use cv2
            assert im.data.contiguous, "Image not contiguous. Apply np.ascontiguousarray(im) to Annotator input images."
            self.im = im if im.flags.writeable else im.copy()
            self.tf = max(self.lw - 1, 1)  # font thickness
            self.sf = self.lw / 3  # font scale
        # Pose
        self.skeleton = [
            [16, 14],
            [14, 12],
            [17, 15],
            [15, 13],
            [12, 13],
            [6, 12],
            [7, 13],
            [6, 7],
            [6, 8],
            [7, 9],
            [8, 10],
            [9, 11],
            [2, 3],
            [1, 2],
            [1, 3],
            [2, 4],
            [3, 5],
            [4, 6],
            [5, 7],
        ]

        self.limb_color = colors.pose_palette[[9, 9, 9, 9, 7, 7, 7, 0, 0, 0, 0, 0, 16, 16, 16, 16, 16, 16, 16]]
        self.kpt_color = colors.pose_palette[[16, 16, 16, 16, 16, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9]]
        self.dark_colors = {
            (235, 219, 11),
            (243, 243, 243),
            (183, 223, 0),
            (221, 111, 255),
            (0, 237, 204),
            (68, 243, 0),
            (255, 255, 0),
            (179, 255, 1),
            (11, 255, 162),
        }
        self.light_colors = {
            (255, 42, 4),
            (79, 68, 255),
            (255, 0, 189),
            (255, 180, 0),
            (186, 0, 221),
            (0, 192, 38),
            (255, 36, 125),
            (104, 0, 123),
            (108, 27, 255),
            (47, 109, 252),
            (104, 31, 17),
        }

    def get_txt_color(self, color: tuple = (128, 128, 128), txt_color: tuple = (255, 255, 255)) -> tuple:
        """
        Assign text color based on background color.

        Args:
            color (tuple, optional): The background color of the rectangle for text (B, G, R).
            txt_color (tuple, optional): The color of the text (R, G, B).

        Returns:
            (tuple): Text color for label.

        Examples:
            >>> from ultralytics.utils.plotting import Annotator
            >>> im0 = cv2.imread("test.png")
            >>> annotator = Annotator(im0, line_width=10)
            >>> annotator.get_txt_color(color=(104, 31, 17))  # return (255, 255, 255)
        """
        if color in self.dark_colors:
            return 104, 31, 17
        elif color in self.light_colors:
            return 255, 255, 255
        else:
            return txt_color

    def box_label(self, box, label: str = "", color: tuple = (128, 128, 128), txt_color: tuple = (255, 255, 255)):
        """
        Draw a bounding box on an image with a given label.

        Args:
            box (tuple): The bounding box coordinates (x1, y1, x2, y2).
            label (str, optional): The text label to be displayed.
            color (tuple, optional): The background color of the rectangle (B, G, R).
            txt_color (tuple, optional): The color of the text (R, G, B).

        Examples:
            >>> from ultralytics.utils.plotting import Annotator
            >>> im0 = cv2.imread("test.png")
            >>> annotator = Annotator(im0, line_width=10)
            >>> annotator.box_label(box=[10, 20, 30, 40], label="person")
        """
        txt_color = self.get_txt_color(color, txt_color)
        if isinstance(box, torch.Tensor):
            box = box.tolist()

        multi_points = isinstance(box[0], list)  # multiple points with shape (n, 2)
        p1 = [int(b) for b in box[0]] if multi_points else (int(box[0]), int(box[1]))
        if self.pil:
            self.draw.polygon(
                [tuple(b) for b in box], width=self.lw, outline=color
            ) if multi_points else self.draw.rectangle(box, width=self.lw, outline=color)
            if label:
                w, h = self.font.getsize(label)  # text width, height
                outside = p1[1] >= h  # label fits outside box
                if p1[0] > self.im.size[0] - w:  # size is (w, h), check if label extend beyond right side of image
                    p1 = self.im.size[0] - w, p1[1]
                self.draw.rectangle(
                    (p1[0], p1[1] - h if outside else p1[1], p1[0] + w + 1, p1[1] + 1 if outside else p1[1] + h + 1),
                    fill=color,
                )
                # self.draw.text([box[0], box[1]], label, fill=txt_color, font=self.font, anchor='ls')  # for PIL>8.0
                self.draw.text((p1[0], p1[1] - h if outside else p1[1]), label, fill=txt_color, font=self.font)
        else:  # cv2
            cv2.polylines(
                self.im, [np.asarray(box, dtype=int)], True, color, self.lw
            ) if multi_points else cv2.rectangle(
                self.im, p1, (int(box[2]), int(box[3])), color, thickness=self.lw, lineType=cv2.LINE_AA
            )
            if label:
                w, h = cv2.getTextSize(label, 0, fontScale=self.sf, thickness=self.tf)[0]  # text width, height
                h += 3  # add pixels to pad text
                outside = p1[1] >= h  # label fits outside box
                if p1[0] > self.im.shape[1] - w:  # shape is (h, w), check if label extend beyond right side of image
                    p1 = self.im.shape[1] - w, p1[1]
                p2 = p1[0] + w, p1[1] - h if outside else p1[1] + h
                cv2.rectangle(self.im, p1, p2, color, -1, cv2.LINE_AA)  # filled
                cv2.putText(
                    self.im,
                    label,
                    (p1[0], p1[1] - 2 if outside else p1[1] + h - 1),
                    0,
                    self.sf,
                    txt_color,
                    thickness=self.tf,
                    lineType=cv2.LINE_AA,
                )

    def masks(self, masks, colors, im_gpu, alpha: float = 0.5, retina_masks: bool = False):
        """
        Plot masks on image.

        Args:
            masks (torch.Tensor): Predicted masks on cuda, shape: [n, h, w]
            colors (List[List[int]]): Colors for predicted masks, [[r, g, b] * n]
            im_gpu (torch.Tensor): Image is in cuda, shape: [3, h, w], range: [0, 1]
            alpha (float, optional): Mask transparency: 0.0 fully transparent, 1.0 opaque.
            retina_masks (bool, optional): Whether to use high resolution masks or not.
        """
        if self.pil:
            # Convert to numpy first
            self.im = np.asarray(self.im).copy()
        if len(masks) == 0:
            self.im[:] = im_gpu.permute(1, 2, 0).contiguous().cpu().numpy() * 255
        if im_gpu.device != masks.device:
            im_gpu = im_gpu.to(masks.device)
        colors = torch.tensor(colors, device=masks.device, dtype=torch.float32) / 255.0  # shape(n,3)
        colors = colors[:, None, None]  # shape(n,1,1,3)
        masks = masks.unsqueeze(3)  # shape(n,h,w,1)
        masks_color = masks * (colors * alpha)  # shape(n,h,w,3)

        inv_alpha_masks = (1 - masks * alpha).cumprod(0)  # shape(n,h,w,1)
        mcs = masks_color.max(dim=0).values  # shape(n,h,w,3)

        im_gpu = im_gpu.flip(dims=[0])  # flip channel
        im_gpu = im_gpu.permute(1, 2, 0).contiguous()  # shape(h,w,3)
        im_gpu = im_gpu * inv_alpha_masks[-1] + mcs
        im_mask = im_gpu * 255
        im_mask_np = im_mask.byte().cpu().numpy()
        self.im[:] = im_mask_np if retina_masks else ops.scale_image(im_mask_np, self.im.shape)
        if self.pil:
            # Convert im back to PIL and update draw
            self.fromarray(self.im)

    def kpts(
        self,
        kpts,
        shape: tuple = (640, 640),
        radius: Optional[int] = None,
        kpt_line: bool = True,
        conf_thres: float = 0.25,
        kpt_color: Optional[tuple] = None,
    ):
        """
        Plot keypoints on the image.

        Args:
            kpts (torch.Tensor): Keypoints, shape [17, 3] (x, y, confidence).
            shape (tuple, optional): Image shape (h, w).
            radius (int, optional): Keypoint radius.
            kpt_line (bool, optional): Draw lines between keypoints.
            conf_thres (float, optional): Confidence threshold.
            kpt_color (tuple, optional): Keypoint color (B, G, R).

        Note:
            - `kpt_line=True` currently only supports human pose plotting.
            - Modifies self.im in-place.
            - If self.pil is True, converts image to numpy array and back to PIL.
        """
        radius = radius if radius is not None else self.lw
        if self.pil:
            # Convert to numpy first
            self.im = np.asarray(self.im).copy()
        nkpt, ndim = kpts.shape
        is_pose = nkpt == 17 and ndim in {2, 3}
        kpt_line &= is_pose  # `kpt_line=True` for now only supports human pose plotting
        for i, k in enumerate(kpts):
            color_k = kpt_color or (self.kpt_color[i].tolist() if is_pose else colors(i))
            x_coord, y_coord = k[0], k[1]
            if x_coord % shape[1] != 0 and y_coord % shape[0] != 0:
                if len(k) == 3:
                    conf = k[2]
                    if conf < conf_thres:
                        continue
                cv2.circle(self.im, (int(x_coord), int(y_coord)), radius, color_k, -1, lineType=cv2.LINE_AA)

        if kpt_line:
            ndim = kpts.shape[-1]
            for i, sk in enumerate(self.skeleton):
                pos1 = (int(kpts[(sk[0] - 1), 0]), int(kpts[(sk[0] - 1), 1]))
                pos2 = (int(kpts[(sk[1] - 1), 0]), int(kpts[(sk[1] - 1), 1]))
                if ndim == 3:
                    conf1 = kpts[(sk[0] - 1), 2]
                    conf2 = kpts[(sk[1] - 1), 2]
                    if conf1 < conf_thres or conf2 < conf_thres:
                        continue
                if pos1[0] % shape[1] == 0 or pos1[1] % shape[0] == 0 or pos1[0] < 0 or pos1[1] < 0:
                    continue
                if pos2[0] % shape[1] == 0 or pos2[1] % shape[0] == 0 or pos2[0] < 0 or pos2[1] < 0:
                    continue
                cv2.line(
                    self.im,
                    pos1,
                    pos2,
                    kpt_color or self.limb_color[i].tolist(),
                    thickness=int(np.ceil(self.lw / 2)),
                    lineType=cv2.LINE_AA,
                )
        if self.pil:
            # Convert im back to PIL and update draw
            self.fromarray(self.im)

    def rectangle(self, xy, fill=None, outline=None, width: int = 1):
        """Add rectangle to image (PIL-only)."""
        self.draw.rectangle(xy, fill, outline, width)

    def text(self, xy, text: str, txt_color: tuple = (255, 255, 255), anchor: str = "top", box_color: tuple = ()):
        """
        Add text to an image using PIL or cv2.

        Args:
            xy (List[int]): Top-left coordinates for text placement.
            text (str): Text to be drawn.
            txt_color (tuple, optional): Text color (R, G, B).
            anchor (str, optional): Text anchor position ('top' or 'bottom').
            box_color (tuple, optional): Box color (R, G, B, A) with optional alpha.
        """
        if self.pil:
            w, h = self.font.getsize(text)
            if anchor == "bottom":  # start y from font bottom
                xy[1] += 1 - h
            for line in text.split("\n"):
                if box_color:
                    # Draw rectangle for each line
                    w, h = self.font.getsize(line)
                    self.draw.rectangle((xy[0], xy[1], xy[0] + w + 1, xy[1] + h + 1), fill=box_color)
                self.draw.text(xy, line, fill=txt_color, font=self.font)
                xy[1] += h
        else:
            if box_color:
                w, h = cv2.getTextSize(text, 0, fontScale=self.sf, thickness=self.tf)[0]
                h += 3  # add pixels to pad text
                outside = xy[1] >= h  # label fits outside box
                p2 = xy[0] + w, xy[1] - h if outside else xy[1] + h
                cv2.rectangle(self.im, xy, p2, box_color, -1, cv2.LINE_AA)  # filled
            cv2.putText(self.im, text, xy, 0, self.sf, txt_color, thickness=self.tf, lineType=cv2.LINE_AA)

    def fromarray(self, im):
        """Update self.im from a numpy array."""
        self.im = im if isinstance(im, Image.Image) else Image.fromarray(im)
        self.draw = ImageDraw.Draw(self.im)

    def result(self):
        """Return annotated image as array."""
        return np.asarray(self.im)

    def show(self, title: Optional[str] = None):
        """Show the annotated image."""
        im = Image.fromarray(np.asarray(self.im)[..., ::-1])  # Convert numpy array to PIL Image with RGB to BGR
        im.show(title=title)

    def save(self, filename: str = "image.jpg"):
        """Save the annotated image to 'filename'."""
        cv2.imwrite(filename, np.asarray(self.im))

    @staticmethod
    def get_bbox_dimension(bbox: Optional[tuple] = None):
        """
        Calculate the dimensions and area of a bounding box.

        Args:
            bbox (tuple): Bounding box coordinates in the format (x_min, y_min, x_max, y_max).

        Returns:
            width (float): Width of the bounding box.
            height (float): Height of the bounding box.
            area (float): Area enclosed by the bounding box.

        Examples:
            >>> from ultralytics.utils.plotting import Annotator
            >>> im0 = cv2.imread("test.png")
            >>> annotator = Annotator(im0, line_width=10)
            >>> annotator.get_bbox_dimension(bbox=[10, 20, 30, 40])
        """
        x_min, y_min, x_max, y_max = bbox
        width = x_max - x_min
        height = y_max - y_min
        return width, height, width * height


@TryExcept()  # known issue https://github.com/ultralytics/yolov5/issues/5395
@plt_settings()
def plot_labels(boxes, cls, names=(), save_dir=Path(""), on_plot=None):
    """
    Plot training labels including class histograms and box statistics.

    Args:
        boxes (np.ndarray): Bounding box coordinates in format [x, y, width, height].
        cls (np.ndarray): Class indices.
        names (dict, optional): Dictionary mapping class indices to class names.
        save_dir (Path, optional): Directory to save the plot.
        on_plot (Callable, optional): Function to call after plot is saved.
    """
    import matplotlib.pyplot as plt  # scope for faster 'import ultralytics'
    import pandas
    from matplotlib.colors import LinearSegmentedColormap

    # Filter matplotlib>=3.7.2 warning
    warnings.filterwarnings("ignore", category=UserWarning, message="The figure layout has changed to tight")
    warnings.filterwarnings("ignore", category=FutureWarning)

    # Plot dataset labels
    LOGGER.info(f"Plotting labels to {save_dir / 'labels.jpg'}... ")
    nc = int(cls.max() + 1)  # number of classes
    boxes = boxes[:1000000]  # limit to 1M boxes
    x = pandas.DataFrame(boxes, columns=["x", "y", "width", "height"])

    try:  # Seaborn correlogram
        import seaborn

        seaborn.pairplot(x, corner=True, diag_kind="auto", kind="hist", diag_kws=dict(bins=50), plot_kws=dict(pmax=0.9))
        plt.savefig(save_dir / "labels_correlogram.jpg", dpi=200)
        plt.close()
    except ImportError:
        pass  # Skip if seaborn is not installed

    # Matplotlib labels
    subplot_3_4_color = LinearSegmentedColormap.from_list("white_blue", ["white", "blue"])
    ax = plt.subplots(2, 2, figsize=(8, 8), tight_layout=True)[1].ravel()
    y = ax[0].hist(cls, bins=np.linspace(0, nc, nc + 1) - 0.5, rwidth=0.8)
    for i in range(nc):
        y[2].patches[i].set_color([x / 255 for x in colors(i)])
    ax[0].set_ylabel("instances")
    if 0 < len(names) < 30:
        ax[0].set_xticks(range(len(names)))
        ax[0].set_xticklabels(list(names.values()), rotation=90, fontsize=10)
    else:
        ax[0].set_xlabel("classes")
    boxes = np.column_stack([0.5 - boxes[:, 2:4] / 2, 0.5 + boxes[:, 2:4] / 2]) * 1000
    img = Image.fromarray(np.ones((1000, 1000, 3), dtype=np.uint8) * 255)
    for cls, box in zip(cls[:500], boxes[:500]):
        ImageDraw.Draw(img).rectangle(box, width=1, outline=colors(cls))  # plot
    ax[1].imshow(img)
    ax[1].axis("off")

    ax[2].hist2d(x["x"], x["y"], bins=50, cmap=subplot_3_4_color)
    ax[2].set_xlabel("x")
    ax[2].set_ylabel("y")
    ax[3].hist2d(x["width"], x["height"], bins=50, cmap=subplot_3_4_color)
    ax[3].set_xlabel("width")
    ax[3].set_ylabel("height")
    for a in {0, 1, 2, 3}:
        for s in {"top", "right", "left", "bottom"}:
            ax[a].spines[s].set_visible(False)

    fname = save_dir / "labels.jpg"
    plt.savefig(fname, dpi=200)
    plt.close()
    if on_plot:
        on_plot(fname)


def save_one_box(
    xyxy,
    im,
    file: Path = Path("im.jpg"),
    gain: float = 1.02,
    pad: int = 10,
    square: bool = False,
    BGR: bool = False,
    save: bool = True,
):
    """
    Save image crop as {file} with crop size multiple {gain} and {pad} pixels. Save and/or return crop.

    This function takes a bounding box and an image, and then saves a cropped portion of the image according
    to the bounding box. Optionally, the crop can be squared, and the function allows for gain and padding
    adjustments to the bounding box.

    Args:
        xyxy (torch.Tensor | list): A tensor or list representing the bounding box in xyxy format.
        im (np.ndarray): The input image.
        file (Path, optional): The path where the cropped image will be saved.
        gain (float, optional): A multiplicative factor to increase the size of the bounding box.
        pad (int, optional): The number of pixels to add to the width and height of the bounding box.
        square (bool, optional): If True, the bounding box will be transformed into a square.
        BGR (bool, optional): If True, the image will be returned in BGR format, otherwise in RGB.
        save (bool, optional): If True, the cropped image will be saved to disk.

    Returns:
        (np.ndarray): The cropped image.

    Examples:
        >>> from ultralytics.utils.plotting import save_one_box
        >>> xyxy = [50, 50, 150, 150]
        >>> im = cv2.imread("image.jpg")
        >>> cropped_im = save_one_box(xyxy, im, file="cropped.jpg", square=True)
    """
    if not isinstance(xyxy, torch.Tensor):  # may be list
        xyxy = torch.stack(xyxy)
    b = ops.xyxy2xywh(xyxy.view(-1, 4))  # boxes
    if square:
        b[:, 2:] = b[:, 2:].max(1)[0].unsqueeze(1)  # attempt rectangle to square
    b[:, 2:] = b[:, 2:] * gain + pad  # box wh * gain + pad
    xyxy = ops.xywh2xyxy(b).long()
    xyxy = ops.clip_boxes(xyxy, im.shape)
    grayscale = im.shape[2] == 1  # grayscale image
    crop = im[int(xyxy[0, 1]) : int(xyxy[0, 3]), int(xyxy[0, 0]) : int(xyxy[0, 2]), :: (1 if BGR or grayscale else -1)]
    if save:
        file.parent.mkdir(parents=True, exist_ok=True)  # make directory
        f = str(increment_path(file).with_suffix(".jpg"))
        # cv2.imwrite(f, crop)  # save BGR, https://github.com/ultralytics/yolov5/issues/7007 chroma subsampling issue
        crop = crop.squeeze(-1) if grayscale else crop[..., ::-1] if BGR else crop
        Image.fromarray(crop).save(f, quality=95, subsampling=0)  # save RGB
    return crop


@threaded
def plot_images(
    labels: Dict[str, Any],
    images: Union[torch.Tensor, np.ndarray] = np.zeros((0, 3, 640, 640), dtype=np.float32),
    paths: Optional[List[str]] = None,
    fname: str = "images.jpg",
    names: Optional[Dict[int, str]] = None,
    on_plot: Optional[Callable] = None,
    max_size: int = 1920,
    max_subplots: int = 16,
    save: bool = True,
    conf_thres: float = 0.25,
) -> Optional[np.ndarray]:
    """
    Plot image grid with labels, bounding boxes, masks, and keypoints.

    Args:
        labels (Dict[str, Any]): Dictionary containing detection data with keys like 'cls', 'bboxes', 'conf', 'masks', 'keypoints', 'batch_idx', 'img'.
        images (torch.Tensor | np.ndarray]): Batch of images to plot. Shape: (batch_size, channels, height, width).
        paths (Optional[List[str]]): List of file paths for each image in the batch.
        fname (str): Output filename for the plotted image grid.
        names (Optional[Dict[int, str]]): Dictionary mapping class indices to class names.
        on_plot (Optional[Callable]): Optional callback function to be called after saving the plot.
        max_size (int): Maximum size of the output image grid.
        max_subplots (int): Maximum number of subplots in the image grid.
        save (bool): Whether to save the plotted image grid to a file.
        conf_thres (float): Confidence threshold for displaying detections.

    Returns:
        (np.ndarray): Plotted image grid as a numpy array if save is False, None otherwise.

    Note:
        This function supports both tensor and numpy array inputs. It will automatically
        convert tensor inputs to numpy arrays for processing.
    """
    for k in {"cls", "bboxes", "conf", "masks", "keypoints", "batch_idx", "images"}:
        if k not in labels:
            continue
        if k == "cls" and labels[k].ndim == 2:
            labels[k] = labels[k].squeeze(1)  # squeeze if shape is (n, 1)
        if isinstance(labels[k], torch.Tensor):
            labels[k] = labels[k].cpu().numpy()

    cls = labels.get("cls", np.zeros(0, dtype=np.int64))
    batch_idx = labels.get("batch_idx", np.zeros(cls.shape, dtype=np.int64))
    bboxes = labels.get("bboxes", np.zeros(0, dtype=np.float32))
    confs = labels.get("conf", None)
    masks = labels.get("masks", np.zeros(0, dtype=np.uint8))
    kpts = labels.get("keypoints", np.zeros(0, dtype=np.float32))
    images = labels.get("img", images)  # default to input images

    if len(images) and isinstance(images, torch.Tensor):
        images = images.cpu().float().numpy()
    if images.shape[1] > 3:
        images = images[:, :3]  # crop multispectral images to first 3 channels

    bs, _, h, w = images.shape  # batch size, _, height, width
    bs = min(bs, max_subplots)  # limit plot images
    ns = np.ceil(bs**0.5)  # number of subplots (square)
    if np.max(images[0]) <= 1:
        images *= 255  # de-normalise (optional)

    # Build Image
    mosaic = np.full((int(ns * h), int(ns * w), 3), 255, dtype=np.uint8)  # init
    for i in range(bs):
        x, y = int(w * (i // ns)), int(h * (i % ns))  # block origin
        mosaic[y : y + h, x : x + w, :] = images[i].transpose(1, 2, 0)

    # Resize (optional)
    scale = max_size / ns / max(h, w)
    if scale < 1:
        h = math.ceil(scale * h)
        w = math.ceil(scale * w)
        mosaic = cv2.resize(mosaic, tuple(int(x * ns) for x in (w, h)))

    # Annotate
    fs = int((h + w) * ns * 0.01)  # font size
    fs = max(fs, 18)  # ensure that the font size is large enough to be easily readable.
    annotator = Annotator(mosaic, line_width=round(fs / 10), font_size=fs, pil=True, example=str(names))
    for i in range(bs):
        x, y = int(w * (i // ns)), int(h * (i % ns))  # block origin
        annotator.rectangle([x, y, x + w, y + h], None, (255, 255, 255), width=2)  # borders
        if paths:
            annotator.text([x + 5, y + 5], text=Path(paths[i]).name[:40], txt_color=(220, 220, 220))  # filenames
        if len(cls) > 0:
            idx = batch_idx == i
            classes = cls[idx].astype("int")
            labels = confs is None

            if len(bboxes):
                boxes = bboxes[idx]
                conf = confs[idx] if confs is not None else None  # check for confidence presence (label vs pred)
                if len(boxes):
                    if boxes[:, :4].max() <= 1.1:  # if normalized with tolerance 0.1
                        boxes[..., [0, 2]] *= w  # scale to pixels
                        boxes[..., [1, 3]] *= h
                    elif scale < 1:  # absolute coords need scale if image scales
                        boxes[..., :4] *= scale
                boxes[..., 0] += x
                boxes[..., 1] += y
                is_obb = boxes.shape[-1] == 5  # xywhr
                # TODO: this transformation might be unnecessary
                boxes = ops.xywhr2xyxyxyxy(boxes) if is_obb else ops.xywh2xyxy(boxes)
                for j, box in enumerate(boxes.astype(np.int64).tolist()):
                    c = classes[j]
                    color = colors(c)
                    c = names.get(c, c) if names else c
                    if labels or conf[j] > conf_thres:
                        label = f"{c}" if labels else f"{c} {conf[j]:.1f}"
                        annotator.box_label(box, label, color=color)

            elif len(classes):
                for c in classes:
                    color = colors(c)
                    c = names.get(c, c) if names else c
                    annotator.text([x, y], f"{c}", txt_color=color, box_color=(64, 64, 64, 128))

            # Plot keypoints
            if len(kpts):
                kpts_ = kpts[idx].copy()
                if len(kpts_):
                    if kpts_[..., 0].max() <= 1.01 or kpts_[..., 1].max() <= 1.01:  # if normalized with tolerance .01
                        kpts_[..., 0] *= w  # scale to pixels
                        kpts_[..., 1] *= h
                    elif scale < 1:  # absolute coords need scale if image scales
                        kpts_ *= scale
                kpts_[..., 0] += x
                kpts_[..., 1] += y
                for j in range(len(kpts_)):
                    if labels or conf[j] > conf_thres:
                        annotator.kpts(kpts_[j], conf_thres=conf_thres)

            # Plot masks
            if len(masks):
                if idx.shape[0] == masks.shape[0]:  # overlap_masks=False
                    image_masks = masks[idx]
                else:  # overlap_masks=True
                    image_masks = masks[[i]]  # (1, 640, 640)
                    nl = idx.sum()
                    index = np.arange(nl).reshape((nl, 1, 1)) + 1
                    image_masks = np.repeat(image_masks, nl, axis=0)
                    image_masks = np.where(image_masks == index, 1.0, 0.0)

                im = np.asarray(annotator.im).copy()
                for j in range(len(image_masks)):
                    if labels or conf[j] > conf_thres:
                        color = colors(classes[j])
                        mh, mw = image_masks[j].shape
                        if mh != h or mw != w:
                            mask = image_masks[j].astype(np.uint8)
                            mask = cv2.resize(mask, (w, h))
                            mask = mask.astype(bool)
                        else:
                            mask = image_masks[j].astype(bool)
                        try:
                            im[y : y + h, x : x + w, :][mask] = (
                                im[y : y + h, x : x + w, :][mask] * 0.4 + np.array(color) * 0.6
                            )
                        except Exception:
                            pass
                annotator.fromarray(im)
    if not save:
        return np.asarray(annotator.im)
    annotator.im.save(fname)  # save
    if on_plot:
        on_plot(fname)


@plt_settings()
def plot_results(
    file: str = "path/to/results.csv",
    dir: str = "",
    segment: bool = False,
    pose: bool = False,
    classify: bool = False,
    on_plot: Optional[Callable] = None,
):
    """
    Plot training results from a results CSV file. The function supports various types of data including segmentation,
    pose estimation, and classification. Plots are saved as 'results.png' in the directory where the CSV is located.

    Args:
        file (str, optional): Path to the CSV file containing the training results.
        dir (str, optional): Directory where the CSV file is located if 'file' is not provided.
        segment (bool, optional): Flag to indicate if the data is for segmentation.
        pose (bool, optional): Flag to indicate if the data is for pose estimation.
        classify (bool, optional): Flag to indicate if the data is for classification.
        on_plot (callable, optional): Callback function to be executed after plotting. Takes filename as an argument.

    Examples:
        >>> from ultralytics.utils.plotting import plot_results
        >>> plot_results("path/to/results.csv", segment=True)
    """
    import matplotlib.pyplot as plt  # scope for faster 'import ultralytics'
    import pandas as pd
    from scipy.ndimage import gaussian_filter1d

    save_dir = Path(file).parent if file else Path(dir)
    if classify:
        fig, ax = plt.subplots(2, 2, figsize=(6, 6), tight_layout=True)
        index = [2, 5, 3, 4]
    elif segment:
        fig, ax = plt.subplots(2, 8, figsize=(18, 6), tight_layout=True)
        index = [2, 3, 4, 5, 6, 7, 10, 11, 14, 15, 16, 17, 8, 9, 12, 13]
    elif pose:
        fig, ax = plt.subplots(2, 9, figsize=(21, 6), tight_layout=True)
        index = [2, 3, 4, 5, 6, 7, 8, 11, 12, 15, 16, 17, 18, 19, 9, 10, 13, 14]
    else:
        fig, ax = plt.subplots(2, 5, figsize=(12, 6), tight_layout=True)
        index = [2, 3, 4, 5, 6, 9, 10, 11, 7, 8]
    ax = ax.ravel()
    files = list(save_dir.glob("results*.csv"))
    assert len(files), f"No results.csv files found in {save_dir.resolve()}, nothing to plot."
    for f in files:
        try:
            data = pd.read_csv(f)
            s = [x.strip() for x in data.columns]
            x = data.values[:, 0]
            for i, j in enumerate(index):
                y = data.values[:, j].astype("float")
                # y[y == 0] = np.nan  # don't show zero values
                ax[i].plot(x, y, marker=".", label=f.stem, linewidth=2, markersize=8)  # actual results
                ax[i].plot(x, gaussian_filter1d(y, sigma=3), ":", label="smooth", linewidth=2)  # smoothing line
                ax[i].set_title(s[j], fontsize=12)
                # if j in {8, 9, 10}:  # share train and val loss y axes
                #     ax[i].get_shared_y_axes().join(ax[i], ax[i - 5])
        except Exception as e:
            LOGGER.error(f"Plotting error for {f}: {e}")
    ax[1].legend()
    fname = save_dir / "results.png"
    fig.savefig(fname, dpi=200)
    plt.close()
    if on_plot:
        on_plot(fname)


def plt_color_scatter(v, f, bins: int = 20, cmap: str = "viridis", alpha: float = 0.8, edgecolors: str = "none"):
    """
    Plot a scatter plot with points colored based on a 2D histogram.

    Args:
        v (array-like): Values for the x-axis.
        f (array-like): Values for the y-axis.
        bins (int, optional): Number of bins for the histogram.
        cmap (str, optional): Colormap for the scatter plot.
        alpha (float, optional): Alpha for the scatter plot.
        edgecolors (str, optional): Edge colors for the scatter plot.

    Examples:
        >>> v = np.random.rand(100)
        >>> f = np.random.rand(100)
        >>> plt_color_scatter(v, f)
    """
    import matplotlib.pyplot as plt  # scope for faster 'import ultralytics'

    # Calculate 2D histogram and corresponding colors
    hist, xedges, yedges = np.histogram2d(v, f, bins=bins)
    colors = [
        hist[
            min(np.digitize(v[i], xedges, right=True) - 1, hist.shape[0] - 1),
            min(np.digitize(f[i], yedges, right=True) - 1, hist.shape[1] - 1),
        ]
        for i in range(len(v))
    ]

    # Scatter plot
    plt.scatter(v, f, c=colors, cmap=cmap, alpha=alpha, edgecolors=edgecolors)


def plot_tune_results(csv_file: str = "tune_results.csv"):
    """
    Plot the evolution results stored in a 'tune_results.csv' file. The function generates a scatter plot for each key
    in the CSV, color-coded based on fitness scores. The best-performing configurations are highlighted on the plots.

    Args:
        csv_file (str, optional): Path to the CSV file containing the tuning results.

    Examples:
        >>> plot_tune_results("path/to/tune_results.csv")
    """
    import matplotlib.pyplot as plt  # scope for faster 'import ultralytics'
    import pandas as pd
    from scipy.ndimage import gaussian_filter1d

    def _save_one_file(file):
        """Save one matplotlib plot to 'file'."""
        plt.savefig(file, dpi=200)
        plt.close()
        LOGGER.info(f"Saved {file}")

    # Scatter plots for each hyperparameter
    csv_file = Path(csv_file)
    data = pd.read_csv(csv_file)
    num_metrics_columns = 1
    keys = [x.strip() for x in data.columns][num_metrics_columns:]
    x = data.values
    fitness = x[:, 0]  # fitness
    j = np.argmax(fitness)  # max fitness index
    n = math.ceil(len(keys) ** 0.5)  # columns and rows in plot
    plt.figure(figsize=(10, 10), tight_layout=True)
    for i, k in enumerate(keys):
        v = x[:, i + num_metrics_columns]
        mu = v[j]  # best single result
        plt.subplot(n, n, i + 1)
        plt_color_scatter(v, fitness, cmap="viridis", alpha=0.8, edgecolors="none")
        plt.plot(mu, fitness.max(), "k+", markersize=15)
        plt.title(f"{k} = {mu:.3g}", fontdict={"size": 9})  # limit to 40 characters
        plt.tick_params(axis="both", labelsize=8)  # Set axis label size to 8
        if i % n != 0:
            plt.yticks([])
    _save_one_file(csv_file.with_name("tune_scatter_plots.png"))

    # Fitness vs iteration
    x = range(1, len(fitness) + 1)
    plt.figure(figsize=(10, 6), tight_layout=True)
    plt.plot(x, fitness, marker="o", linestyle="none", label="fitness")
    plt.plot(x, gaussian_filter1d(fitness, sigma=3), ":", label="smoothed", linewidth=2)  # smoothing line
    plt.title("Fitness vs Iteration")
    plt.xlabel("Iteration")
    plt.ylabel("Fitness")
    plt.grid(True)
    plt.legend()
    _save_one_file(csv_file.with_name("tune_fitness.png"))


def feature_visualization(x, module_type: str, stage: int, n: int = 32, save_dir: Path = Path("runs/detect/exp")):
    """
    Visualize feature maps of a given model module during inference.

    Args:
        x (torch.Tensor): Features to be visualized.
        module_type (str): Module type.
        stage (int): Module stage within the model.
        n (int, optional): Maximum number of feature maps to plot.
        save_dir (Path, optional): Directory to save results.
    """
    import matplotlib.pyplot as plt  # scope for faster 'import ultralytics'

    for m in {"Detect", "Segment", "Pose", "Classify", "OBB", "RTDETRDecoder"}:  # all model heads
        if m in module_type:
            return
    if isinstance(x, torch.Tensor):
        _, channels, height, width = x.shape  # batch, channels, height, width
        if height > 1 and width > 1:
            f = save_dir / f"stage{stage}_{module_type.rsplit('.', 1)[-1]}_features.png"  # filename

            blocks = torch.chunk(x[0].cpu(), channels, dim=0)  # select batch index 0, block by channels
            n = min(n, channels)  # number of plots
            _, ax = plt.subplots(math.ceil(n / 8), 8, tight_layout=True)  # 8 rows x n/8 cols
            ax = ax.ravel()
            plt.subplots_adjust(wspace=0.05, hspace=0.05)
            for i in range(n):
                ax[i].imshow(blocks[i].squeeze())  # cmap='gray'
                ax[i].axis("off")

            LOGGER.info(f"Saving {f}... ({n}/{channels})")
            plt.savefig(f, dpi=300, bbox_inches="tight")
            plt.close()
            np.save(str(f.with_suffix(".npy")), x[0].cpu().numpy())  # npy save


