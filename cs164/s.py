import socket 
import select
import sys
import time

HOST = 'localhost'
PORT = 8888

#Create UDP socket for client communication
try :
	sender = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	print( 'Socket Created')
except socket.error, msg :
	print( 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
	sys.exit()

# reading sockets
inputs = [ sender ]

# output sockets
outputs = [ ]

# Outgoing messages
msgBuffer = []
timeout = 2
addr = (HOST,PORT)
lastAck = ""
window = 4
pktsRecv = 0
startWindow = 0
while inputs :
	
	# wait for a socket to be ready for processing
	readable,writable,exceptional = select.select(inputs, outputs, inputs, timeout)
	
	if not (readable or writable or exceptional):
		if not lastAck:
			for x in range window:
				msg = "pkt"+str(x)
				msgBuffer.append(msg)
		else:
			for x  in range window:
				msg = "pkt"+str(x+
		if sender not in outputs:
			outputs.append(sender)
		
		#if(prevAck == "ack0"):
		#	resend = "pkt1"
		#else: 
		#	resend = "pkt0"

		#print('Timeout: resending ',resend)

		#msgBuffer.append(resend)
	
		#if sender not in outputs:
		#	outputs.append(sender)
		continue

	for s in readable:
		d = s.recvfrom(1024)
		ack = d[0]
		addr = d[1]
		
		if ack:
			print('Received ', ack)

			if(ack == "ack0"):
				reply = "pkt1"
			else:
				reply = "pkt0"
			prevAck = ack
				
			# receive 
			msgBuffer.append(reply)				

			# add socket to output
			if s not in outputs:
				outputs.append(s)
	for s in writable:
		if not msgBuffer:	
			outputs.remove(s)
		else:
			msg = msgBuffer[0]
			msgBuffer = []	
			
			print('Sending ',msg,' to ',addr)
			s.sendto(msg,addr)		
