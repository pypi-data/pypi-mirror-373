import os
import sys
import time
import json
import shlex
import select
import logging
import threading
import subprocess as sp
import numpy as np

from .utils import is_jetson

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

_BAD_SIGS = (
    b"Impossible to convert between the formats",
    b"Failed to inject frame into filter network",
    b"Function not implemented",
    b"No device available for decoder",
    b"Invalid data found when processing input",
)

_ALLOWED_CODECS = {"h264", "hevc", "mpeg4", "mpeg2video", "vp8", "vp9"}

# ---------------------------
# Tools for ffmpeg init
# ---------------------------
def has_decoder(name: str) -> bool:
    try:
        out = sp.check_output(["ffmpeg", "-hide_banner", "-decoders"], stderr=sp.STDOUT)
        return (name.encode() + b" ") in out or (b" " + name.encode() + b" ") in out
    except Exception:
        return False


def _run(cmd, timeout=6.0):
    """
    Conduct subprocess with stderr discarded to prevent noise interference in parsing.
    return (returncode:int, stdout:str)
    """
    env = os.environ.copy()
    # Avoid EGL error when no X on Jetson/container
    env.setdefault("EGL_PLATFORM", "surfaceless")
    p = sp.run(
        cmd,
        stdout=sp.PIPE,
        stderr=sp.DEVNULL,   # ignore stderr like 'No EGL Display'
        env=env,
        timeout=timeout,
        check=False,
    )
    out = p.stdout.decode("utf-8", "ignore")
    return p.returncode, out


def probe_stream_info(url: str, timeout: float = 6.0):
    """
    Get stream info from RTSP URL using ffprobe.
    Parse JSON output first; if fails, fallback to text parsing.
    Return (codec:str|None, width:int|None, height:int|None).
    """
    # JSON parsing (most reliable)
    cmd = [
        "ffprobe", "-v", "quiet",
        "-rtsp_transport", "tcp", "-rtsp_flags", "prefer_tcp",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height",
        "-of", "json", url,
    ]
    rc, out = _run(cmd, timeout=timeout)
    if rc == 0 and out.strip():
        try:
            data = json.loads(out)
            streams = data.get("streams") or []
            if streams:
                s = streams[0]
                codec = (s.get("codec_name") or "").lower() or None
                w = s.get("width") or None
                h = s.get("height") or None
                if codec and codec in _ALLOWED_CODECS:
                    return codec, int(w) if w else None, int(h) if h else None
        except Exception:
            pass

    # Fallback to text parsing
    # This may be unreliable due to possible noise lines in output
    # Use nk=1:nw=1 to text output, get the last valid codec
    cmd_fb = [
        "ffprobe", "-v", "error",
        "-rtsp_transport", "tcp", "-rtsp_flags", "prefer_tcp",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height",
        "-of", "default=nk=1:nw=1", url,
    ]
    rc, out = _run(cmd_fb, timeout=timeout)
    if rc == 0 and out:
        lines = [x.strip().lower() for x in out.splitlines() if x.strip()]
        # Try to find codec first since it may have noise lines
        codec = next((x for x in lines if x in _ALLOWED_CODECS), None)
        
        def _to_int(s):
            try: return int(s)
            except: return None

        # Width, height may be in the last two lines (but double-check)
        w = _to_int(lines[-2]) if len(lines) >= 2 else None
        h = _to_int(lines[-1]) if len(lines) >= 1 else None
        if w is None or h is None:
            ints = [ _to_int(x) for x in lines ]
            ints = [i for i in ints if i is not None ]
            if len(ints) >= 2:
                w, h = ints[-2], ints[-1]
        return codec, w, h
    
    return None, None, None


# ---------------------------
# Tools for ffmpeg subprocess
# ---------------------------
def drain_stderr(proc):
    """
    Read and discard ffmpeg stderr to avoid blocking.
    Also print messages for debugging.
    """
    for line in iter(proc.stderr.readline, b''):
        try:
            sys.stderr.write("[ffmpeg] " + line.decode("utf-8", "ignore"))
        except Exception:
            pass


def build_cmd(rtsp_url, w, h, fps=5, hwaccel=True, probe_timeout=5.0):
    w = int(w); h = int(h); fps = int(fps)
    
    # Probe the codec safely (in case ffprobe not exist/timeout/abnormal)
    codec = None
    try:
        codec, _, _ = probe_stream_info(rtsp_url, timeout=probe_timeout)
    except FileNotFoundError:
        _logger.warning("ffprobe not exist; skip codec probe, use software decode.")  
    except Exception as e:
        _logger.warning(f"ffprobe failed: {e}; skip codec probe, use software decode.")

    # ---------------- Jetson (nvv4l2dec) ----------------
    if is_jetson():
        if hwaccel:
            # Try nvv4l2dec (NVDIA hardware decoder)
            nvmap = {"h264": "h264_nvv4l2dec", "avc": "h264_nvv4l2dec",
                     "hevc": "hevc_nvv4l2dec", "h265": "hevc_nvv4l2dec"}
            nvdec = nvmap.get((codec or "").lower())
            if nvdec and has_decoder(nvdec):
                return [
                    "ffmpeg",
                    "-v", "error",
                    "-hide_banner",
                    "-nostats",
                    "-rtsp_transport", "tcp",
                    "-rtsp_flags", "prefer_tcp",
                    "-use_wallclock_as_timestamps", "1",
                    "-c:v", nvdec,
                    "-i", rtsp_url,
                    "-an", "-sn", "-dn",
                    "-sws_flags", "fast_bilinear",
                    "-vf", f"fps={fps},scale={w}:{h},format=bgr24",
                    "-pix_fmt", "bgr24",
                    "-vsync", "0",
                    "-f", "rawvideo", "pipe:1",
                ], codec
            
        # Jetson soft decode (or fallback)
        return [
            "ffmpeg",
            "-v", "error",
            "-hide_banner",
            "-nostats",
            "-rtsp_transport", "tcp",
            "-rtsp_flags", "prefer_tcp",
            "-use_wallclock_as_timestamps", "1",
            "-i", rtsp_url,
            "-an", "-sn", "-dn",
            "-sws_flags", "fast_bilinear",
            "-vf", f"fps={fps},scale={w}:{h},format=bgr24",
            "-pix_fmt", "bgr24",
            "-vsync", "0",
            "-f", "rawvideo", "pipe:1",
        ], codec
    
    # ---------------- Raspberry Pi (V4L2-request + DRM PRIME) ----------------
    else:
        # RPi5 only support hevc/h265 hardware decode
        if hwaccel and codec in {"hevc", "h265"}:
            return [
                "ffmpeg",
                "-v", "error",   # logging level, does not affect data stream
                "-hide_banner",  # hide version info
                "-nostats",      # no stats to reduce I/O overhead

                # ===== RTSP input options =====
                "-rtsp_transport", "tcp",
                "-rtsp_flags", "prefer_tcp",

                # ==== timestamp options =====
                "-use_wallclock_as_timestamps", "1",
                # → Use system wallclock as timestamps to avoid issues with non-monotonic input timestamps

                # ===== hw decode and hw frame format =====
                "-hwaccel", "drm",
                "-hwaccel_output_format", "drm_prime",
                # → Use DRM PRIME path for hwaccel (RPi uses V4L2-request)
                #   Each decoded frame is a "GPU/driver DMABUF" (drm_prime), not in CPU memory
                
                # If your system has multiple DRM devices, you may need to adjust the path
                # (e.g., /dev/dri/renderD128, /dev/dri/card0, /dev/dri/card1, etc.)
                # (check with `ls /dev/dri/` or `v4l2-ctl --list-devices`)
                # "-init_hw_device", "drm=drm:/dev/dri/renderD128",
                # "-filter_hw_device", "drm",

                "-i", rtsp_url,

                # ===== close unwanted streams =====
                "-an", "-sn", "-dn",  # not process audio/subtitle/data streams

                # ===== swscale global flags (applied to scale filter) =====
                "-sws_flags", "fast_bilinear",  
                # → CPU scaling algorithm (speed over quality)

                # ===== filter graph ===== 
                "-vf", f"fps={fps},hwdownload,format=nv12,scale={w}:{h},format=bgr24",
                # fps=5
                #   Adjust output frame rate to 5 fps, reducing CPU load from DRM frame fetching
                # hwdownload
                #   Copy each frame from GPU/driver DMABUF to CPU memory
                # format=nv12
                #   Specify the pixel format of the downloaded frame to NV12 (Y + interleaved UV)
                #   This is the fastest for the subsequent scaling
                # scale=OUT_W:OUT_H
                #   Scale on CPU with swscale (uses fast_bilinear as above)
                # format=bgr24
                #   Finally convert pixel format to BGR 8:8:8, most compatible with OpenCV

                "-pix_fmt", "bgr24",
                # → Specify pixel format of output frames.
                #   Since we output rawvideo, this determines the byte layout of each frame.

                "-vsync", "0",
                # "-fps_mode", "passthrough",
                # → Not do any frame dropping/duplication, output frames as they come.

                # ===== output (to stdout) =====
                "-f", "rawvideo", "pipe:1",
                # → Use rawvideo muxer to output raw frames to stdout
            ], codec
        
        # soft decode (or fallback)
        return [
            "ffmpeg",
            "-v", "error", "-hide_banner", "-nostats",
            "-rtsp_transport", "tcp", "-rtsp_flags", "prefer_tcp",
            "-use_wallclock_as_timestamps", "1",
            "-i", rtsp_url,
            "-an", "-sn", "-dn",
            "-sws_flags", "fast_bilinear", 
            "-vf", f"fps={fps},scale={w}:{h},format=bgr24", 
            "-pix_fmt", "bgr24",
            "-fps_mode", "passthrough",
            "-f", "rawvideo", "pipe:1",
        ], codec
    

class FFmpegCapture:
    """
    Adapter that mimics cv2.VideoCapture interface:
      - open(rtsp) / isOpened() / read() / release() / get(prop)
      - Built-in hardware decode → software decode fallback
      - Reads raw BGR frames from stdout
    """
    is_ffmpeg = True

    def __init__(
        self, 
        width, 
        height, 
        fps=5, 
        hwaccel=True,
        fallback=False,  # allow fallback to software decode if hwaccel fails
        first_frame_timeout=5.0, 
        frame_timeout=3.0
    ):
        self.w, self.h = int(width), int(height)
        self.fps = int(fps)
        self.hwaccel = bool(hwaccel)
        self.fallback = bool(fallback)
        self.first_frame_timeout = float(first_frame_timeout)
        self.frame_timeout = float(frame_timeout)

        self._url = None
        self._proc = None
        self._opened = False
        self._frame_size = self.w * self.h * 3  # bgr24
        self._buf = bytearray(self._frame_size)
        self._mv = memoryview(self._buf)

    def _start_proc(self, cmd):
        print("[cmd]", " ".join(shlex.quote(x) for x in cmd))
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, bufsize=10**8)  # 10**8
        threading.Thread(target=drain_stderr, args=(p,), daemon=True).start()
        return p
    
    def _try_read_exact(self, proc, timeout_sec=1.5):
        """
        Wait for stdout to be readable and try to read exactly one frame; 
        return False on failure.
        """
        got = 0
        fd  = proc.stdout.fileno()
        deadline = time.time() + timeout_sec
        while got < self._frame_size:
            if time.time() > deadline:
                return False
            # Wait for data
            r, _, _ = select.select([fd], [], [], 0.05)
            if not r:
                if proc.poll() is not None:  # subprocess exited
                    print("[main] ffmpeg exited with code", proc.returncode)
                    return False
                continue
            n = proc.stdout.readinto(self._mv[got:])
            if not n:
                if proc.poll() is not None:
                    return False
                continue
            got += n
        return True
    
    def open(self, rtsp_url):
        self.release()
        self._url = rtsp_url

        # try hwaccel first
        cmd, self.codec = build_cmd(rtsp_url, self.w, self.h, self.fps, hwaccel=self.hwaccel)
        self._proc = self._start_proc(cmd)
        if not self._try_read_exact(self._proc, self.first_frame_timeout):
            # Failed to read first frame, or process exited
            try: self._proc.kill()
            except: pass

            if not (self.fallback and self.hwaccel):
                self._proc = None
                self._opened = False
                return False
            
            # try software decode if specified hwaccel but failed and fallback allowed
            cmd, self.codec = build_cmd(rtsp_url, self.w, self.h, self.fps, hwaccel=False)
            self._proc = self._start_proc(cmd)
            if not self._try_read_exact(self._proc, self.first_frame_timeout):
                try: self._proc.kill()
                except: pass
                self._proc = None
                self._opened = False
                return False

        self._opened = True
        return True

    def isOpened(self):
        return bool(self._proc and self._proc.poll() is None and self._opened)
    
    def read(self):
        """
        Return (True, frame) or (False, None). 
        On failure, do not raise exception to allow upper layer to reconnect.
        """
        p = self._proc
        if not self.isOpened():
            return False, None
        ok = self._try_read_exact(p, self.frame_timeout)
        if not ok:
            return False, None
        frame = np.frombuffer(self._buf, dtype=np.uint8).reshape((self.h, self.w, 3))
        return True, frame.copy()
    
    def release(self):
        if self._proc:
            try: self._proc.terminate()
            except: pass
            self._proc = None
        self._opened = False

    def get(self, prop):
        """Simulate cv2.VideoCapture.get() for a few properties."""
        try:
            import cv2
        except ImportError:
            return 0.0
        if prop == cv2.CAP_PROP_FRAME_WIDTH:  return float(self.w)
        if prop == cv2.CAP_PROP_FRAME_HEIGHT: return float(self.h)
        if prop == cv2.CAP_PROP_FPS:          return float(self.fps)
        if prop == cv2.CAP_PROP_FOURCC:       return float(cv2.VideoWriter_fourcc(*self.codec)) if self.codec else 0.0
        return 0.0