import os
from pathlib import Path
import subprocess
import time

from ..Butils import B_Color


def args_process(args: tuple) -> list:
    lst = []
    for x in args:
        if type(x) is str:
            lst.append(x)
        elif type(x) is list:
            lst.extend(x)
    return lst

def b_run_cmd(
        *args: str,
        show: bool = True,
):
    '''
    可传入多个字符串, 在cmd中运行
    :param args:
    :param show: 若show=True, 则会单开一个cmd, 在cmd中运行
    :return:
    '''
    command = ''
    for i in range(len(args)):
        if i == len(args) - 1:
            command += str(args[i])
            break
        command += str(args[i]) + ' && '
    if show:
        command = f'start cmd /K "{command}"'
    # print(command)
    subprocess.run(command, shell=True)

def b_run_python(
    *args: str|list[str],
    limit_time: int|float|None = None,
    log_path: Path|None = None
):
    '''
    可传入多个字符串, 在当前python环境下运行
    :param args: 以python开头, 用于运行.py文件
    :param show:
    :return:
    '''
    def run_log(content=''):
        if log_path is not None:
            parent = Path(log_path).parent
            os.makedirs(parent, exist_ok=True)
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("=====================\n")
                for string in str_lst:
                    f.write("\t" + string + '\n')
                f.write("=====================\n")
                f.write(content)

    str_lst = args_process(args)

    print(f"{B_Color.GREEN.value}=====================")
    print("BRunPython 将在3秒后开始:")
    for string in str_lst:
        print("\t" + string)
    print(f"====================={B_Color.RESET.value}")
    time.sleep(3)

    for string in str_lst:
        try:
            command_lst = string.split(' ')
            run_log("正在执行: " + string)
            start = time.time()
            result = subprocess.run(command_lst, timeout=limit_time)
            end = time.time()
            delta_t = end - start
            h_t = int(delta_t // 3600)
            m_t = int((delta_t % 3600) // 60)
            s_t = int(delta_t % 60)
            if result.returncode != 0: # 报错
                index = str_lst.index(string)
                str_lst[index] = string + f"\t[!!!Error!!!] [{h_t}h {m_t}m {s_t}s]"
            else:
                index = str_lst.index(string)
                str_lst[index] = string + f"\t[~Success~] [{h_t}h {m_t}m {s_t}s]"
        except subprocess.TimeoutExpired:
            print(f"程序运行超过 {limit_time} 秒，已被强制终止")
            h_t = int(limit_time // 3600)
            m_t = int((limit_time % 3600) // 60)
            s_t = int(limit_time % 60)
            index = str_lst.index(string)
            str_lst[index] = string + f"\t[!!!Time limit!!!] [{h_t}h {m_t}m {s_t}s]"

    print(f"{B_Color.GREEN}====================={B_Color.RESET}")
    print(f"{B_Color.GREEN}BRunPython 结束:{B_Color.RESET}")
    for string in str_lst:
        if 'Time limit' in string:
            print(f"\t{B_Color.YELLOW}" + string + f"{B_Color.RESET}")
        elif 'Error' in string:
            print(f"\t{B_Color.RED}" + string + f"{B_Color.RESET}")
        else:
            print(f"\t{B_Color.GREEN}" + string + f"{B_Color.RESET}")
    print(f"{B_Color.GREEN}====================={B_Color.RESET}")

    run_log('结束')



if __name__ == '__main__':
    b_run_cmd("echo hello", "echo world", "echo awa", show=True)
    # b_run_python(
    #     r"python E:\byzh_workingplace\byzh-rc-to-pypi\test1.py",
    #     r"python E:\byzh_workingplace\byzh-rc-to-pypi\test2.py",
    #     limit_time=3,
    # )