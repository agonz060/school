#! /usr/bin/env python2

import socket 
import select
import sys
import time
import Queue

HOST = ''
PORT = 8888

#Create UDP socket for client communication
try :
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#sender = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	print( 'Socket Created')
except socket.error, msg :
	print( 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
	sys.exit()
server.setblocking(0)

server_address = (HOST,PORT)
print >> sys.stderr, 'Starting up on %s port %s' % server_address

server.bind(server_address)

server.listen(5)

# reading sockets
inputs = [ server ]

# output sockets
outputs = [ ]

password = {'mando':'pass123', 'sam':'s1', 'andrew':'a1', 'tim':'t1'}
users = ['mando', 'sam', 'andrew', 'tim']

msgQue = {'':''}
getUserName = "Username: "
getPass = "Password: "

errUserName = "Error: Username not found.\n Enter username: "
errPass = "Error: wrong password.\n Enter password: "

# key = userName, value = userId
userName = {'':''}
clientId = 0

while inputs :
	
	# wait for a socket to be ready for processing
	readable,writable,exceptional = select.select(inputs, outputs, inputs)
	
	for s in readable:
		if s is server:
			conn, cliAddr = s.accept()
			print >> sys.stderr, 'new connection from', cliAddr
			
			conn.setblocking(0)
			tmpUserName = clientId

			inputs.append(conn)
			
			clientPort = str(conn.getpeername()[1])
			msgQue[clientPort] = getUserName
		
			if conn not in outputs:
				outputs.append(conn)
		else:
			data = s.recv(1024)
			if data:
				print('recv: '+data)
				errUserName = 'Error: username not found.'
				errPass = 'Error: wrong password.'
			
				clientPort = conn.getsockname()
				clientPort = clientPort[1]
				
				if errUserName in data:
					print('in errUsername')
					usrName = data.split(" ")[6]
					print('Username: '+usrName)
					for user in users:
						if user is usrName:
							print('getPass: ',getPass)
							print('client: ',clientPort)
							msgQue[clientPort] = getPass
							userName[clientPort] = user
						else:
							msgQue[clientPort] = errUserName
				elif getUserName in data:
					print('in getUsername')

					usrName = data.split(" ")[1]

					print('In username')
					print('Username: '+usrName)

					for user in users:
						print('usr: '+user)
						if (user == usrName):
							print('Success')
						 	msgQue[clientPort] = getPass
							userName[clientPort] = user
						else:
							msgQue[clientPort] = errUserName
				elif errPass in data:
					print('errPass')
					password = data.split(" ")[5]
					print('Pass: '+password)
					if password is password[userName[clientPort]]:
						msgQue[clientPort] = menu
					else:
						msgQue[clientPort] = errPass
				elif getPass in data:
					print('getPass')
					passwrd = data.split(" ")[1]
					print('Pass: '+passwrd)
					if passwrd is password[userName[clientPort]]:
						msgQue[clientPort] = menu
					else:
						msgQue[clientPort] = errPass
				
				if s not in outputs:
					print('adding client to output')
					outputs.append(s)
			else:
				if s in outputs:
					outputs.remove(clientPort)
				inputs.remove(clientPort)
				s.close()

				msgQue[clientPort] = ""
							
	for s in writable:
		print('in writable')		
		print('client: ',clientPort)
		clientPort = str(s.getpeername()[1])
		
		
		nextMsg = msgQue[clientPort]
		msgQue[clientPort] = ""
		print('nextMsg: ',nextMsg)

		if(nextMsg):
			s.send(nextMsg)
		else:
			print('removing client',clientPort,' from writable')
			outputs.remove(s)

	for s in exceptional:
		print('in exceptional')

		clientPort = s.getpeername()
		clientPort = clientPort[1]
		
		if s in inputs:
			inputs.remove(s)
		if s in outputs:
			outputs.remove(s)
		
		s.close()

		msgQue[clientPort] = ""
