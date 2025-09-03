import sys
import os
import tempfile
import time
import subprocess
import socket
import hmac
import hashlib
import base64
from urllib.parse import quote, unquote
from typing import Union
# pip install paramiko		#window库/linux库:ssh操作
import paramiko
# pip install sshtunnel		#window库/linux库:ssh操作
from sshtunnel import SSHTunnelForwarder
# pip install ctypes		#window库/linux库:ssh操作
import ctypes

#当前脚本所在文件夹
scriptDir = os.path.dirname(__file__)+os.sep

# 引用其它python脚本, name-模块名，如: utils.com
def importScript(scriptName:str,scriptPath=None):
	try:
		if(scriptPath==None):scriptPath=scriptDir
		sys.path.append(scriptPath)
		script = __import__(scriptName)
		sys.path.remove(scriptPath)
		return script
	except Exception as e:
		print(f"导入python脚本: {e}")

# 引用其它python脚本, scriptPath-脚本对应文件夹
def importScripts(scriptPath:str):
	try:
		sys.path.append(scriptPath)
		scripts=[]
		def action(name:str,path:str,relPath:str):
			# 去掉扩展名
			lastIndex=name.rfind(".")
			scriptName=name[0:lastIndex]
			# 导入脚本
			try:
				script=__import__(scriptName)
				scripts.append(script)
			except Exception as e:
				print(f"导入python脚本: {e}")
		# 循环读取脚本
		eachFile(scriptPath,action)
		sys.path.remove(scriptPath)
		print(scripts)
		return scripts
	except Exception as e:
		print(f"导入python脚本: {e}")

# 通过子进程运行其它python脚本, file-相对或绝对路径, 如：c:\pys\aa.py
def runScript(file:str):
	try:
		result = subprocess.run(['python', file], capture_output=True)
		print(result.stdout.decode())
	except Exception as e:
		print(f"运行python脚本: {e}")

# 遍历文件夹及子文件夹中所有文件，并调用action, dir-要遍历的文件夹, action-被调用函数(接收fileName-文件名,absDir-所在绝对目录,relDir-所在相对目录). isReadChildren-是否读取子文件夹
def eachFile(dir:str,action,isReadChildren:bool=False,relPath:str=""):
	for name in os.listdir(dir):
		absPath = os.path.join(dir,name)
		if (os.path.isfile(absPath)):
			action(name,dir,relPath)
		else:
			if not isReadChildren: return
			relPatht=os.path.join(relPath,name)+os.sep
			eachFile(absPath+os.sep,action,isReadChildren,relPatht)

# 批量执行python脚本
# action-自定义函数
# configPath-配置所在文件夹
# configName-调用指定配置名称
def eachConfigsAction(action,configPath:str,configName:str=None,args:list=None):
	# 导入ssh配置
	configs=importScripts(configPath)
	if configName==None:
		# 调用所有脚本
		for config in configs:
			action(config,args)
	else:
		for config in configs:
			if(config.__name__==configName):
				action(config,args)

# 批量执行python脚本
# moduleFile-模块文件路径(main为入口函数)
# configPath-配置所在文件夹
# configName-调用指定配置名称
def eachConfigsModule(moduleFile:str,configPath:str,configName:str=None,args:list=None):
	# 加载要执行脚本
	path, filename=os.path.split(moduleFile)
	name,exname=os.path.splitext(filename)
	runScript=importScript(name,path)
	# 调用脚本
	eachConfigsAction(runScript.main,configPath,configName,args)

# 遍历指定文件夹中的配置(python)文件并执行
# moduleFileOrAction-模块文件路径或函数; 模块名-main为入口函数，如: utils.com 或 com; 函数-外部定义
# configsDir-配置文件所在目录
# configName-调用指定配置名称
def eachConfigs(moduleFileOrAction,configsDir,configName:str=None,args:list=None):
	if type(moduleFileOrAction) is str:
		eachConfigsModule(moduleFileOrAction,configsDir,configName,args)
	else:
		eachConfigsAction(moduleFileOrAction,configsDir,configName,args)

# 读取文件, filename-保存文件名, encoding-编码
def readFile(filename, encoding='utf-8'):
	if not os.path.exists(filename): return ""
	with open(filename, "r", encoding=encoding) as file:
		content = file.read()
		return content
	
# 保存文件, filename-保存文件名, content-保存内容, encoding-编码, mode-a添加w重写
def saveFile(filename, content, encoding='utf-8', mode='w'):
    with open(filename, mode, encoding=encoding) as file:
        file.write(content)

# 远程连接ssh服务器并执行命令
def ssh(action,ip,port,username,password,config=None,args=None):
	if ip==None or port==None or username==None or password==None or action==None: return
	# 创建SSH客户端
	client = paramiko.SSHClient()
	# 自动添加主机名和密钥到本地的known_hosts文件
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 	# 连接到远程主机
	client.connect(ip,port,username,password)
	clientEx=SshClient(client)
	# 调用外部函数
	action(clientEx,config,args)
	# 关闭连接
	client.close()

# 打开SSH隧道
# action-被调用函数(无参数)
# ip,port,username,passowrd-SSH连接帐号信息
# remoteHost,remotePort-远程服务器地址和端口
# localHost,localPort-本地主机和端口
def sshForward(action,ip,port,username,password,remoteHost,remotePort,localHost,localPort):
	if ip==None or port==None or username==None or password==None or action==None: return
	# 打开SSH隧道参数
	server = SSHTunnelForwarder(
		ssh_address_or_host=(ip, port),
		ssh_username=username,
		ssh_password=password,
		local_bind_address=(localHost, localPort),
		remote_bind_address=(remoteHost, remotePort)
	)
	# 启动SSH隧道
	server.start()
	if server.is_active:
		print('本地端口{}:{}已转发至远程端口{}:{}'.format(localHost,server.local_bind_port,remoteHost,remotePort))
	else :
		print('本地端口{}:{}转发失败,请重试')
	# 调用外部函数
	action()
	# 关闭连接
	server.close()

# 执行命令(等待执行完成后，才会往后执行)
def cmd(commands:str,isEcho:bool=False):
	try:
		platform = sys.platform
		filename="tempbs"
		callname=""
		encodeing=""
		varcurrentdir=""
	
		if 'linux' in platform:
			filename=filename+".sh"
			callname="bash"
			encodeing="utf-8"
			varcurrentdir="$PWD"
		elif 'darwin' in platform:
			filename=filename+".sh"
			callname="bash"
			encodeing="utf-8"
			varcurrentdir="$PWD"
		elif 'win32' in platform or 'win64' in platform:
			filename=filename+".bat"
			callname="call"
			encodeing="gbk"
			varcurrentdir="%cd%"
		else:
			print("未知操作系统,无法执行命令")
			return None
		
		# 读取临时文件路径
		tempdir = tempfile.gettempdir()
		execfile = os.path.join(tempdir, filename)
		if os.path.exists(execfile): os.remove(execfile)
		# 生成执行脚本
		print('########执行脚本########')
		print(execfile)
		print('########执行中请稍等...########')
		cmd = "@echo "+("on" if isEcho else "off")+"\n"
		cmd += "echo 执行前当前目录: "+varcurrentdir+"\n"
		cmd += commands + '\n'
		cmd += "echo 执行后当前目录: "+varcurrentdir+"\n"
		cmd += 'exit\n'
		with open(execfile, 'w',encoding=encodeing) as f: f.write(cmd)
        # 执行命令
		process = subprocess.Popen(callname+ " " + execfile, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True)
		# 输出结果
		while process.poll() is None:
			line = process.stdout.read()
			if line: print(line,end="")
		# 等待命令执行完成
		returnCode = process.wait()
		if returnCode:
			print(f"########执行错误########\n返回码: {returnCode}")
		else:
			print("########执行完成########")
		# 返回命令执行的结果
		return None
	except Exception as e:
		# 如果命令执行失败，返回错误输出
		print(e)
		return e

# 执行命令(新窗口执行不会阻塞)
def run(commands:str,isEcho:bool=False):
	try:
		# 判断操作系统，根据不同系统设置不同的命令
		if os.name == 'nt':  # 对于Windows
			runcmd = 'start cmd /k "$cmd$"'
			# 读取临时文件路径
			tempdir = tempfile.gettempdir()
			execfile = os.path.join(tempdir, 'tempbs.bat')
		else:  # 对于Unix或Mac
			runcmd = 'xterm -e "$cmd$"'
			# 读取临时文件路径
			tempdir = tempfile.gettempdir()
			execfile = os.path.join(tempdir, 'tempbs.sh')
		if os.path.exists(execfile): os.remove(execfile)
		# 生成执行脚本
		cmd = "@echo "+("on" if isEcho else "off")+"\n"
		cmd += "echo 当前目录: %~dp0\n"
		cmd += commands + '\n'
		cmd += 'exit\n'
		with open(execfile, 'w',encoding="gbk") as f: f.write(cmd)
        # 执行命令
		subprocess.call(runcmd.replace("$cmd$", execfile), shell=True)
		# 返回命令执行的结果
		return None
	except Exception as e:
		# 如果命令执行失败，返回错误输出
		print(e)
		return e

# 切换到管理员模式
def toAdmin(file:str):
	isAdmin=False
	try: isAdmin=ctypes.windll.shell32.IsUserAnAdmin()
	except Exception as e: 
		print(e)
	if isAdmin: 
		return
	if(file=="" or file==None): 
		print("切换到管理员模式时，缺少file参数")
		return
	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, file, None, 1)
	sys.exit()

# 获取本机局域网IP
def GetLanIp():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# 生成数字HmacSha1签名
def HmacSha1(key: Union[str, bytes], text: Union[str, bytes],encoding="utf-8") -> str:
    if isinstance(key, str):
        key = key.encode(encoding)
    if isinstance(text, str):
        text = text.encode(encoding)
    sha1bytes=hmac.new(key, text, hashlib.sha1).digest()
    return base64.b64encode(sha1bytes).decode(encoding)

# 字典:根据Key重新排序keys
def DictSortByKey(obj: dict, reverse=False):
    return {k: obj[k] for k in sorted(obj.keys(), reverse=reverse)}

# 将字典转成Url参数
def DictToUrlParams(obj: dict, safe_chars='') -> str:
	params = []
	for key, value in obj.items():
		if isinstance(value, (list, tuple)):
			params.extend(f"{quote(str(k), safe=safe_chars)}={quote(str(v), safe=safe_chars)}" 
						for v in value for k in [key])
		else:
			params.append(f"{quote(str(key), safe=safe_chars)}={quote(str(value), safe=safe_chars)}")
	return '&'.join(params)

# 将Url参数转成字典
def UrlParamsToDict(query: str) -> dict:
	from urllib.parse import parse_qs
	return {k: v[0] if len(v) == 1 else v 
			for k, v in parse_qs(unquote(query)).items()}


	




# 定义ssh操作类, 命令执行原理：
# 1、第1次执行时，获取之前的执行结果并返回输出，然后执行空命令，获取结束字符串标记
# 2、当执行结果中是否存在结束字符串标记时，结束执行并返回输出
# 3、实例结束时（即最后一次执行完），获取之前的执行结果并返回输出
class SshClient:
	ssh=None
	ftp=None
	chn=None
	# 结束字符串组
	endStrs=None
	# 超时间根据创建连接时间自动生成
	timeout:int=30000
	# 当前命令执行结果
	result:str=""
	# 构造函数
	def __init__(self,ssh):  
		self.ssh=ssh
		self.ftp=ssh.open_sftp()
		startTime=time.time()
		self.chn = ssh.invoke_shell()
		timeout=max((time.time()-startTime)*1000,self.timeout) 
		if timeout>self.timeout: self.timeout=timeout
		self.endStrs=self.readEndStr()
	def __del__(self):
		self.ftp.close()
		self.chn.close()

	# 下载文件
	def get(self,serverFile,localFile):
		try:
			print(f"下载文件: {serverFile} -> {localFile}")
			if os.path.exists(localFile):
				try:os.remove(localFile)
				except Exception as ex: pass
			rst=self.ftp.get(serverFile,localFile)
			print(rst)
		except Exception as e:
			print(e)

	# 下载文件
	def getDir(self, serverDir, localDir):
		try:
			print(f"下载文件夹: {serverDir} -> {localDir}")
			for name in self.ftp.listdir(serverDir):
				serverPath=serverDir+"/"+ name
				serverObj=self.ftp.stat(serverPath)
				# 查看文档linux-st_mode为2字节aaaabbbcccdddeee, 其中aaaa代表文件类型, 0100-目录
				if serverObj.st_mode>>12==4:
					if not os.path.exists(localPath): os.mkdir(localPath)
					self.getDir(serverPath,localPath)
				else:
					localPath=localDir+"\\"+name
					self.get(serverPath, localPath)				
		except Exception as e:
			print(e)

	# 上传文件
	def put(self,localFile,serverFile):
		try:
			print(f"上传文件: {localFile} -> {serverFile}")
			try:self.ftp.remove(serverFile)
			except Exception as ex: pass
			rst=self.ftp.put(localFile,serverFile)
			print(rst)
		except Exception as e:
			print(e)

	# 上传文件夹
	def putDir(self,localDir:str,serverDir:str):
			localDir=localDir.rstrip(os.sep)+os.sep
			serverDir="" if serverDir=="" else serverDir.rstrip(os.sep)+os.sep
			print(f"上传文件夹: {localDir} -> {serverDir}")
			dic={}
			def action(name,absPath,relPath):
				relPathT=relPath.replace(os.sep,"/")
				if dic.get(relPathT,None)==None:
					dic[relPathT]=True
					try:self.ftp.mkdir(relPathT)
					except Exception as ex: 
						pass
				self.put(absPath+name, relPathT+name)
			eachFile(localDir,action,True,serverDir)

	# 读取输入提示符
	def readEndStr(self):
		# 读取信息并打印
		output=self.readResult()
		print(output,end="")
		for i in range(0,3):
			# 尝试读取提示符
			outputx=output.replace("\r","\n")
			labels=outputx.split("\n")
			label=labels[len(labels)-1]
			# 读取信息并打印
			output=self.readResult(self.timeout);
			# 非空则二次尝试读取提示符
			if output!="":
				print(output,end="")
				rst=output.replace("\r","\n")
				labels=rst.split("\n")
				label=labels[len(labels)-1]
			# 去除提示符中的数径
			labelArr=label.split("~")
			if len(labelArr)==2:return labelArr
			# 去除提示符中的数径
			labelArr=label.split("/")
			if len(labelArr)==2:return labelArr
		# 扔出错误
		raise Exception("找不到提示符")
		return None
	
	# 执行命令
	def cmd(self,config):
		# 使用subprocess.Popen来启动ssh命令
		proc = subprocess.Popen(['ssh', '-o', 'StrictHostKeyChecking=no', config.username + '@' + config.ip],
								stdin=subprocess.PIPE,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE, text=True)
		time.sleep(3)
		# 发送密码
		proc.stdin.write(config.password + '\n')
		proc.stdin.flush()  # 清空输入缓冲区
	
		# 读取输出
		stdout, stderr = proc.communicate()
	
		# 打印输出结果
		print(stdout.decode())

	# 执行命令
	def cmd2(self,config):
		# 创建一个新的cmd窗口
		process = subprocess.Popen(['cmd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
		# 构建SSH连接命令
		cmd = 'ssh {username}@{host}'.format(username=config.username, host=config.ip)
		process.stdin.write(cmd + '\n')
		process.stdin.flush()
		cmd = config.password
		process.stdin.write(cmd + '\n')
		process.stdin.flush()


	# 执行命令,缺陷：命令完成需要确认时，由于找不到提示符，会导致进入死循环
	def cmd(self):
		while True:
			inputStr=input()
			cmd=inputStr.strip("\n")
			sys.stdout.write("\033[1A\033[1000C\033["+str(len(cmd))+"D")
			if cmd=="exit":break
			self.run(cmd)
	# 执行命令
	def run(self,cmd):
		self.chn.send(cmd+'\n')
		while True:
			output=self.readResult(60000)
			print(output,end="")
			if self.isEnd(output): break
		return
	# 是否为结束提示符
	def isEnd(self,output):
		# 将输出添加到结果中
		self.result+=output
		# 检测结果中是否包含结束提示符
		start=self.endStrs[0]
		end=self.endStrs[1]
		index=self.result.rfind('\n')
		if index==-1:
			index=self.result.rfind('\r')
		index=index + 1
		line=self.result[index:]
		ok=line[len(line)-len(end):]==end and start in line
		# 当前命令执行结束时清空结果
		if ok:self.result=""
		return ok

	# 读取执行命令结果
	# timeout-超时时间（毫秒）
	def readResult(self,timeout:int=0):
		if timeout==0:
			while True:
				output=self.chn.recv(256).decode('utf-8','ignore')
				if output!="": return output
		else:
			endTime=time.time()+timeout/1000
			while True:
				output=self.chn.recv(256).decode('utf-8','ignore')
				if output!="" or time.time()>endTime: return output

	

