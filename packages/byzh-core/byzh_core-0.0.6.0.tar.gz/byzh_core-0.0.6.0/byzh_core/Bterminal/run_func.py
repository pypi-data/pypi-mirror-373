from itertools import product
from typing import Sequence, Callable, Literal
import warnings
class b_Wrapper():
    def __init__(
            self,
            mode:Literal["product", "zip"] = "product",
            **kwargs: Sequence
    ):
        self.mode = mode
        self.keys = []

        for key, value in kwargs.items():
            setattr(self, key+"_list", value)
            self.keys.append(key)

        self.values_lst = self._get_values_lst()

    def _get_values_lst(self):
        temp = [getattr(self, key + "_list") for key in self.keys]
        if self.mode == "product":
            return list(product(*temp))
        elif self.mode == "zip":
            # 检查是否个数相同
            if len(set(map(len, temp)))!= 1:
                warnings.warn("zip模式下, 如果各部分的len不一样, 则超出部分不参与遍历")
            return list(zip(*temp))
        else:
            raise ValueError("Invalid mode")

    def _set_values(self, index):
        for key, value in zip(self.keys, self.values_lst[index]):
            setattr(self, key, value)

    def run(self, func: Callable, *args, **kwargs):
        for i in range(len(self.values_lst)):
            self._set_values(i)
            func(*args, **kwargs)


if __name__ == '__main__':
    def demo_func():
        print(f"x={wrapper.x}, y={wrapper.y}, x+y={wrapper.x + wrapper.y}")

    # 示例 1: product 笛卡尔积模式
    print("=== product 模式 ===")
    wrapper = b_Wrapper(
        mode="product",
        x=[1, 2, 3],
        y=[10, 20]
    )
    wrapper.run(demo_func)

    # 示例 2: zip 模式
    print("\n=== zip 模式 ===")
    wrapper = b_Wrapper(
        mode="zip",
        x=[1, 2, 3],
        y=[10, 20, 30]
    )
    wrapper.run(demo_func)
