import os
import sys
scriptDir = os.path.dirname(__file__)+os.sep
rootDir=scriptDir+".."+os.sep
sys.path.append(rootDir)
from src.bscommon import Com
from src.bscommon import Ssh
sys.path.remove(rootDir)




params=Com.DictSortByKey({
    "secret_id":"o1fjh1re9o28876h7c08",
    "sign_type":"hmacsha1",
    "timestamp":1555069980
})
paramsStr=Com.DictToUrlParams(params)
urlpath="/api/getdps/?"+paramsStr
rawStr="GET/api/getorderexpiretime?"+paramsStr
scretKey="jd1gzm6ant2u7pojhbtl0bam0xpzsm1c"
res="https://dps.kdlapi.com"+urlpath+"&signature="+Com.HmacSha1(scretKey,rawStr)

print(rawStr)
print(res)
exit()

# GET/api/getorderexpiretime?secret_id=o1fjh1re9o28876h7c08&sign_type=hmacsha1&timestamp=1555069980
# GET/api/getorderexpiretime?secret_id=o1fjh1re9o28876h7c08&sign_type=hmacsha1&timestamp=1555069980
# https://dps.kdlapi.com/api/getdps/?secret_id=o1fjh1re9o28876h7c08&sign_type=hmacsha1&timestamp=1555069980&signature=SMRu2P5xWQm+6bYlBji4xriEL+I=
#Ssh.init(scriptDir)
# Ssh.sshHostRun("setup",args={"bs9.top"})






cmds=[]
cmds.append("cd /Volumes/xmac/projects/java_jiangge/server")
cmds.append("export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-8.jdk/Contents/Home")
cmds.append("/opt/homebrew/bin/mvn clean package -Dmaven.test.skip=true -s /Volumes/xmac/java/maven/dybsettings.xml -Dmaven.repo.local=/Volumes/xmac/java/maven/repository")
Com.cmd(str.join("\n",cmds))
