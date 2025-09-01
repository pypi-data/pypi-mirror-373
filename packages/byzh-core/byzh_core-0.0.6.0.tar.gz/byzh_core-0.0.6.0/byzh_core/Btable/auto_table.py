import copy
import os
from pathlib import Path
from typing import List, Tuple, Union
Seq = Union[List, Tuple]
try:
    from wcwidth import wcswidth
except ImportError:
    raise ImportError("[table] 请先安装wcwidth库: pip install wcwidth")

def get_width(string):
    return wcswidth(string)

def get_maxwidth_2d(matrix):
    widths = [0 for _ in range(len(matrix[0]))]
    for row in matrix:
        for i, element in enumerate(row):
            if element is None:
                element = ' '
            widths[i] = max(widths[i], get_width(element))

    diff_matrix = [[0 for _ in range(len(matrix[0]))] for _ in range(len(matrix))]
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            element = matrix[i][j]
            if element is None:
                element = ' '
            diff_matrix[i][j] = widths[j] - get_width(element)

    return widths, diff_matrix

def get_T_matrix(matrix):
    new_matrix = [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]
    return new_matrix

def strs2matrix(str_lst):
    str_lst = [x.strip() for x in str_lst if len(x.strip()) > 0]
    str_lst.pop(-1)
    str_lst.pop(2)
    dividing_line = str_lst.pop(0)
    indexes = [i for i, c in enumerate(dividing_line) if c == '+']
    row_cnt = len(str_lst)
    col_cnt = len(indexes) - 1


    matrix = []
    for i in range(row_cnt):
        row = str_lst[i].split('|')[1:-1]
        for j in range(col_cnt):
            row[j] = row[j].strip()
        matrix.append(row)

    row_name, col_name = matrix[0][0].split(' \\ ')

    return matrix, row_name, col_name


class Matrix2d:
    def __init__(self, row_name='x', col_name='y'):
        self.row_name = row_name
        self.col_name = col_name
        self.matrix = [[row_name + ' \\ ' + col_name]]

    def get_rows(self): # 包含left_upper
        if self.matrix == [[]]:
            return []
        return [x[0] for x in self.matrix]
    def get_cols(self): # 包含left_upper
        return self.matrix[0]
    def set_by_str(self, row, col, value):
        row, col, value = str(row), str(col), str(value)

        rows = self.get_rows()
        cols = self.get_cols()

        if row in rows:
            row_index = rows.index(row)
        else:
            row_index = len(rows)
        if col in cols:
            col_index = cols.index(col)
        else:
            col_index = len(cols)

        self.set_by_index(row_index, col_index, row, col, value)

    def set_by_index(self, row_index, col_index, row, col, value):
        row, col, value = str(row), str(col), str(value)

        rows = self.get_rows()
        cols = self.get_cols()

        if row_index < len(rows):
            pass
        elif row_index == len(rows):
            self.matrix.append([row] + [None] * (len(cols) - 1))

        if col_index < len(cols):
            pass
        elif col_index == len(cols):
            self.matrix[0].append(col)
            for i in range(1, len(self.matrix)):
                self.matrix[i].append(None)

        self.matrix[row_index][col_index] = value

    def get_by_str(self, row, col):
        row, col = str(row), str(col)

        rows = self.get_rows()
        cols = self.get_cols()
        if row in rows and col in cols:
            row_index = rows.index(row)
            col_index = cols.index(col)
            return self.get_by_index(row_index, col_index)
        else:
            raise ValueError(f"row {row} or col {col} not found in table")

    def get_by_index(self, row_index, col_index):
        rows = self.get_rows()
        cols = self.get_cols()
        if row_index < len(rows) and col_index < len(cols):
            return self.matrix[row_index][col_index]
        else:
            raise ValueError(f"row_index {row_index} or col_index {col_index} out of range")

    def T(self):
        new_matrix = get_T_matrix(self.matrix)
        new_left_upper = self.col_name + ' \\ ' + self.row_name
        new_matrix[0][0] = new_left_upper

        self.row_name, self.col_name = self.col_name, self.row_name

        self.matrix = new_matrix

        return self
    def __str__(self):
        result = ''
        for x in self.matrix:
            result += str(x) + '\n'
        return result


class Dict1d:
    def __init__(self, dictionary=None):
        self.dict = {}
        if dictionary:
            for key, value in dictionary.items():
                self[key] = value

    def __getitem__(self, key):
        key = str(key)
        try:
            return self.dict[key]
        except KeyError:
            return None
    def __setitem__(self, key, value): # 用于最底层赋值
        key, value = str(key), str(value)
        if value == 'None':
            value = ' '
        self.dict[key] = value
    def set(self, key, value): # 用于非底层赋值（防止把子dict变为str）
        key = str(key)
        self.dict[key] = value


    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()

    def items(self):
        return self.dict.items()

    def copy(self):
        return copy.deepcopy(self)

    def __str__(self):
        return str(self.dict)

    def __repr__(self):
        return str(self.dict)

class Dict2d:
    def __init__(self):
        self.dict = Dict1d()

    # 先实现setitem，再实现getitem
    def __getitem__(self, key):
        key = str(key)
        if key not in self.dict.keys():
            self[key] = Dict1d()
        return self.dict[key]
    def __setitem__(self, key, new_dict: Dict1d | dict):
        key = str(key)
        self.dict.set(key, Dict1d(new_dict))
    def __str__(self):
        return str(self.dict)

class B_Table2d:
    def __init__(self, row_name='x', col_name='y', auto_adaptive=False, narrow_better=True):
        '''

        :param row_name:
        :param col_name:
        :param auto_adaptive: 是否采取自动翻转的策略，来提升显示效果
        :param narrow_better: 在auto_adaptive=True的情况下，是否优先选择横向窄的表格，避免换行显示
        '''
        self.row_name = row_name
        self.col_name = col_name
        self.auto_adaptive = auto_adaptive
        self.narrow_better = narrow_better

        self.matrix2d = Matrix2d(row_name, col_name) # 用于输出
        self.dict2d = Dict2d() # 用于输入

        # 判断是否改变
        self.is_changed = False

    def set(self, row, col, content):
        row, col, content = str(row), str(col), str(content)
        self[row][col] = content

    def get_str(self, row, col):
        return self[row][col]
    def get_int(self, row, col):
        return int(self[row][col])
    def get_float(self, row, col):
        return float(self[row][col])
    def get_bool(self, row, col):
        '''
        如果是字符串"True"或"1"，返回True，否则返回False
        '''
        temp = self[row][col]
        if temp == "True" or temp == "1":
            return True
        else:
            return False

    def __getitem__(self, row):
        self.is_changed = True

        row = str(row)
        return self.dict2d[row]

    def __setitem__(self, row, new_dict):
        self.is_changed = True

        row = str(row)
        self.dict2d[row] = new_dict

    def from_txt(self, txt_path, create:bool=False, use_txt_name:bool=False):
        '''
        :param txt_path:
        :param create: 如果文件不存在，则创建
        :param use_txt_name: 默认使用init时的row_name和col_name
        :return:
        '''
        if not os.path.exists(txt_path):
            if create:
                self.to_txt(txt_path)
            else:
                raise FileNotFoundError(f"文件不存在: {txt_path}")

        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        matrix, row_name, col_name = strs2matrix(lines)
        if {self.row_name, self.col_name} != {row_name, col_name}:
            raise ValueError(f"行头列头正反均不对应，请检查: [{self.row_name}, {self.col_name}] ❌ [{row_name}, {col_name}]")

        if use_txt_name:
            self.row_name = row_name
            self.col_name = col_name
            self.matrix2d = Matrix2d(self.row_name, self.col_name)
            self.matrix2d.matrix = matrix
        else:
            left_upper = self.row_name + ' \\ ' + self.col_name
            matrix[0][0] = left_upper
            if self.row_name == row_name and self.col_name == col_name:
                self.matrix2d = Matrix2d(self.row_name, self.col_name)
                self.matrix2d.matrix = matrix
            elif self.row_name == col_name and self.col_name == row_name:
                self.matrix2d = Matrix2d(self.col_name, self.row_name)
                self.matrix2d.matrix = get_T_matrix(matrix)

        self.__matrix2dict()

    def to_txt(self, txt_path):
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(str(self))

    def to_strs(self):
        if self.is_changed:
            self.__dict2matrix()
        if self.__if_need_T():
            self.T()

        result = []

        # 计算宽度
        widths, diff_matrix = get_maxwidth_2d(self.matrix2d.matrix)

        for i in range(len(self.matrix2d.matrix)):
            elements = []
            for j in range(len(self.matrix2d.matrix[i])):
                element = self.matrix2d.matrix[i][j]
                if element is None:
                    element = ' '
                diff = diff_matrix[i][j]
                diff_left = diff // 2
                diff_right = diff - diff_left
                element = ' '*diff_left + str(element) + ' '*diff_right
                elements.append(element)
            row = ' | '.join(elements)
            row = '| ' + row + ' |'
            result.append(row)

        # 添加三行分隔线
        dividing_line = '+' + '+'.join(['-' * (widths[i] + 2) for i in range(len(widths))]) + '+'
        result.append(dividing_line)
        result.insert(1, dividing_line)
        result.insert(0, dividing_line)

        return result

    def to_str(self):
        return '\n'.join(self.to_strs())

    def to_ini(self, path):
        '''
        输出为ini格式
        :param path:
        :return:
        '''
        if self.is_changed:
            self.__dict2matrix()

        groups = self.matrix2d.get_rows()[1:]
        keys = self.matrix2d.get_cols()[1:]
        with open(path, 'w', encoding='utf-8') as f:
            for i, group in enumerate(groups):
                f.write(f"[{group}]\n")
                for j, key in enumerate(keys):
                    value = self.matrix2d.get_by_index(i+1, j+1)
                    f.write(f"{key} = {value}\n")
                f.write("\n")

    def from_ini(self, path):
        '''
        输入为ini格式
        :param path:
        :return:
        '''
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self.dict2d = Dict2d()

        group = None
        for line in lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                group = line[1:-1]
            elif '=' in line:
                key, value = line.split('=')
                key = key.strip()
                value = value.strip()
                if value == 'None':
                    value = None
                self[group][key] = value

        self.__dict2matrix()

    def __str__(self):
        return self.to_str()

    def __repr__(self):
        if self.is_changed:
            self.__dict2matrix()

        result = ''
        for x in self.matrix2d.matrix:
            result += str(x) + '\n'
        return result

    def T(self):
        if self.is_changed:
            self.__dict2matrix()
        self.matrix2d.T()
        self.row_name, self.col_name = self.col_name, self.row_name
        self.__matrix2dict()

        return self

    def __matrix2dict(self): # __
        keys1 = self.matrix2d.get_rows()[1:]
        keys2 = self.matrix2d.get_cols()[1:]
        self.dict2d = Dict2d()
        for i, key1 in enumerate(keys1):
            for j, key2 in enumerate(keys2):
                value = self.matrix2d.get_by_index(i+1, j+1)
                self.dict2d[key1][key2] = value

        self.is_changed = False

    def __dict2matrix(self): # __
        left_upper = self.row_name + ' \\ ' + self.col_name
        # 处理keys1和keys2
        keys1 = [left_upper] + list(self.dict2d.dict.keys())
        keys2 = [left_upper]

        temp = []
        for key1 in self.dict2d.dict.keys():
            for key2 in self.dict2d.dict[key1].keys():
                if key2 not in temp:
                    temp.append(key2)

        keys2.extend(temp)

        # 处理matrix框架
        matrix = [keys2]
        for x in keys1[1:]:
            matrix.append([x] + [None] * (len(keys2) - 1))

        # 构建matrix2d
        self.matrix2d = Matrix2d(self.row_name, self.col_name)
        self.matrix2d.matrix = matrix
        for row in self.dict2d.dict.keys():
            for col in self.dict2d.dict[row].keys():
                value = self.dict2d.dict[row][col]
                self.matrix2d.set_by_str(row, col, value)

        self.is_changed = False
    def __if_need_T(self):
        '''
        尽管T，但只是出来的str是T过的，并没有改变原来的矩阵，
        所以赋值还是原来的字符索引
        :return:
        '''
        if not self.auto_adaptive:
            return False

        now_matrix2d = self.matrix2d
        T_matrix2d = copy.deepcopy(now_matrix2d).T()

        now_widths, _ = get_maxwidth_2d(now_matrix2d.matrix)
        T_widths, _ = get_maxwidth_2d(T_matrix2d.matrix)

        now_width = sum(now_widths)
        T_width = sum(T_widths)

        if T_width < now_width and self.narrow_better:
            return True
        elif T_width > now_width and not self.narrow_better:
            return True
        else:
            return False


if __name__ == '__main__':
    a = B_Table2d(row_name='data', col_name='score', auto_adaptive=False)
    # a[0][1] = 'a3'
    # a[11][22] = '123'
    # a[11][1] = 'dawd'
    a.from_txt('./a.txt')
    print(a)
    # a.T()
    # print(a)


