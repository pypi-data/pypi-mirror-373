import os
import sys
scriptDir = os.path.dirname(__file__)+os.sep
rootDir=scriptDir+".."+os.sep
sys.path.append(rootDir)
from src.bscommon import Com
from src.bscommon import Ssh
sys.path.remove(rootDir)




# Ssh.init(scriptDir)
# Ssh.sshHostRun("setup",args={"bs9.top"})






cmds=[]
cmds.append("cd /Volumes/xmac/projects/java_jiangge/server")
cmds.append("export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-8.jdk/Contents/Home")
cmds.append("/opt/homebrew/bin/mvn clean package -Dmaven.test.skip=true -s /Volumes/xmac/java/maven/dybsettings.xml -Dmaven.repo.local=/Volumes/xmac/java/maven/repository")
Com.cmd(str.join("\n",cmds))
