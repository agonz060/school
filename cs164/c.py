import socket
import sys
import time
import select

# create dgram udp socket
try :
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
except socket.error:
	print( 'Failed to create socket')
	sys.exit()

# Server address variables
host = 'localhost'
port = 8888
#port = raw_input("Enter port: ")

while(1) :
	msg = raw_input('Enter message to send: ')

	try:
		# Send string to server
		s.sendto(msg,(host,port))

		# Receive input from server (data,addr)
		d = s.recvfrom(1024)
		reply = d[0]
		addr = d[1]

		print( 'Server reply: ' + reply)
	
	except socket.error, msg:
		print( 'Error code: ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()
