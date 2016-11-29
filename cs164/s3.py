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
numUsers = len(users)

msgQue = {'':''}
privateMsgs = {'':[ ]}

getUserName = "Username: "
getPass = "Password: "
errUserName = "Error: Username not found. Enter username: "
errPass = "Error: wrong password. Enter password: "

# key = portNumber value = userName
userName = {'':''}

menu = "\tMenu\n*******************\nSelect option:"
sendMsgOption = "\n1. Send message"
checkInboxOption = "\n2. Check inbox"
requestOption = "\n3. Send request"
pswdOption = "\n4. Change password"
logOutOption = "\n5.Log out"
options = [sendMsgOption,checkInboxOption,requestOption, pswdOption,logOutOption]
numOptions = len(options)

for x in range(0,numOptions):
	menu += options[x]	

changePswdMsg = "\nChanging password\n********************\nEnter current password: "
newPswdMsg = "Enter new password: "

composeMsg = "\nCompose message\n***************\nSend message to:"
getMsg = "\nEnter message: "

menuMsg = "Menu"
newMsg = "new"
currentPswd = "current"
newPassSaved = "New password saved!\n\n"
loggingOutMsg = "logging out"
savedMsg = "saved"

uComposeMsg = {'':''}
online = {'':''}
messages = [ ]
testMsg = 'From: mando\nTo: andrew\n************\nSuccess is near\n************\n'
messages.append(testMsg)
newMsgRecved = "New message received"
replyingToRequest = "requests to display"
# Key = uName , value = [requests]
requests = {'':[ ]}
friends = {'':[ ]}

#print("option.len: ", len(options))
def _compose1(data,clientPort): 
	inputSplit = data.split(":")
	uNameIndex = len(inputSplit) - 1
	uName = (inputSplit[uNameIndex]).lower()
	#print('sending message to ', uName)
	sendingTo = "To: "
	found = 0
	for x in range(0,numUsers):
		#print("users[",x,"]: ",users[x])
		name = (users[x]).lower()
		if uName == name:
			#print('Compose: user found')
			found = 1
			sendingTo += name
			uComposeMsg[clientPort] = sendingTo
			msgQue[clientPort] = getMsg
			break
		#else:
		#	print('uName: ',uName,' != ',name)
	if found == 0:
		print('Compose: user not found')
		errUserNotFound = "\nUser: " + uName + " not found\n\n"
		msgQue[clientPort] = errUserNotFound + menu

	return

def _compose2(data,clientPort):
	print('in _compose2')
	#print('data: ',data)
	inputSplit = data.split(':')
	#print('inputSplit: ',inputSplit)
	msgIndex = len(inputSplit) - 1
	msg = inputSplit[msgIndex]

	to = uComposeMsg[clientPort]
	uComposeMsg[clientPort] = ""

	fromUser = "From: " + userName[clientPort] + "\n"
	divider = '\n-------------'

	completeMsg = fromUser + to + divider + '\n' + msg + divider
	print('completeMsg: ',completeMsg)
	#print('to: ',to)
	sendToUserSplit = to.split(" ")
	#print('sendToUserSplit: ',sendToUserSplit)
	sendToIndex = len(sendToUserSplit) - 1
	sendToUser = sendToUserSplit[sendToIndex]
	print('sendToUser: ',sendToUser)
	
	userPort = _userOnline(sendToUser)
	if userPort >= 0:
		_sendAlert(userPort)
	else:
		print('_sendAlert: user ',sendToUser,' not online, storing message for later viewing')
	print('messages before: ',messages)
	messages.append(completeMsg)
	print('messages after: ',messages)

	msgQue[clientPort] = "Message sent!\n\n" + menu
	return

# Returns the port number associated with user name: 'uName'
def _userOnline(uName):
	#print('in _userOnline')
	portNum = _getPortNum(uName)
	#print('User: ',uName,' port: ',portNum)
	
	if portNum >= 0:
		print('online.keys: ',online.keys())
		for onlineUserPort in online.keys():
			if onlineUserPort == portNum:
				return portNum
		print('_userOnline: could not find a user online with the specified port, returning -1')
		return -1
	else:
		print('_userOnline: port number for user: ',uName,' not found, returning -1')
		return -1

def _getPortNum(uName):
	print('in _getPortNum for user: ',uName)
	for portNum in userName.keys():
		print('userName[',portNum,']: ',userName[portNum])
		if userName[portNum] == uName:
			return portNum
	return -1

# Notifies a user of a new message received
def _sendAlert(userPort):
	print('Sending alert to ',userName[userPort])
	sock = online[userPort]

	msgQue[userPort] = newMsgRecved

	if sock not in outputs:
		outputs.append(sock)

	return

# Check the inbox of a user by scanning through messages list
def _checkInbox(clientPort):
	uName = userName[clientPort]
	print('Checking the inbox of user: ',uName)
	inbox = [ ]

	toUser = 'To: ' + uName
	#print('messages: ',messages)
	for x in range(0,len(messages)):
		msg = messages[x]
		#print('msg: ',messages[x])
		if toUser in msg:
			#print('msg found for user')
			inbox.append(msg)
			
	privateMsgs[uName] = inbox
	return 
	

def _displayMsgs(uName,clientPort):
	print('in _displayMsgs')
	_checkInbox(clientPort)
	#print('userName: ',uName)
	selectMsg = _getInboxMenu(uName)
	#print(selectMsg)
	msgQue[clientPort] = selectMsg

def _getInboxMsgCount(uName):
	#print('_getInboxMsgCount: uName: ',uName)
	return len(privateMsgs[uName])

def _getInboxMenu(uName):
	msgCount = _getInboxMsgCount(uName)
	#print('User: ',uName,' msgs: ',msgCount)

	inbox = privateMsgs[uName]
	selectMsg = "\n\nInbox: "+str(msgCount)+" messages\n****************\n"
	selectMsg += "Select message to read:\n"
	
	for x in range(0,msgCount):
		msg = inbox[x]
		fromUser = 'From: ' + _getSenderName(msg)
		selection = str(x) + '. ' + fromUser + '\n'
		selectMsg += selection

	return selectMsg

def _getSenderName(msg):
	toLineIndex = 0
	userNameIndex = 1
	#print('_getSenderNameMsg: ',msg)
	toLine = msg.split('\n')[toLineIndex]
	#print('toLine: ',toLine)
	uName = toLine.split(' ')[userNameIndex]
	#print('uName: ', uName)
	return uName

def _readMsg(data,clientPort):
	uName = userName[clientPort]

	userInputSplit = data.split('\n')
	openMsgIndex = len(userInputSplit) - 1
	openMsg = userInputSplit[openMsgIndex]

	if openMsg == 'b':
		print('_readMsg: 'b' detected, returning to menu')
		formatting = '\n\n'
		msgQue[clientPort] = formatting + menu
	else: 
		openMsg = int(openMsg)
		print('openMsg: ',openMsg)

	inboxCount = _getInboxMsgCount(uName)
	print('inboxCount: ',inboxCount)
	if openMsg >= 0 and openMsg < inboxCount:
		inbox = privateMsgs[uName]
		formatting = '\n\nOpening message ' + str(openMsg) + '\n*****************\n'

		inboxMenu = _getInboxMenu(uName)
		msgQue[clientPort] = formatting + inbox[openMsg] + inboxMenu
	else:
		errSelection = "Could not open message: " + openMsg + '\n\n'
		msgQue[clientPort] = errSelection + menu

	return

def _displayRequests(uName,clientPort):
	print('in display requests')
	reqsMsg = _getRequests(uName)

	msgQue[clientPort] = reqsMsg
	return

def _getRequests(uName):
	numRequests = _getNumReqs(uName)
	print('numReqs: ', numRequests)

	reqsMsg = "\n\n" + numRequests + " requests to display" + "\n**********************"
	requestsList = requests[uName]
	print('requests: ',requests)

	for x in range(0, len(requestsList[uName])):
		requestFrom = '\n' + str(x) + '. From: ' + requestsList[x]
		reqsMsg += requestFrom

	return reqsMsg

def _getNumReqs(uName):
	return len(requests[uName])

def _replyToRequest(data,clientPort):
	print('in _replyToRequest')
	replySplit = data.split('\n')
	replyIndex = len(replySplit) - 1
	reply = replySplit[replyIndex]
	print('reply: ',reply)

	if 'b' in reply:
		msgQue[clientPort] = menu
	elif 'a' in reply or 'r' in reply:
		replyId = _getReplyId(reply,clientPort)
		if replyId == -1:
			reqsMsg = _getRequests(userName[clientPort])
			invalidInMsg = "* Invalid input"
			msgQue[clientPort] = reqsMsg
			return
		else:
			if 'a' in reply:
				_acceptRequest(clientPort,replyId)
				return
			elif 'r' in reply:
				//To do
				print('Continue with rejection actions')
				return

def _acceptRequest(clientPort,replyId):
	print('in _acceptRequest')
	print('replyId: ',replyId)
	uName = userName[clientPort]

	reqs = requests[uName]
	print('requests for user ',uName,': ',reqs)

	friendName = reqs[replyId]
	print('friendName: ',friendName)

	friendsList = friends[uName]
	friendsList.append(friendName)

	friends[uName] = friendsList

	_updateRequests(uName,friendName)
	acceptedMsg = '\nAccepted ' + friendName + "'s friend request"
	completeMsg = acceptedMsg + _getRequests(uName)
	print('completeMsg: ',completeMsg)
	msgQue[clientPort] = completeMsg
	return 

def _updateRequests(uName,friendName):
	print('updating requests for user: ',uName)
	reqs = requests[uName]
	print('requests before: ', reqs)

	updated = [ ]
	for x in range(0,len(reqs)):
		if friendName is not reqs[x]:
			print('user: ',reqs[x],' being added to updated')
			updated.append(reqs[x])
		else:
			print('friendName: ',friendName,' reqs[x]: ',reqs[x])

	requests[uName] = updated
	print('requests after: ', updated)
	return 

def _getReplyId(reply,clientPort):
	print('in _getReplyId')
	print('reply: ',reply)

	numReqs = _getNumReqs(userName[clientPort])

	replySplit = reply.split(' ')
	replyIdIndex = len(replySplit) - 1
	replyId = int(replySplit[replyIdIndex])
	print('replyId: ',replyId)
	
	if replyId >= 0 and replyId < numReqs:
		return replyId
	else:
		return -1

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

			if conn not in outputs:
				outputs.append(conn)
		else:
			data = s.recv(1024)
			if data:
				print('Data: ',data)
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
						inputSplit = data.split(" ")
						uNameIndex = len(inputSplit) - 1
						usrName = inputSplit[uNameIndex]
						#print('username: ',usrName)
						
						flag = 1
			
						for user in users:
							if user == usrName:
								msgQue[clientPort] = getPass
								userName[clientPort] = user
								
								if s not in outputs:
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

						inputSplit = data.split(" ")
						passIndex = len(inputSplit) - 1
						clientPass = inputSplit[passIndex]

						print('client: ', clientPort,'Pass: '+ clientPass)
						uName = userName[clientPort]
						uPass = password[uName]

						if clientPass == uPass:
							online[clientPort] = s
							_checkInbox(clientPort)
							inboxCount = _getInboxMsgCount(uName)
							greetingMsg = "Welcome " + uName + " you have " + str(inboxCount) + " new messages\n\n"
							msgQue[clientPort] = greetingMsg + menu
							if s not in outputs:
								print('adding s to outputs: menu')
								outputs.append(s)
						else:
							print('errPass')
							msgQue[clientPort] = errPass
							if s not in outputs:
								print('errPass: adding s to outputs')
								outputs.append(s)
					elif "Compose" in data:
						_compose(data,clientPort)
						if s not in outputs:
							outputs.append(s)
				elif uName in data or uName2 in data:
					print('In username')
					inputSplit = data.split(" ")
					uNameIndex = len(inputSplit) - 1
					usrName = inputSplit[uNameIndex]
					
					flag = 1	
					for user in users:
						if (user == usrName):	
							msgQue[clientPort] = getPass
							userName[clientPort] = user
							if s not in outputs:
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
					#print('Checking current password before making change')
					dataSplit = data.split('\n')
					pswdIndex = len(dataSplit) - 1
					currentPass = dataSplit[pswdIndex]
					#print('currPass: ',currentPass)

					uName = userName[clientPort]
					uPass = password[uName]

					if currentPass == uPass:
						#print('password match, requesting new password')
						msgQue[clientPort] = newPswdMsg
						if s not in outputs:
							outputs.append(s)
					else:
						#print('error: wrong password. returning to menu')
						msgQue[clientPort] = menu
						if s not in outputs:
							outputs.append(s)
				elif newMsg in data and "password" in data and not menuMsg in data:
					#print('Setting client ',clientPort,' new password')
					#print('newPassdata.len: ',len(data.split('\n')))
					inputSplit = data.split('\n')
					pswdIndex = len(inputSplit) - 1
					newPass = inputSplit[pswdIndex]
					#print('newPass: ', newPass)

					uName = userName[clientPort]
					oldPass = password[uName]
					#print('oldPass: ', oldPass)

					password[uName] = newPass

					msgQue[clientPort] = newPassSaved + menu
					if s not in outputs:
						outputs.append(s)

				elif passWord in data or passWord2 in data:
					print('inGetPass')
					#print('getPassData.len: ',len(data.split(" ")))
					inputSplit = data.split(" ")
					pswdIndex = len(data.split(" ")) - 1
					passwrd = inputSplit[pswdIndex]
					print('client: ',clientPort,' pass: ', passwrd)
					
					uName = userName[clientPort]
					#print('uName: ',uName)
						
					if(passwrd == password[uName]):
						#print('Success! uName: ',uName,' pass: ',passwrd)
						online[clientPort] = s

						_checkInbox(clientPort)
						inboxCount = _getInboxMsgCount(uName)

						greetingMsg = "Welcome " + uName + " you have " + str(inboxCount) + " new messages\n\n"
						msgQue[clientPort] = greetingMsg + menu	

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
					inputSplit = data.split('\n')
					inputIndex = len(inputSplit) - 1
					userInput = inputSplit[inputIndex]
					#print('menuInput: ', userInput)

					userOption  = ""

					for x in range(0,numOptions):
						if userInput in options[x]:
							userOption = options[x]
							#print('userOption: ', userOption)

					if "message" in userOption:
						print('in send message option')
						msgQue[clientPort] = composeMsg
					elif "password" in userOption:
						print('in change password option')
						msgQue[clientPort] = changePswdMsg
					elif "inbox" in userOption:
						print('in inbox option')
						_displayMsgs(userName[clientPort],clientPort)
					elif "request" in userOption:
						_displayRequests(userName[clientPort],clientPort)
					elif "out" in userOption:
						print('in log out option')
						msgQue[clientPort] = loggingOutMsg

					if s not in outputs:
						outputs.append(s)

				elif "Compose" in data:
					_compose1(data,clientPort)

					if s not in outputs:
						outputs.append(s)
			
				elif "Enter message" in data:
					print('getting msg')
					_compose2(data,clientPort)

					if s not in outputs:
						outputs.append(s)
				elif "Select message" in data:
					print('selecting message to read')
					_readMsg(data,clientPort)

					if s not in outputs:
						outputs.append(s)
				elif replyingToRequest in data:
					print('replying to request')
					_replyToRequest(data,clientPort)

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
