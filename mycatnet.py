#_*_coding:utf-8_*_
import sys
import socket
import getopt
import threading
import subprocess

#定义一些全局变量
listen = False
command = False
upload =False
execute = ""
target =""
upload_destination =""
port =9999
#上面定义个是设定了一些全局变量‘

#客户端发送的函数，主要是用来向客户端发送一些数据的
#这里要理清楚，谁是客户端，谁是服务端
def client_sender(buffer):
	client =socket.socket(socket.AF_INET,socket.SOCK_STREAM)	#使用的是标准的ipv4协议来进行套接字的创建
	try:
		#连接目标主机
		client.connect((target,port))	#连接目标，和目标端口   本地的主机连接上了这个
		if len(buffer):					#查询buffer中的数据长度
			client.send(buffer)			#向目标主机发送数据
		while True:
			recv_len = 1
			response = ""
			while recv_len:
				date = client.recv(4096)	#从目标主机接受数据，显然，这里的目标主机并没有给我们返回数据
				recv_len =len(date)			#判断一些接受数据的长度
				response+=date				#准备响应的数据
				
				if recv_len < 4096:		#第一次接受数据转跳出来
					break
			print 
			print response
			
			#等待输入更多
			buffer = raw_input("")	#客户机，一直在输入
			buffer+="\n"
			
			#发送出去
			client.send(buffer)		#将在客户端输入的数据发送到了我们的目标主机
	except:
		print "[*]异常退出"
		client.close()
def client_handler(client_socket):
	global upload
	global execute
	global command
	
	if len(upload_destination):
		#读取所有的字符串并写下目标
		file_buffer=""
		#持续的读数据，直到没有符合的数据
		while True:
			date =client_socket.recv(1024)
			if not date:
				break
			else:
				file_buffer+=date
				
		#现在将我们接受到的数据写下来
		try:
			file_descriptor = open(upload_destination,"wb")
			file_descriptor.write(file_buffer)
			file_descriptor.close()
			#确认文件已经写出来了
			client_socket.send("成功的保存文件到%s \r\n"%upload_destination)
		except:
			client_socket.send("失败的保存文件")
	
	#检查命令执行
	if len(execute):
		#运行命令
		output = run_command(execute)
		client_socket.send(output)
	if command:
		print "命令"
		while True:
			client_socket.send("<BHP:#>")
			#接受文件，直到发现换行符
			cmd_buffer = ""
			while "\n" not in cmd_buffer:
				cmd_buffer+=client_socket.recv(1024)
				response = run_command(cmd_buffer)
				client_socket.send(response)

def server_loop():
	global target
	#如果没有定义目标，那么我们监听所有的端口
	if not len(target):
		target ="0.0.0.0"
	server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	server.bind((target,port))
	server.listen(5)
	print "[*]监听来自在%s:%d"%(target,port)
	while True:
		client_socket ,addr = server.accept()	#本机接受外来客户机的连接，然后把处理程序仍给client_handler函数
		#多线程处理
		client_thread = threading.Thread(target=client_handler,args=(client_socket,))
		client_thread.start()

def run_command(command):
	#换行
	command = command.rstrip()
	#运行命令，并返回输出结果
	try:
		output = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
	except:
		output = "执行命令失败"
	return output


#创建主函数，来处理命令行参数
def usage():
	print "网络工具"
	print 
	print "使用格式：mynetcat.py -t 目标主机 -p 端口号"
	print "-l --listen  -监听在正在链接的主机：端口"
	print "-e --execute=file_to_run  执行上传的文件"
	print "-c --command      初始化一个命令脚本"
	print "-u --upload=destination --上传一个链接文件"
	print
	print
	sys.exit(0)

def main():
	global listen
	global port
	global execute
	global command
	global upload_destination
	global target
	#判断是否输入了数据
	if not len(sys.argv[1:]):	#检查输入的参数是否是多个，如果只是脚本名称，那么就提示信息
		usage()
	try:
		opts,args=getopt.getopt(sys.argv[1:],"hle:t:p:cu:",["help","listen","execute","target","port","command","upload"])
	except getopt.GetoptError as err:
		print str(err)
		usage()
	for o,a in opts:
		if  o in ("-h","--help"):
			usage()
		elif o in ("-l","--listen"):
			listen = True
		elif o in ("-e","--execute"):
			execute = a
		elif o in ("-c","--commandshell"):
			command = True
		elif o in ("-u","--upload"):
			upload_destination =a
		elif o in ("-t","--target"):
			target =a
		elif o in ("-p","--port"):
			prot=a
		else:
			assert False,"未知的指令"
	#判断我们是进行监听还是从标准输入发送数据
	if not listen and len(target) and port>0:
		#从命令行中读取内存中的数据
		#这里将阻塞，所以不再向标准输入发送crtl+d
		buffer =sys.stdin.read()   
		#发送数据
		client_sender(buffer)
	#开始监听并准备上传文件、执行命令
	#放置一个反弹shell
	#取决于上面命令行选项
	if listen:
		server_loop()
main()	#开始执行main函数

