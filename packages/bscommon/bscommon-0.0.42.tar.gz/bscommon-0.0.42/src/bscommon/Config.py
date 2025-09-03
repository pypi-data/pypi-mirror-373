import os
import json

# 读取配置文件
def read(filePath):
    global ReadConfigFilePath
    ReadConfigFilePath=filePath
    if os.path.exists(filePath) is False:
        return json.loads("{}")
    with open(filePath, 'r') as file:
        text=file.read()
        if text=="":text="{}"
        return json.loads(text)
    
# 保存配置文件，如果filePath为None，则保存到readConfig中读取的文件中
def save(config, filePath=None):
    global ReadConfigFilePath
    if filePath is None:filePath=ReadConfigFilePath
    with open(filePath, 'w') as file:
        text=json.dumps(config)
        file.write(text)
        