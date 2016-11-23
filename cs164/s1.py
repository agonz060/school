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

password = {'mando':'m1', 'sam':'s1', 'andrew':'a1', 'tim':'t1'}
users = ['mando', 'sam', 'andrew', 'tim']

msgQue = {'':''}

getUserName = "Username: "
getPass = "Password: "
errUserName = "Error: Username not found. Enter username: "
errPass = "Error: wrong password. Enter password: "

# key = userName, value = userId
userName = {'':''}
connectedClients = [ ] 

menuMsg = "Welcome"
menu = "\tWelcome\n*******************\nSelect option:\n1. Change password\n2.Log out"
changePswdMsg = "Changing password\n********************\nEnter current password: "
newPswdMsg = "Enter new password: "

newMsg = "new"
currentPswd = "current"
newPassSaved = "New password saved!\n"
loggingOutMsg = "logging out"
savedMsg = "saved"
optionIndex = 5

while inputs :
	
	# wait for a socket to be ready for processing
	readable,writable,exceptional = select.select(inputs, outputs, inputs)
	
	for s in readable:
		if s is server:
			conn, cliAddr = s.accept()
			print >> sys.stderr, 'new connection from', cliAddr
			
			conn.setblocking(0)
			inputs.append(conn)
			#print('s.SockName: ',s.getsockname())
			#print('conn.sockname: ',conn.getsockname())
			#print('conn.getpeer: ', conn.getpeername())
			clientPort = str(conn.getpeername()[1])
			msgQue[clientPort] = getUserName
			connectedClients.append(clientPort)

			if conn not in outputs:
				outputs.append(conn)
		else:
			#print('s.SockName: ',s.getsockname())
			#print('s.getpeer: ',s.getpeername())
			data = s.recv(1024)
			if data:
				print('recv: '+data)
				
				error = "Error:"
				uName = 'username:'
				uName2 = 'Username:'
				passWord = 'password:'
				passWord2 = 'Password:'

				clientPort = str(s.getpeername()[1])
				
				if error in data:
					print('error in data')
					if uName in data or uName2 in data:
						print('in errUserName')
						usrName = data.split(" ")[6]
						#print('username: ',usrName)
						
						flag = 1
			
						for user in users:
							if user == usrName:
								#print('client: ',clientPort,' username match: ',user)
								#print('getPass: ',getPass)
								msgQue[clientPort] = getPass
								userName[clientPort] = user
								
								if s not in outputs:
									#print('adding s to outputs')
									outputs.append(s)
								flag = 0
								break
						if flag:
							print('errorUserName') 
							msgQue[clientPort] = errUserName
							if s not in outputs:
								print('errorUName: adding s to outputs')
								outputs.append(s)
					
					elif passWord in data or passWord2 in data:
						print('in errPass')
					
						clientPass = data.split(" ")[5]
						print('client: ', clientPort,'Pass: '+ clientPass)
						uName = userName[clientPort]
						uPass = password[uName]
						
						#if password == uPass:
						#	print('passwords match!!!')

						if clientPass == uPass:
							#print('Password found, loading menu')
							msgQue[clientPort] = menu
							if s not in outputs:
								print('adding s to outputs: menu')
								outputs.append(s)
						else:
							print('errPass')
							msgQue[clientPort] = errPass
							if s not in outputs:
								print('errPass: adding s to outputs')
								outputs.append(s)

				elif uName in data or uName2 in data:
					usrName = data.split(" ")[1]
					print('In username')
					#print('Username: '+usrName)
					flag = 1	
					for user in users:
						if (user == usrName):
						 	#print('client: ',clientPort,' username match: ',user)	
							msgQue[clientPort] = getPass
							userName[clientPort] = user
							if s not in outputs:
								#print('adding s to outputs')
								outputs.append(s)
							flag = 0
							break
					if flag:	
						print('errorUserName')
						msgQue[clientPort] = errUserName
						if s not in outputs:
							print('errorUName: adding s to outputs')
							outputs.append(s)
				elif currentPswd in data:
					print('Checking current password before making change')
					currentPass = data.split('\n')[3]
					print('currPass: ',currentPass)

					uName = userName[clientPort]
					uPass = password[uName]

					if currentPass == uPass:
						print('password match, requesting new password')
						msgQue[clientPort] = newPswdMsg
						if s not in outputs:
							outputs.append(s)
					else:
						print('error: wrong password. returning to menu')
						msgQue[clientPort] = menu
						if s not in outputs:
							outputs.append(s)
				elif newMsg in data:
					print('Setting client ',clientPort,' new password')
					newPass = data.split('\n')[1]
					print('newPass: ', newPass)

					uName = userName[clientPort]
					oldPass = password[uName]
					print('oldPass: ', oldPass)

					password[uName] = newPass

					msgQue[clientPort] = newPassSaved + menu
					if s not in outputs:
						outputs.append(s)

				elif passWord in data or passWord2 in data:
					print('inGetPass')
					passwrd = data.split(" ")[1]
					print('client: ',clientPort,' pass: ', passwrd)
					
					uName = userName[clientPort]
					#print('uName: ',uName)
						
					if(passwrd == password[uName]):
						#print('Success! uName: ',uName,' pass: ',passwrd)	
						msgQue[clientPort] = menu	
						if s not in outputs:
							print('adding s to outputs: menu')
							outputs.append(s)
					else:	
						print('errPass')
						msgQue[clientPort] = errPass
						if s not in outputs:
							print('errPass: adding s to outputs')
							outputs.append(s)
						
				elif menuMsg in data:
					print('in menu')
					if savedMsg in data:
						userInput = data.split('\n')[optionIndex+1]
					else:
						userInput = data.split('\n')[optionIndex]
					#print('userInput: ', userInput)
					if userInput == '1':
						print('changing client ',clientPort,' password')
						msgQue[clientPort] = changePswdMsg
						if s not in outputs:
							outputs.append(s)
					elif userInput == '2':
						print('Client ',clientPort,' logging out')
						msgQue[clientPort] = loggingOutMsg
						
						if s not in outputs:
							outputs.append(s)

			else:
				#print('closing s')
				if s in outputs:
					outputs.remove(s)
				if s in inputs:
					inputs.remove(s)
				s.close()

				msgQue[clientPort] = ""
		print('at end of readable')
						
	for s in writable:
		print('in writable')
		#print('s.getpeer: ',s.getpeername())	
		clientPort = str(s.getpeername()[1])
		#print('client: ', clientPort)
		#actualClient = ""

		#for client in connectedClients:
		nextMsg = msgQue[clientPort]
		#	actualClient = client
		
		if(nextMsg):
			msgQue[clientPort] = ""
			if loggingOutMsg in nextMsg:
				print('Client',clientPort,' logging out')
				s.send(nextMsg)
				if s in inputs:
					inputs.remove(s)
				outputs.remove(s)
			else:
				print('sending nextMsg: ',nextMsg,' to client: ',clientPort)
				s.send(nextMsg)
		else:
			#print('no output, removing s from outputs')
			outputs.remove(s)
		print('at end of writable')
	
	for s in exceptional:
		#print('in Exceptional, closing s')	
		if s in inputs:
			inputs.remove(s)
		if s in outputs:
			outputs.remove(s)
		s.close()
