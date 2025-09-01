#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
def start():
    print("import successful")
# constants
 

__author__ = 'shancx'
 
__author_email__ = 'shancx@126.com'


import json
import os
from cryptography.fernet import Fernet, InvalidToken
from shancx import crDir
class UserManager:
    def __init__(self, storage_file=None, info=None):
        self.storage_file = storage_file
        self.usersdata = info
        self.data = self._load_or_initialize_data()
        self.cipher = Fernet(self.data["key"])

    def _load_or_initialize_data(self):
        if self.storage_file and os.path.exists(self.storage_file) and os.path.getsize(self.storage_file) > 0:
            with open(self.storage_file, "r") as file:
                try:
                    data = json.load(file)
                    if "key" in data and "users" in data:
                        return data
                except json.JSONDecodeError:
                    print("错误: 数据文件损坏，请删除文件并重新运行。")
        key = Fernet.generate_key().decode("utf-8")
        return {"key": key, "users": {}} if self.usersdata is None else self.usersdata
    def _save_data(self):
        if self.storage_file:
            crDir(self.storage_file)
            with open(self.storage_file, "w") as file:
                json.dump(self.data, file, indent=4)

    def add_user(self, user_id, secret_value):
        encrypted_secret = self.cipher.encrypt(secret_value.encode("utf-8")).decode("utf-8")
        self.data["users"][user_id] = {"s": encrypted_secret}
        self._save_data()
        print(f"用户 {user_id} 的秘钥已成功保存。")

    def get_user(self, user_id):
        user_data = self.data["users"].get(user_id)
        if user_data:
            try:
                decrypted_secret = self.cipher.decrypt(user_data["s"].encode("utf-8")).decode("utf-8")
                return json.loads(decrypted_secret)
            except InvalidToken:
                print("错误: 秘钥解密失败。")
        else:
            print(f"未找到用户 {user_id} 的数据。")
        return None 
import requests
def sendMESplus(message,base = None):
    webHookUrl = f'{base[1]}{base[0]}'  
    response=None
    try:
        url=webHookUrl
        headers = {"Content-Type":"application/json"}
        data = {'msgtype':'text','text':{"content":message}}
        res = requests.post(url,json=data,headers=headers)
    except Exception as e:
        print(e)
 