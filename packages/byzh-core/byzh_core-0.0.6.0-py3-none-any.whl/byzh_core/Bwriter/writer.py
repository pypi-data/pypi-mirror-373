from pathlib import Path
from typing import Literal
import time
import os

from ..Butils import B_Color

def color_wrap(string:str, color:B_Color):
    return color.value + string + B_Color.RESET.value

class B_Writer:
    def __init__(
        self,
        path:Path,
        mode:Literal["w", "a"] = "w",
        time_file:bool = False,
        color:B_Color = B_Color.RESET,
    ):
        '''
        :param path: 日志保存路径
        :param time_file: 是否输出时间
        '''
        super().__init__()
        self.path = Path(path)
        self.mode = mode
        self.time_file = time_file

        self.color = color

        self.f = None
        self.setFile(self.path, self.mode, self.time_file)

    def setFile(self, file: Path, mode: Literal["w", "a"] = "w", ifTime=False):
        '''
        设置 file的path 以及 writer的ifTime
        :param file: 设置log路径
        :param ifTime:
        :return:
        '''
        if self.f is not None:
            self.f.close()
        self.path = Path(file)
        self.time_file = ifTime
        self.__createDir(self.path)
        self.f = open(self.path, mode, encoding="utf-8")

    def clearFile(self):
        '''
        清空内容
        '''
        assert self.f is not None, "请先调用setFile方法"
        self.f.close()
        self.f = open(self.path, 'w', encoding="utf-8")

    def closeFile(self):
        '''
        关闭log
        '''
        if self.f:
            self.f.close()
            self.f = None

    def toCmd(self, string:str, ifTime:bool=False, color:B_Color = None):
        '''
        打印到terminal
        '''
        t = ''
        if ifTime:
            t = time.strftime("%Y-%m-%d %H:%M:%S ##### ", time.localtime())

        if color is None:
            print(color_wrap(t+str(string), self.color))
        else:
            print(color_wrap(t+str(string), color))

    def toFile(self, string:str, ifTime:bool=None):
        '''
        写入到文件内
        '''
        assert self.f is not None, "请先调用setFile方法"

        t = ''
        if ifTime == False: # 为了使False时不管self.time_file
            pass
        elif ifTime==True or self.time_file==True:
            t = time.strftime("%Y-%m-%d %H:%M:%S ##### ", time.localtime())

        self.f.write(str(t+string))
        self.f.write("\n")
        self.f.flush()

    def toBoth(self, string:str, file_time:bool=None, cmd_time:bool=False, color:B_Color = None):
        '''
        同时写入到文件和terminal
        :param string:
        :param color:
        :return:
        '''
        self.toFile(str(string), file_time)
        self.toCmd(str(string), cmd_time, color)
    def __call__(self, string:str, file_time:bool=None, cmd_time:bool=False, color:B_Color = None):
        self.toBoth(string, file_time, cmd_time, color)

    def __createDir(self, path):
        # 获取到该文件的文件夹
        dir = path.parents[0]
        os.makedirs(dir, exist_ok=True)

    def __exit__(self):
        self.closeFile()

if __name__ == '__main__':
    B_Writer()