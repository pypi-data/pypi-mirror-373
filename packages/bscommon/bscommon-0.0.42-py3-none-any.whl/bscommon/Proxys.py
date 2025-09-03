import time
#pip install pysocks
import socks
import socket
import json as Json
import requests
from requests.exceptions import RequestException
import Com
import ThreadSafe


def GetProxyConfigsByProxyscrape(filter=None):
    res=requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=cn&proxy_format=protocolipport&format=json")
    json=Json.loads(res.text)
    if filter is None: filter=lambda t:True
    proxys=[{"ip":it["ip"],"port":it["port"],"protocol":it["protocol"],"ssl":it["ssl"],"user":None,"password":None} for it in json["proxies"]]
    proxys=[it for it in proxys if filter(it)]
    for proxy in proxys:
        protocol=proxy["protocol"]
        isRun,elapsed=TestSockProxy(proxy["ip"],proxy["port"],30)
        proxy["runTcp"]=isRun
        proxy["runTcpElapsed"]=elapsed
        isRun,elapsed=TestHttpProxy(protocol,proxy["ip"],proxy["port"],proxy["user"],proxy["password"],30,isGlobal=True)
        proxy["runHttp"]=isRun
        proxy["runHttpElapsed"]=elapsed
    return proxys

def GetProxyConfigsByProxyQGNet(filter=None):
    res=requests.get("https://exclusive.proxy.qg.net/replace?key=30493592&num=1&area=&isp=0&format=json&distinct=true&keep_alive=1440")
    json=Json.loads(res.text)
    if filter is None: filter=lambda t:True
    proxys=[{"ip":it["server"].split(":")[0],"port":int(it["server"].split(":")[1]),"protocol":"socks5","ssl":True,"user":None,"password":None} for it in json["data"]["ips"]]
    proxys=[it for it in proxys if filter(it)]
    for proxy in proxys:
        protocol=proxy["protocol"]
        isRun,elapsed=TestSockProxy(proxy["ip"],proxy["port"],30)
        proxy["runTcp"]=isRun
        proxy["runTcpElapsed"]=elapsed
        isRun,elapsed=TestHttpProxy(protocol,proxy["ip"],proxy["port"],proxy["user"],proxy["password"],30,isGlobal=True)
        proxy["runHttp"]=isRun
        proxy["runHttpElapsed"]=elapsed
    return proxys

# 快代理提供服务：https://www.kuaidaili.com/
def GetProxyConfigsByProxyKuaiDaiLi(filter=None):
    params=Com.DictSortByKey({
        "secret_id":"ora1ncsho449fq2mzk7w",
        "num":1,
        "format":"json",
        "sep":1,
        # "f_auth":1,
        # "generateType":1,
        # "f_et":1,
        "sign_type":"hmacsha1",
        "timestamp":int(time.time())
    })
    paramsStr=Com.DictToUrlParams(params)
    urlpath="/api/getdps/?"+paramsStr
    rawStr="GET"+urlpath
    scretKey="tf209eeg5m4qgpwf2mc3lxjj6tg0imvg"
    res=requests.get("https://dps.kdlapi.com"+urlpath+"&signature="+Com.HmacSha1(scretKey,rawStr))
    json=Json.loads(res.text)
    if filter is None: filter=lambda t:True
    proxys=[{"ip":it.split(":")[0],"port":int(it.split(":")[1]),"protocol":"socks5","ssl":True,"user":None,"password":None} for it in json["data"]["proxy_list"]]
    proxys=[it for it in proxys if filter(it)]
    for proxy in proxys:
        protocol=proxy["protocol"]
        isRun,elapsed=TestSockProxy(proxy["ip"],proxy["port"],30)
        proxy["runTcp"]=isRun
        proxy["runTcpElapsed"]=elapsed
        isRun,elapsed=TestHttpProxy(protocol,proxy["ip"],proxy["port"],proxy["user"],proxy["password"],30,isGlobal=True)
        proxy["runHttp"]=isRun
        proxy["runHttpElapsed"]=elapsed
    return proxys


def TestSockProxy(ip, port, timeout=5):
    addr=f"{ip}:{str(port)} :"
    startTime=time.time()
    elapsed=0
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        startTime =  time.time()
        sock.connect((ip, port))
        elapsed = time.time() - startTime
        print(addr+f"成功连接({elapsed})")
        sock.close()
        return True,elapsed
    except Exception as e:
        elapsed = time.time() - startTime
        print(addr+f"无法连接({elapsed}), {str(e)}")
        return False,elapsed

# 测试单个代理的可用性(格式: http://ip:port 或 http://user:pass@ip:port)
# protocol: 协议
# ip: IP地址
# port: 端品
# timeout: 超时时间(秒)
# testUrl: 检测网址
# return: (是否成功, 响应时间, 错误信息)
def TestHttpProxy(protocol,ip,port,user=None,password=None,timeout=5,testUrl="https://api.304cc.cc/sffl/tableconfig.json",isGlobal=True):
    addr=f"{ip}:{str(port)}"
    addrMsg=addr+": "
    
    headers={'User-Agent': 'Mozilla/5.0'}
    elapsed=0
    startTime=time.time()
    try:
        if isGlobal:
            # 设置全局代理
            proxyType= socks.SOCKS4 if protocol=="socks4" else (socks.SOCKS5 if protocol=="socks5" else socks.HTTP)
            socks.set_default_proxy(proxyType, ip, port)
            socket.socket = socks.socksocket
            response = requests.get(testUrl,timeout=timeout,headers=headers)
        else:
            proxy = f"{protocol}://"+("" if user is None else f"{user}:{password}@")+addr
            proxies = {'http':proxy,'https':proxy}
            response = requests.get(testUrl,timeout=timeout,headers=headers,proxies=proxies)
        elapsed = time.time() - startTime
        print(addrMsg+f"连接成功({str(elapsed)}), 状态码{str(response.status_code)}, 内容{response.text}")
        return True,elapsed
    except Exception as e:
        elapsed = time.time() - startTime
        print(addrMsg+f"无法连接({str(elapsed)}), {str(e)}")    
        return False,elapsed


def GetProxyConfigs():
    l=[{"ip":None,"port":None,"protocol":None,"ssl":None,"user":None,"password":None}]
    lst=ThreadSafe.List(l)
    return lst


if __name__ == "__main__":

    # print("指定代理检测")
    # proxyArr=["8.218.116.162",1080,"socks5"]
    # proxyArr=["61.184.8.27",20677,"socks5"]
    # proxyArr=["119.3.113.151",9094,"http"]
    # proxyArr=["117.74.65.207",80,"socks4"]
    # proxyArr=["58.18.39.58",10800,"socks4"]
    # proxyArr=["127.0.0.1",1080,"socks4"]
    # proxyArr=["127.0.0.1",1080,"socks5"]
    # TestHttpProxy(proxyArr[2],proxyArr[0],proxyArr[1],30,isGlobal=False)
    # TestSockProxy(proxyArr[0],proxyArr[1],30)
    # exit()


    print("Proxyscrape代理检测...")
    # proxys=GetProxyConfigsByProxyscrape(lambda p:p if p["ssl"] and p["protocol"]=="socks4" else None)
    # proxys=GetProxyConfigsByProxyQGNet()
    proxys=GetProxyConfigsByProxyKuaiDaiLi()
    print("Proxyscrape代理检测结果:")
    for proxy in proxys:
        if proxy["runHttp"]:
            print(f"{proxy["protocol"]}://{proxy["ip"]}:{str(proxy["port"])} - http正常")
        if proxy["runTcp"]:
            print(f"{proxy["protocol"]}://{proxy["ip"]}:{str(proxy["port"])} - sock正常")
