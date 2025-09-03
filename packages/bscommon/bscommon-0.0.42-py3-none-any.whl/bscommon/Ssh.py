import os
from . import Com

#当前脚本所在文件夹
scriptDir = os.path.dirname(__file__)+os.sep

# 初使化, mainDir引用当前文件所对应的脚本所在文件夹
def init(mainDirP):
	global mainDir
	mainDir=mainDirP

# 连接ssh并批量执行python脚本
# action-自定义函数
# configPath-ssh配置所在文件夹
# configName-调用指定配置名称
def sshRunAction(action,configPath:str,configName:str=None,args:list=None):
	def actionT(config,args):
		Com.ssh(action,config.ip,config.port,config.username,config.password,config,args)
	if type(args) == set:args=list(args)
	Com.eachConfigsAction(actionT,configPath,configName,args)

# 连接ssh并批量执行python脚本
# name-模块名(main为入口函数)，如: utils.com 或 com
# configPath-ssh配置所在文件夹
# configName-调用指定配置名称
def sshRun(name:str,configPath:str,configName:str=None,args:list=None):
	# 加载要执行脚本
	runScript=Com.importScript(name,mainDir)
	# 去除包名
	for dir in name.split("."):
		try:
			obj=getattr(runScript,dir)
		except Exception as e:
			obj=None
		if obj!=None: runScript=obj
	# 调用脚本
	sshRunAction(runScript.main,configPath,configName,args)
		
# 管理节点：连接ssh并执行python脚本
# nameOrAction-模块名/函数; 模块名-main为入口函数，如: utils.com 或 com; 函数-外部定义
def sshManageRun(nameOrAction,configName:str=None,args:list=None):
	dir=mainDir+'configs'+os.sep+'managenodes'+os.sep
	if type(nameOrAction) is str:
		sshRun(nameOrAction,dir,configName,args)
	else:
		sshRunAction(nameOrAction,dir,configName,args)

# 工作节点：连接ssh并执行python脚本
# nameOrAction-模块名/函数; 模块名-main为入口函数，如: utils.com 或 com; 函数-外部定义
def sshWorkRun(nameOrAction,configName:str=None,args:list=None):
	dir=mainDir+'configs'+os.sep+'worknodes'+os.sep
	if type(nameOrAction) is str:
		sshRun(nameOrAction,dir,configName,args)
	else:
		sshRunAction(nameOrAction,dir,configName,args)

# 主机节点（即普通节点）：连接ssh并执行python脚本
# nameOrAction-模块名/函数; 模块名-main为入口函数，如: utils.com 或 com; 函数-外部定义
def sshHostRun(nameOrAction,configName:str=None,args:list=None):
	dir=mainDir+'configs'+os.sep+'hosts'+os.sep
	if type(nameOrAction) is str:
		sshRun(nameOrAction,dir,configName,args)
	else:
		sshRunAction(nameOrAction,dir,configName,args)

