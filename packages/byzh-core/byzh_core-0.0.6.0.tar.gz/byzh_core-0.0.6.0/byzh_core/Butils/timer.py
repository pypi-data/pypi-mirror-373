import time
class B_Timer:
    def __init__(self):
        '''
        >>> with B_Timer():
        >>>     ...
        '''
        self.start_time = 0
        self.end_time = 0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        print(f"[Timer] cost: {self.end_time - self.start_time:.4f}s")

if __name__ == '__main__':
    with B_Timer():
        time.sleep(2)
