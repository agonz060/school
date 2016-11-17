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

users = {'mando':'pass123', 'sam':'s1', 'andrew':'a1', 'tim':'t1'}
keys = ['mando', 'sam', 'andrew', 'tim']

msgQueue = {}
usrNmeMsg = "Username: "
pswd = "Pass: "
errorUsrName = "Error: Username not found. Enter username: "
errorPswd = "Error: wrong password. Enter password: "

# key = userName, value = userId
curUsers = {}

while inputs :
	
	# wait for a socket to be ready for processing
	readable,writable,exceptional = select.select(inputs, outputs, inputs)
	
	for s in readable:
		if s is server:
			connection, clientAddr = s.accept()
			print >> sys.stderr, 'new connection from', clientAddr
			
			connection.setblocking(0)
			inputs.append(connection)

			msgQueue[connection] = Queue.Queue()
			msgQueue[connection].put(usrNmeMsg)
		
			if connection not in outputs:
				outputs.append(connection)
		else:
			data = s.recv(1024)
			if data:
				print('recv: '+data)
				if errorUsrName in data:
					usrName = data.split(" ")[6]
					#print('Username: '+usrName)
					for user in keys:
						if user is usrName:
							curUsers[s] = user
							msgQueue[s].put(pswd)
						else:
							msgQueue[s].put(errorUsrName)
				elif usrNmeMsg in data:
					usrName = data.split(" ")[1]
					#print('In username')
					#print('Username: '+usrName)	
					for user in keys:
						print('usr: '+user)
						if (user == usrName):
							print('Success')
							curUsers[s] = user
						 	msgQueue[s].put(pswd)
						else:
							msgQueue[s].put(errorUsrName)
				elif errorPswd in data:
					passwrd = data.split(" ")[5]
					print('Pass: '+passwrd)
					if passwrd is users[curUsers[s]]:
						msgQueue[s].put(menu)
					else:
						msgQueue[s].put(errorPswd)
				elif pswd in data:
					passwrd = data.split(" ")[1]
					print('Pass: '+passwrd)
					if passwrd is users[curUsers[s]]:
						msgQueue[s].put(menu)
					else:
						msgQueue[s].put(errorPswd)
				if s not in outputs:
					outputs.append(s)
			else:
				if s in outputs:
					outputs.remove(s)
				inputs.remove(s)
				s.close()

				del msgQueue[s]
							
	for s in writable:
			try:
				nextMsg = msgQueue[s].get_nowait()
			except Queue.Empty:
				outputs.remove(s)
			else:
				s.send(nextMsg)

	for s in exceptional:
		inputs.remove(s)
		if s in outputs:
			outputs.remove(s)
		s.close()

		del msgQueue[s]
