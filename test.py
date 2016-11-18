test = "Error: wrong password.\n Enter password: "
test2 = "Error: Username not found.\n Enter username: "

error = "Error"
error2 = "Error: "

if error in test:
	print(test)
else:
	print('error not detected in test')

if error2 in test:
	print(test2)
else:
	print('error2 not detected in test2')
