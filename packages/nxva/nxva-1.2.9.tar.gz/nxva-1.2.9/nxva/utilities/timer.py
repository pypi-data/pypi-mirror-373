import time
import torch

# can only decorate on instance method
def timer():
    def decorator(func):
        def wrapper(*args, **kwargs):
            self = args[0]  # 確定其中之一是 `self`
            if hasattr(self, 'verbose') and self.verbose:
                torch.cuda.synchronize()
                start_time = time.time()
                result = func(*args, **kwargs)
                torch.cuda.synchronize()
                end_time = time.time()
                print(f"{func.__name__}: {(end_time - start_time)*1000:.1f} ms")
            else:
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator