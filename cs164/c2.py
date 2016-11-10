import socket
import sys
import time

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

try: 
	s.bind((host,port))
except socket.error, msg:
	print('Bind failed. Error code: ' + str(msg[0]) + ' Message ' + msg[1])
	sys.exit()

print('Socket bind complete')

while(1) :
	try:
		# Receive input from server (data,addr)
		d = s.recvfrom(1024)
		pkt = d[0]
		addr = d[1]
		
		if(pkt == 'pkt0'):
			reply = 'ack0'
		else:
			reply = 'ack1'

		print( 'Received: ',pkt)
		print( 'Sending: ',reply)
		print('')
		
		# Repond to sender
		s.sendto(reply,addr)
	
		time.sleep(4)
	except socket.error, msg:
		print( 'Error code: ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()
