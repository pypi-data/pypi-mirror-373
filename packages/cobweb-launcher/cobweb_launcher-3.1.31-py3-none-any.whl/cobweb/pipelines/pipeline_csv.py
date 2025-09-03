import os
import csv

from cobweb.base import BaseItem
from cobweb.pipelines import Pipeline


class CSV(Pipeline):

    def __init__(self, *args, **kwargs):
        super(CSV, self).__init__(*args, **kwargs)
        self.log_path = rf"{os.getcwd()}\{self.project}\{self.task}\%s.csv"

    def build(self, item: BaseItem):
        return item.to_dict

    def upload(self, table, datas):
        fieldnames = datas[0].keys()
        file_path = self.log_path % table
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode='a', encoding='utf-8', newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:  # 判断文件是否为空
                writer.writeheader()
            writer.writerows(datas)
