import copy
import math
from typing import List, Tuple, Union
Seq = Union[List, Tuple]
try:
    from wcwidth import wcswidth
except ImportError:
    print("[text table] 请先安装wcwidth库: pip install wcwidth")

class B_RowTable:
    def __init__(self, head: Seq):
        self.head = self._seq2strlist(head)
        self.rows = []
        self._widths = []
        self._update_widths(self.head)

    def append(self, sequence: Seq):
        assert len(sequence) == len(self.head), "添加的 序列元素个数 与 head元素个数 不一致"
        self.rows.append(self._seq2strlist(sequence))
    def insert(self, index, sequence: Seq):
        assert len(sequence) == len(self.head), "插入的 序列元素个数 与 head元素个数 不一致"
        self.rows.insert(index, self._seq2strlist(sequence))
    def remove(self, sequence: Seq):
        self.rows.remove(self._seq2strlist(sequence))
    def pop(self, index=-1):
        return self.rows.pop(index)

    def get_table_by_strs(self) -> List[str]:
        results = self._create_prefix()

        for x in self.rows:
            self._update_widths(x)

        str_dash = ''
        str_head = ''
        for i, x in enumerate(self.head):
            pre_space, suf_space = self._get_prefix_suffix(x, self._widths[i], ' ')
            pre_dash, suf_dash = self._get_prefix_suffix('-', self._widths[i], '-')
            str_head += ' ' + pre_space + x + suf_space + ' |'
            str_dash += '-' + pre_dash + '-' + suf_dash + '-+'
        results[0] += str_dash
        results[1] += str_head
        results[2] += str_dash

        offset = 3
        for i, row in enumerate(self.rows):
            for j, x in enumerate(row):
                pre_space, suf_space = self._get_prefix_suffix(x, self._widths[j], ' ')
                str_content = ' ' + pre_space + x + suf_space + ' |'
                results[i+offset] += str_content

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

    def _create_prefix(self):
        '''
        得到
        +-----+
        | num |
        +-----+
        |  1  |
        |  2  |
        |  3  |
        +-----+
        '''
        results = []
        # 编号的位数
        n = self._get_width(str(len(self.rows)))
        length = max(n, self._get_width("index"))

        pre_dash, suf_dash = self._get_prefix_suffix("-", length, '-')
        str_dash = "+-" + pre_dash + "-" + suf_dash + "-+"
        results.append(str_dash)

        pre_space, suf_space = self._get_prefix_suffix("index", length, ' ')
        str_index = "| " + pre_space + "index" + suf_space + " |"
        results.append(str_index)
        results.append(str_dash)

        for i in range(len(self.rows)):
            number = str(i)
            pre_space, suf_space = self._get_prefix_suffix(number, length, ' ')
            str_number = "| " + pre_space + number + suf_space + " |"
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

    def _update_widths(self, seq):
        temps = []
        for x in seq:
            temps.append(self._get_width(x))

        if len(self._widths) == 0:
            self._widths = temps
        else:
            for i, x in enumerate(temps):
                if x > self._widths[i]:
                    self._widths[i] = x

    def _seq2strlist(self, seq):
        seq = copy.deepcopy(list(seq))
        for i, x in enumerate(seq):
            seq[i] = str(x)

        return seq

    def _get_width(self, string):
        return wcswidth(string)

    def __len__(self):
        return len(self.rows)
    def __str__(self):
        return self.get_table_by_str()
    def __getitem__(self, index):
        return self.rows[index]
    def __setitem__(self, index, value):
        self.rows[index] = self._seq2strlist(value)
    def __contains__(self, item):
        for row in self.rows:
            for x in row:
                if str(item) == x:
                    return True
        return False

if __name__ == '__main__':
    my_table = B_RowTable(['云编号', '名称', 'IP地址', 'aaaabbbbcccc'])
    my_table.append(["server01", "服务器01", "172.16.0.1", 'aacc'])
    my_table.append(["server02", "服务器02", "172.16.0.2", 'aacc'])
    my_table.append(["server03", "服务器03", "172.16.0.3", 'aacc'])
    my_table.append(["server04", "服务器04", "172.16.0.4", 'aacc'])
    my_table.append(["server05", "服务器05", "172.16.0.5", 'aacc'])
    my_table.append(["server06", "服务器06", "172.16.0.6", 'aacc'])
    my_table.append(["server07", "服务器07", "172.16.0.7", 'aacc'])
    my_table.append(["server08", "服务器08", "172.16.0.8", 'aacc'])
    my_table.append(["server09", "服务器09", "172.16.0.9", 'aacc'])
    my_table.append(["server10", "服务器10", "172.16.0.0", 'aacc'])
    my_table.append(["server11", "服务器11", "172.16.0.1", 'aacc'])

    my_table.remove(["server08", "服务器08", "172.16.0.8", 'aacc'])

    my_table[4] = ["server99", "服务器99", "172.16.0.9", '99999']
    print(my_table)
    print(len(my_table))

    print("服务器07" in my_table)