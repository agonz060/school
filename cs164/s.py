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
errUserName = "Error: Username not found. Enter username: "
errPass = "Error: wrong password. Enter password: "

# key = userName, value = userId
userName = {'':''}
connectedClients = [ ] 

menu = "Welcome \n **************** \n Select option:\n1. Change password\n2.Log out"

while inputs :
	
	# wait for a socket to be ready for processing
	readable,writable,exceptional = select.select(inputs, outputs, inputs)
	
	for s in readable:
		if s is server:
			conn, cliAddr = s.accept()
			print >> sys.stderr, 'new connection from', cliAddr
			
			conn.setblocking(0)
			inputs.append(conn)
				
			clientPort = str(conn.getpeername()[1])
			msgQue[clientPort] = getUserName
			connectedClients.append(clientPort)

			if conn not in outputs:
				outputs.append(conn)
		else:
			data = s.recv(1024)
			if data:
				print('recv: '+data)
				
				error = "Error:"
				uName = 'username:'
				uName2 = 'Username:'
				passWord = 'password:'
				passWord2 = 'Password:'

				clientPort = str(conn.getpeername()[1])
				
				if error in data:
					print('error in data')
					if uName in data or uName2 in data:
						print('in errUserName')
						usrName = data.split(" ")[6]
						print('username: ',usrName)
						
						flag = 1
			
						for user in users:
							if user == usrName:
								print('client: ',clientPort,' username match: ',user)
								print('getPass: ',getPass)
								msgQue[clientPort] = getPass
								userName[clientPort] = user
								
								if s not in outputs:
									print('adding s to outputs')
									outputs.append(s)
								flag = 0
								break
						if flag:
							print('errorUserName') 
							msgQue[clientPort] = errUserName
							if s not in outputs:
								print('adding s to outputs')
								outputs.append(s)
					
					elif passWord in data or passWord2 in data:
						print('in errPass')
					
						password = data.split(" ")[5]
						print('Pass: '+password)
						print('client: ',clientPort)
						uPass = password[				
						if password == password[userName[clientPort]]:
							print('Password found, loading menu')
							msgQue[clientPort] = menu
							if s not in outputs:
								print('adding s to outputs')
								outputs.append(s)
							else:
								print('errPass')
								msgQue[clientPort] = errPass
								if s not in outputs:
									print('adding s to outputs')
									outputs.append(s)
				elif uName in data or uName2 in data:
					usrName = data.split(" ")[1]
					print('In username')
					print('Username: '+usrName)
					flag = 1	
					for user in users:
						if (user == usrName):
						 	print('client: ',clientPort,' username match: ',user)	
							msgQue[clientPort] = getPass
							userName[clientPort] = user
							if s not in outputs:
								print('adding s to outputs')
								outputs.append(s)
							flag = 0
							break
					if flag:	
						print('errorUserName')
						msgQue[clientPort] = errUserName
						if s not in outputs:
							print('adding s to outputs')
							outputs.append(s)
				
				elif passWord in data or passWord2 in data:
					print('inGetPass')
					passwrd = data.split(" ")[1]
					#print('Pass: '+passwrd)
					#print('client: ',clientPort)
					
					uName = userName[clientPort]
					#print('uName: ',uName)
					
					flag = 1	
					for userName in password:
						if(userName == uName):
							if(passwrd == password[uName]):
								print('Success! uName: ',uName,' pass: ',passwrd)	
								msgQue[clientPort] = menu
								
								if s not in outputs:
									print('adding s to outputs')
									outputs.append(s)
								flag = 0
								break
					if flag:	
						print('errPass')
						msgQue[clientPort] = errPass
						
						if s not in outputs:
							print('adding s to outputs')
							outputs.append(s)
				
			else:
				print('closing s')
				if s in outputs:
					outputs.remove(clientPort)
				if s in inputs:
					inputs.remove(clientPort)
				s.close()

				msgQue[clientPort] = ""
		print('at end of readable')
						
	for s in writable:
		print('in writable')	
		clientPort = str(s.getpeername()[1])
		print('client: ', clientPort)
		actualClient = ""

		for client in connectedClients:
			nextMsg = msgQue[client]
			actualClient = client
			
			if nextMsg:
				msgQue[client] = ""
			break
		
		if(nextMsg):
			print('sending nextMsg: ',nextMsg,' to client: ',actualClient)
			s.send(nextMsg)
		else:
			print('no output, removing s from outputs')
			outputs.remove(s)
		print('at end of writable')
	
	for s in exceptional:
		print('in Exceptional, closing s')	
		if s in inputs:
			inputs.remove(s)
		if s in outputs:
			outputs.remove(s)
		s.close()
