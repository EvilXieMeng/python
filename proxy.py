#_*_coding:utf-8_*_
import socket
import sys
import threading

#server_loop函数接受到了从客户端传送来的一些信息后，将这些信息做了一些处理
def server_loop(local_host,local_port,remote_host,remote_port,receive_first):
	server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)	#创建了一个套接字对象
	try:
		server.bind((local_host,local_port))	#绑定了本机的端口，也就是说在运行这个程序的电脑上开始了一个监听活动
	except:
		print "[!!]失败的监听%s：%d"%(local_host,local_port)
		print "[!!]检测监听是否正确"
		sys.exit(0)
	print "[*]成功的在本机的%s:%d监听"%(local_host,local_port)
	server.listen(5)	#表示监听的最大数目，到这里还没有用到远程主机和远程端口的信息
	while True:
		client_socket,addr = server.accept()		#等待接受，接受到了某一个客户端的连接
		print "[==>]接受到来自%s：%d的连接"%(addr[0],addr[1])
		#等待一个连接后，将处理这个连接扔给proxy_handler函数来处理
		proxy_thread = threading.Thread(target=proxy_handler,args=(client_socket,remote_host,remote_port,receive_first))	#在本机运行的程序将这个连接套接字扔给了client_socket来处理
		proxy_thread.start()
def proxy_handler(client_socket,remote_host,remote_port,receive_first):  #如果有别的地方的机器连接到了本地的服务程序，那么我们就连接运行上的远程主机
	#连接远程主机
	remote_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)	 #创建一个套接字
	remote_socket.connect((remote_host,remote_port))  #连接上远程的主机，下面我们来看看连接上了远程主机后，做了一些什么事情
	if receive_first:	#判断是否是需要接受数据
		remote_buff = receive_from(remote_socket)	
		hexdump(remote_buff)
		#发送我们的响应处理
		remote_buff = response_handler(remote_buff)
		#如果我们有数据传递给本地的客户端，发送它
		if len(remote_buff):
			print "[<==]发送了%d字节的数据到本机"%len(remote_buff)
			client_socket.send(remote_buff)		#这里是发给连接方
	while True:
		local_buffer = receive_from(client_socket)   #接受本地传来的数据数据，一直循环等待本地发送过来数据
		if len(local_buffer):
			print "[<==]接受%d字节的数据来自本地"%len(local_buffer)
			hexdump(local_buffer)		#展示处来本地连接发送的一些数据
			#发送给我们的的本地请求
			local_buffer = request_handler(local_buffer)
			#向远程主机发送数据
			remote_socket.send(local_buffer)	#将本地发送来的数据转发给远程的主机
			print "[==>]发送到远程主机"
			remote_buff = receive_from(remote_socket)	#数据发送过去后，接受来自远程主机的回应
			if len(remote_buff):
				print "[<==]接受%d字节的数据来自远程主机"%len(remote_buff)
				hexdump(remote_buff)
				#发送到响应处理函数
				remote_buff = response_handler(remote_buff)
				#然后把响应发送给本地
				client_socket.send(remote_buff)
				print "[<==]发送给本地"
			if not len(local_buffer) or not len(remote_buff):
				client_socket.close()
				remote_socket.close()
				print "[*]没有数据，关闭连接"
				break
def hexdump(src,length=16):   #将接受到的数据，打印在屏幕上面
	result=[]
	digits = 4 if isinstance(src,unicode) else 2
	for i in xrange(0,len(src),length):		#每16个字节长度截输出一下
		s= src[i:i+length]
		hexa = b' '.join(["%0*X"%(digits,ord(x)) for x in s])
		text = b' '.join([x if 0x20 <= ord(x) <0x07F else b'.' for x in s])
		result.append(b"%04X %-*s  %s"%(i,length*(digits+1),hexa,text))
		print b'\n'.join(result
def receive_from(connection):
	buffer=""
	connection.settimeout(20)
	try:
		while True:
			data = connection.recv(4096)
			if not data:
				break
			buffer += data
	except:
	pass
	return buffer
def request_handler(buffer)
	return buffer
def response_handler(buffer)
	return buffer
#main函数开始，首先我们在一台电脑上运行这个程序
#然后给这个程序5个参数，一个是本地主机，一个本地端口，一个是远程主机，一个是远程端口，还一个是receive_first
def main():
	if len(sys.argv[1:])!=5:
		print "使用代理./proxy.py [localhost] [local_port] [remotehost] [remoteport] [receive_first]"
	#设置本地监听参数
	local_host = sys.argv[1]
	local_port = int(sys.argv[2])
	#设置目标监听
	remote_host = sys.argv[3]
	remote_port = int(sys.argv[4])
	#告诉代理，在发送给远程主机之前连接和接受数据
	receive_first = sys.argv[5]
	if "True" in receive_first:
		receive_first = True
	else:
		receive_first = False
	#调用我们的服务套接字
	server_loop(local_host,local_port,remote_host,remote_port,receive_first)	#把接受到的数据传送给server服务函数
main()