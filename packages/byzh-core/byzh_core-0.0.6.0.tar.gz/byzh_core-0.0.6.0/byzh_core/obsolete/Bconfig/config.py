from ...Butils import B_Color


class B_Config:
    def __init__(self):
        super().__init__()
        self.group_lst = []
        self.dict_lst = []

    # set-方法
    def set(self, group, key, value):
        '''
        添加元素
        '''
        if not isinstance(group, str):
            raise Exception(f"{B_Color.YELLOW}group({str(group)}) must be str{B_Color.RESET}")
        if not isinstance(key, str):
            raise Exception(f"{B_Color.YELLOW}key({str(key)}) must be str{B_Color.RESET}")

        if group not in self.group_lst:
            self.group_lst.append(group)
            self.dict_lst.append(dict())

        index = self._get_index(group)
        self.dict_lst[index][key] = value

    def set_copygroup(self, dst_group, src_group):
        '''
        通过复制group来快速添加组
        '''
        if not isinstance(dst_group, str):
            raise Exception(f"{B_Color.YELLOW}group({str(dst_group)}) must be str{B_Color.RESET}")
        if not isinstance(src_group, str):
            raise Exception(f"{B_Color.YELLOW}group({str(src_group)}) must be str{B_Color.RESET}")
        if dst_group in self.group_lst:
            raise Exception(f"{B_Color.YELLOW}group({str(dst_group)}) already exist{B_Color.RESET}")

        import copy
        self.group_lst.append(dst_group)
        self.dict_lst.append(copy.deepcopy(self.dict_lst[self._get_index(src_group)]))

    def set_dictgroup(self, group, dict):
        '''
        通过dict来快速添加组
        '''
        if group in self.group_lst:
            raise Exception(f"{B_Color.YELLOW}group({str(group)}) already exist{B_Color.RESET}")
        self.group_lst.append(group)
        # 把dict的键值对都化为字符串
        self.dict_lst.append({str(key): str(value) for key, value in dict.items()})

    # show-方法
    def show_all(self):
        '''
        打印config
        '''
        print(f"group_cnt({len(self.group_lst)}) | {self.group_lst} \ndict_cnt:{len(self.dict_lst)}")
        print()
        for group, dict in zip(self.group_lst, self.dict_lst):
            print(f"{group}:\n\t{dict}")

    def show_group(self, group):
        '''
        打印某个group
        '''
        result = self._get_group_str(group)
        print(group + ":\n" + result)

    # get-方法
    def get_str(self, group, key):
        '''
        获取某个group的某个key的值
        '''
        self._check(group, key)
        index = self._get_index(group)
        return str(self.dict_lst[index][key])

    def get_int(self, group, key):
        '''
        获取某个group的某个key的值
        '''
        self._check(group, key)
        index = self._get_index(group)
        return int(self.dict_lst[index][key])

    def get_float(self, group, key):
        '''
        获取某个group的某个key的值
        '''
        self._check(group, key)
        index = self._get_index(group)
        return float(self.dict_lst[index][key])

    def get_bool(self, group, key):
        '''
        获取某个group的某个key的值\n
        只有value为["False", "0", "None"]时，返回False
        '''
        self._check(group, key)

        if self.get_str(group, key) in ["False", "0", "None"]:
            return False
        elif self.get_str(group, key) in ["True", "1"]:
            return True
        else:
            raise Exception(f"{B_Color.YELLOW}value({str(key)}) cannot change to bool{B_Color.RESET}")

    # save-方法
    def to_pickle(self, path):
        '''
        保存为pickle文件(最稳定的方式)
        '''
        import pickle
        with open(path, 'wb') as f:
            pickle.dump([self.group_lst, self.dict_lst], f)

    def from_pickle(self, path):
        '''
        从pickle文件中读取
        '''
        import pickle
        with open(path, 'rb') as f:
            [self.group_lst, self.dict_lst] = pickle.load(f)

    def to_json(self, path):
        '''
        保存为json文件
        '''
        import json
        with open(path, 'w') as f:
            for group, group_dict in zip(self.group_lst, self.dict_lst):
                entry = {"group": group, "dict": group_dict}
                json.dump(entry, f)
                f.write("\n")

    def from_json(self, path):
        '''
        从json文件中读取
        '''
        import json
        with open(path, 'r') as f:
            self.group_lst = []
            self.dict_lst = []
            for line in f:
                entry = json.loads(line.strip())
                self.group_lst.append(entry["group"])
                self.dict_lst.append(entry["dict"])

    def to_yaml(self, path):
        '''
        保存为yaml文件
        '''
        import yaml
        with open(path, 'w') as f:
            yaml.dump([self.group_lst, self.dict_lst], f)

    def from_yaml(self, path):
        '''
        从yaml文件中读取
        '''
        import yaml
        with open(path, 'r') as f:
            [self.group_lst, self.dict_lst] = yaml.load(f, Loader=yaml.FullLoader)

    def to_ini(self, path):
        '''
        保存为ini文件
        '''
        with open(path, 'w') as f:
            for group, dict in zip(self.group_lst, self.dict_lst):
                f.write(f"[{group}]\n")
                for key, value in dict.items():
                    f.write(f"{key} = {value}\n")
                f.write("\n")

    def from_ini(self, path):
        '''
        从ini文件中读取
        '''
        self.group_lst = []
        self.dict_lst = []
        with open(path, 'r') as f:
            lines = f.readlines()
            dictionary = dict()
            for line in lines:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    # 如果字典非空不是dict()
                    if dictionary != dict():
                        self.dict_lst.append(dictionary.copy())
                        dictionary.clear()
                    group = line[1:-1]
                    self.group_lst.append(group)
                elif line == '':
                    continue
                else:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # key和value去除前后空格
                        key = key.strip()
                        value = value.strip()
                        dictionary[key] = value
                    else:
                        dictionary[line] = ''
            if dictionary != dict():
                self.dict_lst.append(dictionary.copy())

    def to_csv(self, path):
        '''
        保存为csv文件
        '''
        import csv
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header: the first row is group names
            header = ['key'] + self.group_lst
            writer.writerow(header)

            # Find all unique keys across all groups
            all_keys = set()
            for group_dict in self.dict_lst:
                all_keys.update(group_dict.keys())

            # Write rows for each key
            for key in all_keys:
                row = [key]
                for group_dict in self.dict_lst:
                    row.append(group_dict.get(key, ''))  # Add value or empty if key is not present
                writer.writerow(row)

    def from_csv(self, path):
        '''
        从csv文件中读取
        '''
        import csv
        with open(path, 'r') as f:
            reader = csv.reader(f)

            # Read header: the first row is group names
            header = next(reader)
            group_lst = header[1:]  # The first column is 'key', rest are groups
            self.group_lst = group_lst
            self.dict_lst = [{} for _ in range(len(group_lst))]  # Initialize dicts for each group

            # Read the key-value pairs
            for row in reader:
                key = row[0]
                for i, value in enumerate(row[1:], start=0):
                    if value:  # Only add value if it's not empty
                        self.dict_lst[i][key] = value

    def to_table(self, path):
        from ..Btable import B_Table2d
        my_table = B_Table2d()
        for index, group in enumerate(self.group_lst):
            for key, value in self.dict_lst[index].items():
                my_table[group][key] = value

        my_table.to_txt(path)

    # 工具-方法
    def __str__(self):
        result = ""
        for group in self.group_lst:
            result += group + ":\n"
            result += self._get_group_str(group) + "\n"
        # 去掉最后一个\n
        result = result[:-1]
        return result
    def __getitem__(self, item):
        return self.dict_lst[item]

    def __setitem__(self, key, value):
        self.set_dictgroup(key, value)

    def _get_index(self, group):
        return self.group_lst.index(group)

    def _get_group_str(self, group):
        self._check(group)
        index = self._get_index(group)
        result = "\n".join([f"\t({key} -> {value})" for key, value in self.dict_lst[index].items()])
        return result

    def _check(self, group, key=None):
        # 检查group是否是字符串
        if not isinstance(group, str):
            raise Exception(f"{B_Color.YELLOW}group({str(group)}) must be str{B_Color.RESET}")
        # 检查group是否在group_list中
        if group not in self.group_lst:
            raise Exception(f"{B_Color.YELLOW}group({str(group)}) not found{B_Color.RESET}")

        if key is not None:
            # 检查key是否是字符串
            if not isinstance(key, str):
                raise Exception(f"{B_Color.YELLOW}key({str(key)}) must be str{B_Color.RESET}")
            # 检查key是否在dict中
            index = self._get_index(group)
            if key not in self.dict_lst[index]:
                raise Exception(f"{B_Color.YELLOW}key({str(key)}) not found{B_Color.RESET}")


if __name__ == '__main__':
    a = B_Config()

    a.set('awa', 'a', 'None')
    a.set('awa', 'b', '123')
    a.set('awa', '345', '33333')

    a.set('awa', 'a532', 'No32ne')
    a.set('awa', 'b13', '123412')
    a.set('awa', '321345', '33342333')

    a.set_copygroup('default', 'qwq')
    a.set('qwq', '345', 'aaaaaa')

    a.to_csv('config.csv')
    a.from_csv('config.csv')
    # a.to_yaml('config.yaml')
    # a.from_yaml('config.yaml')
    # a.to_pickle('config.pkl')
    # a.from_pickle('config.pkl')
    # a.to_json('config.json')
    # a.from_json('config.json')

    print(a.get_str('awa', 'b13'))
    print(a)