import sys
import time
import threading
from typing import Iterable

from ..Butils import B_Color, B_Appearance, B_Background


class B_Tqdm:
    def __init__(
            self,
            range: int|Iterable = None,
            prefix: str = 'Processing',
            suffix: str = '',
            length: int = 20,
            fill: str = '█',
    ):
        """
        类似tqdm的进度条
        :param total: 总数
        :param prefix: 前缀
        :param suffix: 后缀
        :param length: 进度条长度(字符), 默认为20个字符长度
        :param fill: 填充字符
        """
        super().__init__()
        self.range = range
        if isinstance(range, Iterable):
            self.range_len = len(range)
        elif isinstance(range, int):
            self.range_len = range
        else:
            self.range_len = None

        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.fill = fill
        self.start_time = 0
        self.current = 0

        self._lock = threading.Lock()

    def _format_time(self, seconds):
        """将秒数转换为mm:ss格式"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f'{minutes:02}:{seconds:02}'

    def update(self, step=1, prefix=None, suffix=None, color:B_Color=B_Color.BLUE, appearance:B_Appearance=None, background:B_Background=None):
        with self._lock:
            pre_show = color.value
            if appearance is not None:
                pre_show += appearance.value
            if background is not None:
                pre_show += background.value

            if self.current == 0:
                self.start_time = time.time()
            if prefix is not None:
                self.prefix = prefix
            if suffix is not None:
                self.suffix = suffix

            # 更新进度
            self.current += step

            # 计算已用时间
            elapsed_time = time.time() - self.start_time
            elapsed_str = self._format_time(elapsed_time)
            # 预估剩余时间
            if self.range_len is not None:
                estimated_time = elapsed_time / self.current * (self.range_len - self.current) if self.current > 0 else 0
                estimated_str = self._format_time(estimated_time)
            # 计算每秒处理的项数
            speed = self.current / elapsed_time if elapsed_time > 0 else 0

            # 更新进度条
            if self.range_len is not None:
                filled_length = int(self.length * self.current // self.range_len)
                bar = self.fill * filled_length + '-' * (self.length - filled_length) * len(self.fill)

                sys.stdout.write(f'\r{pre_show}{self.prefix} |{bar}|'
                                 f' {self.current}/{self.range_len} -> {elapsed_str}<{estimated_str} | {speed:.1f} it/s |'
                                 f' {self.suffix}{B_Color.RESET.value}')
            else:
                sys.stdout.write(f'\r{pre_show}{self.prefix} | {self.current} iters -> {elapsed_str} | {speed:.1f} it/s |'
                                 f' {self.suffix}{B_Color.RESET.value}')
            sys.stdout.flush()

            # 补回车
            if self.current == self.range_len:
                sys.stdout.write('\n')
                sys.stdout.flush()

    def __iter__(self):
        for item in self.range:
            yield item
            self.update()
