import os

def is_jetson():
    """Check if the code is running on an NVIDIA Jetson platform."""
    compat_file_path = "/proc/device-tree/compatible"
    if os.path.isfile(compat_file_path):
        with open(compat_file_path, "r") as file:
            compat_str = file.read()
            return "nvidia" in compat_str and "tegra" in compat_str
    return False