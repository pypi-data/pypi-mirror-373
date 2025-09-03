import time
from typing import Optional

import kp

class KneronDevice:
    def __init__(
        self, 
        usb_port_id: Optional[int] = None,
        platform: str = "720",
        timeout: int = 5000  # ms
    ):
        self.usb_port_id  = usb_port_id
        self.timeout_ms   = timeout
        self.platform     = platform
        try:
            self.product_id   = int(getattr(kp.ProductId, f"KP_DEVICE_KL{platform}"))
        except AttributeError:
            raise ValueError(f"Unsupported platform: {platform}. Supported platforms are: '720', '520', etc.")

        self.device_group         = None
        self.model_nef_descriptor = None
        self._check_port_id(platform)
    
    def _check_port_id(self, platform: str):
        device_list = self.scan_devices()
        if self.usb_port_id is not None:
            # 如果已經有 port_id，則檢查是否存在於掃描的設備中
            if not any(device.usb_port_id == self.usb_port_id 
                       for device in device_list):
                raise ValueError(f"Port ID {self.usb_port_id} not found in scanned devices.")
        else:
            # 如果沒有 port_id，則根據 platform 找到對應的設備
            for device in device_list:
                if device.product_id == self.product_id:
                    self.usb_port_id = device.usb_port_id
                    break
            
            if self.usb_port_id is None:
                raise ValueError(f"No device found for platform {platform}")

    @staticmethod  
    def scan_devices():
        return kp.core.scan_devices().device_descriptor_list
            
    def connect(self):
        try:
            self.device_group = kp.core.connect_devices([self.usb_port_id])
            kp.core.set_timeout(self.device_group, self.timeout_ms)
        except kp.ApiKPException as e:
            raise RuntimeError(f"Failed to connect to device: {e}")

    def info(self):
        return next(d for d in self.scan_devices() if d.usb_port_id == self.usb_port_id)
    
    def is_usb_speed_high(self):
        info = self.info()
        return (info.link_speed == kp.UsbSpeed.KP_USB_SPEED_HIGH or
                info.link_speed == kp.UsbSpeed.KP_USB_SPEED_SUPER)
    
    def load_firmware_from_file(self, scpu_fw_path: str, ncpu_fw_path: str):
        if self.device_group is None:
            raise RuntimeError("Device not connected.")
        
        if self.platform == '720':
            print("KL720 already has firmware loaded, skipping.")
            return
        
        try:
            kp.core.load_firmware_from_file(self.device_group, scpu_fw_path, ncpu_fw_path)
        except kp.ApiKPException as e:
            raise RuntimeError(f"Failed to load firmware: {e}")
        
    def load_model_from_file(self, model_path: str):
        if self.device_group is None:
            raise RuntimeError("Device not connected.")
        
        try:
            self.model_nef_descriptor = kp.core.load_model_from_file(self.device_group, model_path)
        except kp.ApiKPException as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def disconnect(self):
        if self.device_group is not None:
            kp.core.disconnect_devices(self.device_group)
            self.device_group = None
        
    def reset(self):
        kp.core.reset_device(self.device_group)
        # kp.core.disconnect_devices(self.device_group)
        time.sleep(1)               # 等 USB 重新枚舉
        self.connect()