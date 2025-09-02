#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/2/27 13:34
@Author  : dmj-11740
@File    : excel_read.py
@Software: PyCharm
@desc    : 
"""
import json
import os
import warnings


class BList(list):

    def to_excel(
        self,
        file_name,
        sheet_name: str = "sheet1",
        mode: str = "w",
    ):
        try:
            import pandas
        except:
            raise Exception("pandas not found!")
        data = []
        have_convert = False
        for key, value in self[0].items():
            if isinstance(value, dict) or isinstance(value, list):
                have_convert = True
                break
        if have_convert:
            for item in self:
                for key, value in item.items():
                    if isinstance(value, dict) or isinstance(value, list):
                        item[key] = json.dumps(value, ensure_ascii=False)
                data.append(item)
        pad = pandas.DataFrame(data or self)
        mode = "w" if not os.path.exists(file_name + ".xlsx") else mode
        with pandas.ExcelWriter(
            file_name + ".xlsx",
            mode=mode,
            engine="xlsxwriter",
            # options={"strings_to_urls": False},
            engine_kwargs={"options": {"strings_to_urls": False}},
        ) as writer:
            pad.to_excel(writer, index=False, sheet_name=sheet_name)


class ExcelRead:
    def __init__(self, file_path, sheet_name=0, header=0, **kwargs):
        """
            读取Excel
        :param file_path:  文件路径
        :param sheet_name: 表名
        :param kwargs:
        """
        self.path = file_path
        self.sheet_name = sheet_name
        self.header = header
        self._sheet_names = None
        self.__values = None
        self.__sheet_name_bck = None

    @property
    def values(self) -> BList:
        # 读取Excel文件
        try:
            import pandas
        except:
            raise Exception("pandas not found!")
        if self.__values:
            return self.__values
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"找不到文件:{self.path}")
        # excel_name = self.path.rsplit("/", 1)[1] if "/" in self.path else self.path
        # loading = Loading(f"文件[{excel_name}]")
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("ignore", ResourceWarning)
            df = pandas.read_excel(
                self.path, sheet_name=self.sheet_name, dtype="str", header=self.header
            )
        # 替换Excel表格内的空单元格，否则在下一步处理中将会报错
        df.fillna("", inplace=True)
        df_list = []
        for row in df.index.values:
            # loc为按列名索引 iloc为按位置索引，使用的是 [[行号], [列名]]
            df_line = df.loc[row, df.columns.values.tolist()].to_dict()
            # print(df.loc[row, df.columns.values.tolist()])
            for k, v in df_line.items():
                if v == "true" or v == "True":
                    df_line[k] = True
                elif v == "false" or v == "False":
                    df_line[k] = False
                # if not isinstance(v, str):
                #     df_line[k] = str(v)
            df_list.append(df_line)
        # loading.stop()
        self.__values = BList(df_list)
        return self.__values

    @property
    def values_str(self) -> list:
        json_str = []
        for value_json in self.values:
            json_str.append(
                {key: value.__str__() for key, value in value_json.mow_list()}
            )
        return json_str

    def only_index(self, index: str, *args) -> dict:
        if not self.__values:
            self.__values = self.values
        index = [index]
        index.extend(args)
        item = {}
        for val in self.__values:
            keys = "###".join([val.get(k, "") for k in index])
            assert (
                keys
            ), f"有值为空:{val[list(val.keys())[0]]}, {val[list(val.keys())[1]]}"
            if keys not in item:
                item[keys] = []
            item[keys].append(val)
        return item

    @property
    def values_all(self) -> BList:
        try:
            import pandas
        except:
            raise Exception("pandas not found!")
        excel_file = pandas.ExcelFile(self.path)
        self._sheet_names = excel_file.sheet_names
        items = BList()
        self.__sheet_name_bck = self.sheet_name
        for sheet_name in self._sheet_names:
            self.sheet_name = sheet_name
            item = self.values
            items.extend(item)
        self.sheet_name = self.__sheet_name_bck
        return items

