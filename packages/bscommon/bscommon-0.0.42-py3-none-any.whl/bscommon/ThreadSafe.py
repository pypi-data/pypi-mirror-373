import threading
from concurrent.futures import ThreadPoolExecutor
import os
import re
import time
import random

class Object:
    def __init__(self, initValue=0):
        self.lock = threading.Lock()
        self.data = initValue
    
    @property
    def value(self):
        with self.lock:
            return self.data
    
    @value.setter
    def value(self, newValue):
        with self.lock:
            self.data = newValue

class List:
    def __init__(self,initArray=[]):
        self.data = initArray
        self.lock = threading.Lock()
    
    def push(self,item):
        with self.lock:
            return self.data.append(item)

    def pop(self,index=0):
        with self.lock:
            return self.data.pop(index)
        
    def get(self,index):
        with self.lock:
            return self.data[index]
        
    def copy(self):
        with self.lock:
            return self.data.copy()

    def count(self):
        with self.lock:
            return len(self.data)




if __name__ == "__main__":
    # lst=List([33,32,12,34,36,30,12])
    # print(lst.count())
    # lst.pop(-1)
    # print(lst.copy())

    # obj=Object(1)
    # obj.value=2
    # print(obj.value)

    lst=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    lst=List(lst)
    def test(t):
        time.sleep(random.uniform(0.1,1))
        print(str(t)+","+str(lst.pop()))
        return t

    with ThreadPoolExecutor(max_workers=4) as executor:
        t=[1,2,3,4,5]
        arr=executor.map(test,t)
        print(arr)
