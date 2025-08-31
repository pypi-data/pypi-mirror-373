import json


# 读取配置文件
def readConfig(filePath):
    global ReadConfigFilePath
    ReadConfigFilePath=filePath
    with open(filePath, 'r') as file:
        return json.load(file)
    
# 保存配置文件，如果filePath为None，则保存到readConfig中读取的文件中
def saveConfig(strJson, filePath=None):
    global ReadConfigFilePath
    if filePath is None:filePath=ReadConfigFilePath
    with open(filePath, 'w') as file:
        json.dump(strJson, file)
