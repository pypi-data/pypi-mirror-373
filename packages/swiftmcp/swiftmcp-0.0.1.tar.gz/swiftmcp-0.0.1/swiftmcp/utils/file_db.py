#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2024 yaqiang.sun.
# This source code is licensed under the license found in the LICENSE file
# in the root directory of this source tree.
#########################################################################
# Author: yaqiangsun
# Created Time: 2024/09/09 17:22:40
########################################################################


import json
import yaml
from miniolite.FileSQLite import FileSQLite

class AgentFileDB(object):
    def __init__(self,db_path="tmp/test.db"):
        pass
        # initalize the database
        self.file_db = FileSQLite(db_path)
    def create_folder(self):
        # create folder
        self.file_db.force_add_folder("/data/flows")
        self.file_db.force_add_folder("/data/flows_simple")
        self.file_db.force_add_folder("/data/tools")
        self.file_db.force_add_folder("/data/tools_simple")
    create_folder()


    def delete_file(self,path):
        self.file_db.delete_file(path)

    def list_file(self,path):
        name_list = self.file_db.list_files(path)
        return name_list

    def write_json(self,json_obj,file_path):
        json_str = json.dumps(json_obj)
        self.file_db.add_file(file_path,content=json_str)
        pass

    def read_json(self,path):
        try:
            file = self.file_db.read_file(path)
            data = json.loads(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件不存在或为空，则初始化为空列表/字典
            data = {}
        return data

    def write_yml(self,json_obj,file_path):
        json_str = json.dumps(json_obj)
        self.file_db.add_file(file_path,content=json_str)
    def load_yaml_file(self,file_path: str, ignore_error: bool = True):
        
        file = self.file_db.read_file(file_path)
        try:
            yaml_content = yaml.safe_load(file)
            if not yaml_content:
                raise ValueError(f'YAML file {file_path} is empty')
            return yaml_content
        except Exception as e:
            raise ValueError(f'Failed to load YAML file {file_path}: {e}')

if __name__ == "__main__":
    agent_db = AgentFileDB()
    json_obj = {
        "demo":"test"
    }
    agent_db.create_folder()
    # write_json(json_obj=json_obj,file_path="/data/tools/out.json")
    data = agent_db.read_json(path="/data/tools/out.json")
    print(data)

    pass