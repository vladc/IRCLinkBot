import socket, urllib2, sys, json, os, thread, re, random, time
from util import *
def importConfig():
	configFile = open ('./linkbot.conf','rw')#	Import settings file
	config = json.loads( configFile.read() )#	Parse config file
	configFile.close()
	return config

config = importConfig()
# Creating socket   
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
def connect(s):
	print "[-]Connecting to server..."
	while 1:
		try:
		        s.connect(( config['settings']['host'] , int(config['settings']['port']))) #connect to server
			break
		except:
		        print "[E]Could not connect to server."
	time.sleep(0.2)
	s.send('nick ' + config['settings']['botNick'] + '\r\n')
	time.sleep(0.2)
	s.send('user ' + config['settings']['botIdent'] + ' * ' + config['settings']['botUser'] + ' ' + config['settings']['botName'] + '\r\n')
	if config['settings']['authenticate'] == 'True':
	    try:
	        passFile = open('pass','r')
	        password = passFile.read()
	        s.send('PRIVMSG nickserv :identify ' + password + '\r\n')
	    except:
	        print "[E] Password not found. Continuing without authentication."
	while 1:
		recvData = s.recv(512)
		if config['settings']['printRecv'] == 'True':
			print recvData
		if ":You are now identified for" in recvData or config['settings']['authenticate'] != 'True':
			break
	for channel in config['settings']['joinChannels']:#	Join all the channels
	        s.send('join ' + channel + '\r\n')
		time.sleep(0.5)
	        s.send('privmsg ' + channel + ' :' + config['settings']['joinMessage'] + "\n\r")
connect(s)
sending = 0
def runPlugins(plugins, path, data):#	This function is for threading
	global sending
	for plugin in plugins:
		if plugin[-3:] == '.py' and plugin[0:2] != 'lib':
			pluginFile = open (path + '/' + plugin,'r')
			exec(pluginFile)
			pluginFile.close()
			args = argv(':', data['recv'])
			toSend = main(data)
			if args['channel'] in config['settings']['pluginIgnoreChannels']:
				if plugin in config['settings']['pluginIgnoreChannels'][args['channel']]:
					toSend = None
			if toSend and toSend != '' and toSend != None:
				global sending
				while 1:
					if sending <= 2:
						sending += 1
						for send in toSend.split('\n'):
							s.send(send + '\n')
							time.sleep(float(config['settings']['messageTimeSpacing']))
						sending -= 1
						break
					else:
						continue
				if config['settings']['printSend'] == 'True':
					print toSend
			"""
			except Exception , err:
				sending -= 1
				errormsg = sys.exc_info()[1]
				if errormsg != None:
					print plugin + ' : ' + str(errormsg)
			"""

loop = 0
while 1:
	try:
		config = importConfig()#		Refresh the config file
	except:
		print "[E] Failed to read config"
	recvLen = int(config['settings']['recvLen'])
	recvData = s.recv(recvLen)
	if recvData == "":
		s.close()
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		connect(s)
	data = {'recv' : recvData,#		Format data to send to the plugins.	
			'config' : config,
			'loop' : loop } 
	#Run plugins from ./plugins/
	path = './plugins/'
	rootPlugins = os.listdir('./plugins/')# 	Get plugin filenames only from the plugins directory
						#	This runs the plugins no matter what.
	thread.start_new_thread( runPlugins, (rootPlugins, path, data) )#	Run the root plugins in a new thread

	'''Check if the recv is a privmsg from a channel (Not foolproof, you can involk this by privmsging
	the bot with ":a!b@c PRIVMSG #d:e" for example.'''
	if not re.match('^:*!*@*.*PRIVMSG.#*.:*', recvData) == None and re.match('^:*!*@*.*PRIVMSG.' + config['settings']['botNick'] + '.:*',recvData) == None:
		#Run plugins from ./plugins/privmsg/*
		for root, subFolders, files in os.walk('./plugins/privmsg/',followlinks=True):#		Fetch plugins recurisively. This means
			thread.start_new_thread( runPlugins, (files, root, data) )#	you can organize plugins in subfolders
										#	however you'd like. eg. Have a folder
										#	full of entertainment plugins that you
										#	can easily disable by prepending '.'
										#	to the folder name.
	# If recv is a private message to the bot
	elif not re.match('^:*!*@*.*PRIVMSG.' + config['settings']['botNick'] + '.:*',recvData) == None:
		# Run plugins from ./plugins/privmsgbot/*
		for root, subFolders, files in os.walk('./plugins/privmsgbot/',followlinks=True):
			thread.start_new_thread( runPlugins, (files, root, data) )
	else:
		for line in recvData.splitlines():
			if line[0:5] == 'PING ':
				s.send('PONG ' + recvData.split(' ')[1][1:] + '\r\n')
				if config['settings']['printSend'] == 'True':
					print 'PONG ' + recvData.split(' ')[1][1:] + '\r\n'
		'''	I was thinking about making the bot run plugins from a 'PING' folder,
			but saw very little point, other than possible data logging?. Regardless,
			I left it out.	'''
		#run plugins from the directory named 'root'

	for root, subFolders, files in os.walk('./plugins/root/',followlinks=True):
		thread.start_new_thread( runPlugins, (files, root, data) )
		
	if config['settings']['printRecv'] == 'True':
		print recvData
	loop += 1

