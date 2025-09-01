import copy
import math
import os
from pathlib import Path
from typing import List, Tuple, Union
Seq = Union[List, Tuple]
try:
    from wcwidth import wcswidth
except ImportError:
    raise ImportError("[table] 请先安装wcwidth库: pip install wcwidth")

class InnerList:
    def __init__(self):
        self.key_list = []
        self.value_list = []

    def items(self):
        return zip(self.key_list, self.value_list)
    def keys(self):
        return self.key_list
    def values(self):
        return self.value_list
    def copy(self):
        return copy.deepcopy(self)
    def __getitem__(self, item):
        item = str(item)
        if item not in self.key_list:
            self.key_list.append(item)
            self.value_list.append('')
        index = self.key_list.index(item)
        return self.value_list[index]

    def __setitem__(self, key, value):
        key, value = str(key), str(value)
        if key not in self.key_list:
            self.key_list.append(key)
            self.value_list.append(value)
        index = self.key_list.index(key)
        self.value_list[index] = value


class OuterList:
    def __init__(self):
        self.key_list = []
        self.value_list = []

    def items(self):
        return zip(self.key_list, self.value_list)
    def keys(self):
        return self.key_list
    def values(self):
        return self.value_list
    def __getitem__(self, item: str):
        item = str(item)
        if item not in self.key_list:
            self.key_list.append(item)
            self.value_list.append(InnerList())
        index = self.key_list.index(item)
        return self.value_list[index]

    def __setitem__(self, key, value):
        key, value = str(key), value
        if key not in self.key_list:
            self.key_list.append(key)
            self.value_list.append(value)
        self.value_list[self.key_list.index(key)] = value

class MyMatrix:
    def __init__(self):
        self.matrix = []
        self.fill = ' '


    def add(self, i, j, value):
        if i > len(self.matrix)-1:
            self.matrix.extend([[] for _ in range(i-len(self.matrix)+1)])
        if j > len(self.matrix[i])-1:
            self.matrix[i].extend([self.fill for _ in range(j-len(self.matrix[i])+1)])
        self.matrix[i][j] = value

    def update_matrix(self):
        max_length = max([len(x) for x in self.matrix])
        for i in range(len(self.matrix)):
            self.matrix[i].extend([self.fill for _ in range(max_length-len(self.matrix[i]))])

    def get_matrix(self):
        self.update_matrix()
        return self.matrix

class B_AutoTable:
    def __init__(self, row_name='x', col_name='y', auto_adaptive=False):
        self.row_sidebar = []
        self.col_sidebar = []
        self.row_name = row_name
        self.col_name = col_name
        self.lists = OuterList()
        self.verbose_lists = []
        self._widths = []

        self.auto_adaptive = auto_adaptive

    def set(self, row, col, content):
        row, col, content = str(row), str(col), str(content)
        self.lists[row][col] = content

    def get_str(self, row, col):
        return self[row][col]
    def get_int(self, row, col):
        return int(self[row][col])
    def get_float(self, row, col):
        return float(self[row][col])
    def get_bool(self, row, col):
        temp = self[row][col]
        if temp == "True" or temp == "1":
            return True
        else:
            return False
    def items(self):
        '''
        (key1, key2, value)
        '''
        self._update_all()
        result = [(row, col, self[row][col]) for row in self.row_sidebar for col in self.col_sidebar]
        return result
    def copy_row(self, new_row, old_row):
        new_row, old_row = str(new_row), str(old_row)
        self[new_row] = self[old_row]
    def read_txt(self, path:Path, row_name:None|str=None, col_name:None|str=None):
        with open(path, 'r') as f:
            lines = f.readlines()
            lines = [x.strip() for x in lines if x.startswith('|')]

        # 所有内容
        temp = []
        for string in lines:
            elements = string.split('|')[1:-1]
            elements = [x.strip() for x in elements]
            temp.append(elements)

        # 边角内容
        x_name, y_name = temp[0][0].split(' \\ ') if ('\\' in temp[0][0]) else ("x", "y")
        x_sidebar = [var[0] for var in temp[1:]]
        y_sidebar = temp[0][1:]

        if row_name == y_name and col_name == x_name: # 不按txt的样子读, 而是翻折后读
            self.row_sidebar = y_sidebar
            self.col_sidebar = x_sidebar
            self.row_name = y_name
            self.col_name = x_name
            self.lists = OuterList()
            self._widths = []
            for i in range(len(y_sidebar)):
                for j in range(len(x_sidebar)):
                    self[y_sidebar[i]][x_sidebar[j]] = temp[j + 1][i + 1]
        else:
            self.row_sidebar = x_sidebar
            self.col_sidebar = y_sidebar
            self.row_name = x_name
            self.col_name = y_name
            self.lists = OuterList()
            self._widths = []
            for i in range(len(x_sidebar)):
                for j in range(len(y_sidebar)):
                    self[x_sidebar[i]][y_sidebar[j]] = temp[i+1][j+1]

    def to_txt(self, path):
        '''
        将表格内容写入文件
        :param path:
        :return:
        '''
        dir = Path(path).resolve().parent
        os.makedirs(dir, exist_ok=True)
        with open(path, 'w') as f:
            f.write(self.to_str())

    def update_txt(self, path):
        '''
        更新表格内容\n
        如果文件不存在，则创建文件
        :param path:
        :return:
        '''
        # 是否存在该文件
        if not os.path.exists(path):
            self.to_txt(path)
        else:
            current_lists = self.lists
            self.read_txt(path, self.row_name, self.col_name)
            new_lists = self.lists
            self.lists = self._merge_lists(new_lists, current_lists)

            self.to_txt(path)



    def to_strs(self) -> List[str]:
        transpose = self._need_transpose()
        self._update_all(transpose)
        self._update_widths()
        results = self._create_prefix()

        str_dash = ''
        str_head = ''
        for index, y in enumerate(self.col_sidebar):
            pre_space, suf_space = self._get_prefix_suffix(y, self._widths[index], ' ')
            pre_dash, suf_dash = self._get_prefix_suffix('-', self._widths[index], '-')
            str_head += ' ' + pre_space + y + suf_space + ' |'
            str_dash += '-' + pre_dash + '-' + suf_dash + '-+'
        results[0] += str_dash
        results[1] += str_head
        results[2] += str_dash

        offset = 3
        for i, y_list in enumerate(self.verbose_lists):
            for j, value in enumerate(y_list):
                pre_space, suf_space = self._get_prefix_suffix(value, self._widths[j], ' ')
                str_content = ' ' + pre_space + value + suf_space + ' |'
                results[i+offset] += str_content

        results[-1] += str_dash

        return results

    def to_str(self) -> str:
        result = ""
        strs = self.to_strs()
        for x in strs[:-1]:
            result += x + '\n'
        result += strs[-1]

        return result

    def _merge_lists(self, lists_base, lists_new):
        result = OuterList()

        for row_key, inner_list in lists_base.items():
            for col_key, value in inner_list.items():
                result[row_key][col_key] = value
        for row_key, inner_list in lists_new.items():
            for col_key, value in inner_list.items():
                result[row_key][col_key] = value

        return result

    def _update_all(self, transpose=False):
        if not transpose:
            row_sidebar = []
            col_sidebar = []
            my_matrix = MyMatrix()
            for x_key, x_list in self.lists.items():
                row_sidebar.append(x_key)
                i = row_sidebar.index(x_key)

                for y_key, value in x_list.items():
                    if y_key not in col_sidebar:
                        col_sidebar.append(y_key)
                    j = col_sidebar.index(y_key)

                    my_matrix.add(i, j, value)

            self.row_sidebar = row_sidebar
            self.col_sidebar = col_sidebar
            self.verbose_lists = my_matrix.get_matrix()
            self.row_name, self.col_name = self.row_name, self.col_name
        else:
            row_sidebar = []
            col_sidebar = []
            my_matrix = MyMatrix()
            for x_key, x_list in self.lists.items():
                col_sidebar.append(x_key)
                i = col_sidebar.index(x_key)

                for y_key, value in x_list.items():
                    if y_key not in row_sidebar:
                        row_sidebar.append(y_key)
                    j = row_sidebar.index(y_key)

                    my_matrix.add(j, i, value)

            self.row_sidebar = row_sidebar
            self.col_sidebar = col_sidebar
            self.verbose_lists = my_matrix.get_matrix()
            self.row_name, self.col_name = self.col_name, self.row_name

    def _update_widths(self):
        '''
        请先调用_update_sidebar_and_vlist
        :return:
        '''
        temp = [self._get_width(x) for x in self.col_sidebar]

        for i in range(len(self.verbose_lists)):
            for j in range(len(self.verbose_lists[i])):
                temp[j] = max(temp[j], self._get_width(self.verbose_lists[i][j]))

        self._widths = temp

    def _create_prefix(self):
        '''
        先调用_update_sidebar_and_vlist

        得到
        +-------+
        | x \ y |
        +-------+
        |   1   |
        |   2   |
        |   3   |
        +-------+
        '''
        front, behind, row_sidebar = self.row_name, self.col_name, self.row_sidebar


        results = []

        title = front + " \ " + behind
        n = self._get_maxlength_from_list(row_sidebar)
        target_length = max(n, self._get_width(title))

        pre_dash, suf_dash = self._get_prefix_suffix("-", target_length, '-')
        str_dash = "+-" + pre_dash + "-" + suf_dash + "-+"
        results.append(str_dash)

        pre_space, suf_space = self._get_prefix_suffix(title, target_length, ' ')
        str_index = "| " + pre_space + title + suf_space + " |"
        results.append(str_index)
        results.append(str_dash)

        for x in row_sidebar:
            pre_space, suf_space = self._get_prefix_suffix(x, target_length, ' ')
            str_number = "| " + pre_space + x + suf_space + " |"
            results.append(str_number)
        results.append(str_dash)

        return results

    def _get_prefix_suffix(self, string, length, charactor=' '):
        prefix = ''
        suffix = ''
        str_len = self._get_width(string)

        delta = length - str_len
        if delta < 0:
            assert "string的宽度比length宽"
        elif delta == 0:
            pass
        else:
            prefix = charactor * math.floor(delta / 2)
            suffix = charactor * math.ceil(delta / 2)

        return prefix, suffix

    def _get_maxlength_from_list(self, lst: List[str]) -> int:
        temp = [self._get_width(x) for x in lst]
        if len(temp) == 0:
            return 0
        else:
            return max(temp)

    def _get_width(self, string):
        return wcswidth(string)

    def _need_transpose(self):
        if self.auto_adaptive:
            self._update_all()

            normal_widths = [self._get_width(x) for x in self.col_sidebar]
            for i in range(len(self.verbose_lists)):
                for j in range(len(self.verbose_lists[i])):
                    normal_widths[j] = max(normal_widths[j], self._get_width(self.verbose_lists[i][j]))

            transpose_widths = [self._get_width(x) for x in self.row_sidebar]
            for i in range(len(self.verbose_lists)):
                for j in range(len(self.verbose_lists[i])):
                    transpose_widths[i] = max(transpose_widths[i], self._get_width(self.verbose_lists[i][j]))

            if sum(normal_widths) > sum(transpose_widths):
                return True
            return False
        return False


    def __len__(self):
        return len(self.row_sidebar) * len(self.col_sidebar)
    def __contains__(self, item):
        item = str(item)
        for x in self.row_sidebar:
            for y in self.col_sidebar:
                if item == self[x][y]:
                    return True
        return False
    def __str__(self):
        return self.to_str()

    def __getitem__(self, index):
        index = str(index)
        return self.lists[index]
    def __setitem__(self, index, value:InnerList):
        index = str(index)
        self.lists[index] = value.copy()


# if __name__ == '__main__':
#     my_table = BAutoTable("x", "y", auto_adaptive=True)
#
#     my_table[1][3] = "w"
#
#     my_table[2][2] = "b"
#     my_table[1][5] = "a"
#     my_table[3][5] = "b"
#
#     print(my_table)

if __name__ == '__main__':
    my_table = B_AutoTable("x", "y", auto_adaptive=False)

    my_table[1][3] = "w"

    my_table[2][2] = "b"
    my_table[1][5] = "a"
    my_table["wq"]["dw"] = "adawd"
    my_table["wqdq"]["ddasfsaddw"] = "adawd"

    print(my_table)
    for x, y, value in my_table.items():
        print(x, y, value)
