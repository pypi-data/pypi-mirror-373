import time
import contextlib
import numpy as np
import torch

class Profile(contextlib.ContextDecorator):
    """
    YOLOv8 Profile class. Use as a decorator with @Profile() or as a context manager with 'with Profile():'.

    Example:
        ```python
        from ultralytics.utils.ops import Profile

        with Profile(device=device) as dt:
            pass  # slow operation here

        print(dt)  # prints "Elapsed time is 9.5367431640625e-07 s"
        ```
    """

    def __init__(self, t=0.0, device: torch.device = None):
        """
        Initialize the Profile class.

        Args:
            t (float): Initial time. Defaults to 0.0.
            device (torch.device): Devices used for model inference. Defaults to None (cpu).
        """
        self.t = t
        self.device = device
        self.cuda = bool(device and str(device).startswith("cuda"))

    def __enter__(self):
        """Start timing."""
        self.start = self.time()
        return self

    def __exit__(self, type, value, traceback):  # noqa
        """Stop timing."""
        self.dt = self.time() - self.start  # delta-time
        self.t += self.dt  # accumulate dt

    def __str__(self):
        """Returns a human-readable string representing the accumulated elapsed time in the profiler."""
        return f"Elapsed time is {self.t} s"

    def time(self):
        """Get current time."""
        if self.cuda:
            torch.cuda.synchronize(self.device)
        return time.time()

class SpeedCalculator:
    def __init__(self):
        self.speed = []

    def update(self, n, profilers):
        preprocess_time = profilers[0].dt * 1e3 / n
        inference_time = profilers[1].dt * 1e3 / n
        postprocess_time = profilers[2].dt * 1e3 / n
        # print(f"Preprocess: {preprocess_time:.2f} ms")
        # print(f"Inference: {inference_time:.2f} ms")
        # print(f"Postprocess: {postprocess_time:.2f} ms")
        self.speed.append([preprocess_time, inference_time, postprocess_time])

    def compute(self):
        self.speed = np.array(self.speed)
        return np.mean(self.speed, axis=0)

    def empty(self):
        self.speed = []
    
    def print_results(self, title="Speed Analysis Results"):
        """
        Print formatted speed analysis results.
        
        Args:
            title (str): Title for the output. Defaults to "Speed Analysis Results".
        """
        if not self.speed:
            print("No speed data available.")
            return
            
        avg_speeds = self.compute()
        total_time = np.sum(avg_speeds)
        
        print(f"\n{'='*50}")
        print(f"{title:^50}")
        print(f"{'='*50}")
        print(f"{'Stage':<15} {'Average Time (ms)':<20} {'Percentage':<15}")
        print(f"{'-'*50}")
        
        stages = ['Preprocess', 'Inference', 'Postprocess']
        for i, (stage, avg_time) in enumerate(zip(stages, avg_speeds)):
            percentage = (avg_time / total_time) * 100 if total_time > 0 else 0
            print(f"{stage:<15} {avg_time:<20.2f} {percentage:<15.1f}%")
        
        print(f"{'-'*50}")
        print(f"{'Total':<15} {total_time:<20.2f} {'100.0':<15}%")
        print(f"{'='*50}")
        
        # Additional metrics
        fps = 1000 / total_time if total_time > 0 else 0
        print(f"\nPerformance Metrics:")
        print(f"  • FPS: {fps:.2f}")
        print(f"  • Total Time per Image: {total_time:.2f} ms")
        print(f"  • Number of Samples: {len(self.speed)}")
        
        # Detailed statistics
        if len(self.speed) > 1:
            std_devs = np.std(self.speed, axis=0)
            print(f"\nDetailed Statistics (Standard Deviation):")
            for i, (stage, std_dev) in enumerate(zip(stages, std_devs)):
                print(f"  • {stage}: {std_dev:.2f} ms")
    
    def get_summary_dict(self):
        """
        Get speed analysis results as a dictionary.
        
        Returns:
            dict: Dictionary containing speed analysis results.
        """
        if not self.speed:
            return {}
            
        avg_speeds = self.compute()
        total_time = np.sum(avg_speeds)
        
        return {
            'preprocess_time': avg_speeds[0],
            'inference_time': avg_speeds[1], 
            'postprocess_time': avg_speeds[2],
            'total_time': total_time,
            'fps': 1000 / total_time if total_time > 0 else 0,
            'num_samples': len(self.speed),
            'std_devs': np.std(self.speed, axis=0).tolist() if len(self.speed) > 1 else [0, 0, 0]
        }