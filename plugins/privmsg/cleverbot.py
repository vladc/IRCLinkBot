def main(data):
	if data['config']['settings']['botNick'] in data['recv'] or data['config']['settings']['botNick'].lower() in data['recv']:
		from libchatterbot import ChatterBotFactory, ChatterBotType
		if not 'bot' in globals():
			factory = ChatterBotFactory()
			botfac = factory.create(ChatterBotType.CLEVERBOT)#JABBERWACKY
			bot = botfac.create_session()
		else:
			global bot
		args = argv('@', data['recv'])
		junk = ':' + textbetween(':',' :', data['recv']) + ' :'
		query = data['recv'].replace(junk, '')
		query = query.replace('\n','')
		query = query.replace('\r','')
		query = query.replace(data['config']['settings']['botNick'] + ':','')
		query = query.replace(data['config']['settings']['botNick'],'Jorn')
		answer = bot.think(query)
		answer = answer.replace('PandoraBot',data['config']['settings']['botNick'])
		answer = answer.replace('God','Taiiwo')
		answer = answer.replace('&ouml;', 'o')
		debug = 'Query: ' + query + ' -- Answer: "' + answer + '"'
		print debug
		
		return say(args['channel'],args['nick'] + ': ' + answer)
		
