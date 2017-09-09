#_*_coding:utf-8_*_
#脚本可以可以检测cpu利用率，如果CPU利用率高的话，就触发报警模式
import psutil
import os
import time
#获取当前运行的pid
p1=psutil.Process(os.getpid())
while True:
    file = open('test.txt','a')
    memory_rate = psutil.virtual_memory().percent  #内存占用率
    cpu_rate = psutil.cpu_percent(interval=1.0) #cpu占用率
    file.write("memory_rate="+str(memory_rate)+" "+"cpu_rate="+str(cpu_rate)+"\n")
    file.close()
    time.sleep(2)
