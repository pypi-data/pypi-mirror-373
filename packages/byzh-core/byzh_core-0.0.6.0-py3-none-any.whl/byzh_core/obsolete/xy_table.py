import copy
import math
from typing import List, Tuple, Union
Seq = Union[List, Tuple]
try:
    from wcwidth import wcswidth
except ImportError:
    print("[text table] 请先安装wcwidth库: pip install wcwidth")

class MyDict:
    def __init__(self, init_dict:dict|None = None):
        self.dict = init_dict if init_dict is not None else dict()

    def update(self, other_dict):
        self.dict.update(other_dict)

    def items(self):
        return self.dict.items()
    def keys(self):
        return self.dict.keys()
    def values(self):
        return self.dict.values()

    def __getitem__(self, item):
        return self.dict[str(item)]

    def __setitem__(self, key, value):
        self.dict[str(key)] = value

class B_XYTable:
    def __init__(self, x_name, y_name, x_sidebars=[], y_sidebars=[]):
        self.x_sidebars = self._seq2strlist(x_sidebars)
        self.y_sidebars = self._seq2strlist(y_sidebars)
        self.x_name = x_name
        self.y_name = y_name
        self.dict = self._create_dict(self.x_sidebars, self.y_sidebars)
        self._widths = {x: 0 for x in self.y_sidebars}
        self._update_widths(MyDict({y: y for y in self.y_sidebars}))

    def set(self, x_sidebar, y_sidebar, content):
        x_sidebar, y_sidebar, content = str(x_sidebar), str(y_sidebar), str(content)
        assert x_sidebar in self.dict.keys(), "x_sidebar 与 不是指定好的属性"
        assert y_sidebar in self.dict[x_sidebar].keys(), "y_sidebar 与 不是指定好的属性"
        self.dict[x_sidebar][y_sidebar] = str(content)

    def get(self, x_sidebar, y_sidebar):
        return self.dict[x_sidebar][y_sidebar]
    def items(self):
        '''
        (key1, key2, value)
        '''
        result = [(x, y, self.dict[x][y]) for x in self.x_sidebars for y in self.y_sidebars]
        return result

    def get_table_by_strs(self) -> List[str]:
        results = self._create_prefix()

        for x in self.dict.values():
            self._update_widths(x)

        str_dash = ''
        str_head = ''
        for y in self.y_sidebars:
            pre_space, suf_space = self._get_prefix_suffix(y, self._widths[y], ' ')
            pre_dash, suf_dash = self._get_prefix_suffix('-', self._widths[y], '-')
            str_head += ' ' + pre_space + y + suf_space + ' |'
            str_dash += '-' + pre_dash + '-' + suf_dash + '-+'
        results[0] += str_dash
        results[1] += str_head
        results[2] += str_dash

        offset = 3
        for index, y_dicts in enumerate(self.dict.values()):
            for key, value in y_dicts.items():
                pre_space, suf_space = self._get_prefix_suffix(value, self._widths[key], ' ')
                str_content = ' ' + pre_space + value + suf_space + ' |'
                results[index+offset] += str_content

        results[-1] += str_dash

        return results

    def get_table_by_str(self) -> str:
        result = ""
        strs = self.get_table_by_strs()
        for x in strs[:-1]:
            result += x + '\n'
        result += strs[-1]

        return result
    def print_table(self):
        print(self.get_table_by_str())

    def _create_dict(self, seq1, seq2):
        result = dict()
        for x in seq1:
            temp = MyDict()
            for y in seq2:
                temp.update({y: ''})
            result.update({x: temp})

        return result

    def _create_prefix(self):
        '''
        得到
        +-------+
        | x \ y |
        +-------+
        |   1   |
        |   2   |
        |   3   |
        +-------+
        '''
        results = []

        title = self.x_name + " \ " + self.y_name
        n = self._get_maxlength_from_list(self.x_sidebars)
        length = max(n, self._get_width(title))

        pre_dash, suf_dash = self._get_prefix_suffix("-", length, '-')
        str_dash = "+-" + pre_dash + "-" + suf_dash + "-+"
        results.append(str_dash)

        pre_space, suf_space = self._get_prefix_suffix(title, length, ' ')
        str_index = "| " + pre_space + title + suf_space + " |"
        results.append(str_index)
        results.append(str_dash)

        for x in self.x_sidebars:
            pre_space, suf_space = self._get_prefix_suffix(x, length, ' ')
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

    def _update_widths(self, new_dict: MyDict):
        temps = copy.deepcopy(self._widths)
        for key, value in new_dict.items():
            temps[key] = self._get_width(value)

        if len(self._widths) == 0:
            self._widths = temps
        else:
            for key, value in temps.items():
                if value > self._widths[key]:
                    self._widths[key] = value

    def _seq2strlist(self, seq):
        seq = copy.deepcopy(list(seq))
        for i, x in enumerate(seq):
            seq[i] = str(x)

        return seq

    def _get_width(self, string):
        return wcswidth(string)

    def __len__(self):
        return len(self.x_sidebars) * len(self.y_sidebars)
    def __contains__(self, item):
        for x in self.x_sidebars:
            for y in self.y_sidebars:
                if str(item) == self.dict[x][y]:
                    return True
        return False
    def __str__(self):
        return self.get_table_by_str()

    def __getitem__(self, index):
        return self.dict[str(index)]
    def __setitem__(self, index, value):
        self.dict[index] = value
if __name__ == '__main__':
    my_table = B_XYTable("x", "y", [123, 234], [345, 456])

    my_table[123]['345'] = 'qwq'
    my_table['123']['456'] = '456'
    my_table.set(234, '345', "awwwa")
    my_table.set('234', '456', "123")

    print(my_table)
    print(my_table[123][345])
    for key1, key2, value in my_table.items():
        print(key1, key2, value)

    print('qwq' in my_table)
