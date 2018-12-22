#version 1.1.1
import discord
import os
import sys
import time
import asyncio
import random
import youtube_dl
import queue
import subprocess
import datetime
import threading
import pickle
import urllib.request
from forecastiopy import *
import re

client = discord.Client()
calendar = []
users = []
started = False
shitpostingstreet = "405834555392655361"
coin = ["Heads","Tails"]
dank = 0

#these 5 variables are all used with voice functionality
voice = None
player = None
_in_voice = False
_skip_flag = False
q = queue.Queue(maxsize=0)

#coords for SIUE and api key for forecastio/darksky
api_key = "afdcb714b448f3f390bf6da777457d43"
lat = 38.792
lon = -89.999

board = []
teamA = [] #list of user id's in team A
teamB = [] #list of user id's in team B
wordStates = [0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2] #list of states for the corresponding word in board.  0=red, 1=blue, 2=gray, 3=black

def shuffle(array):
	for number in range(0, len(array)):
		first = random.randint(1,36)
		second = random.randint(1,36)
		temp = array[first]
		array[first] = array[second]
		array[second] = temp
	return array

#will return 12 hour forecast.  currently inaccurate and therefore in progress
async def weather():
	fio = ForecastIO.ForecastIO(api_key,
                            units=ForecastIO.ForecastIO.UNITS_SI,
                            lang=ForecastIO.ForecastIO.LANG_ENGLISH,
                            latitude=lat, longitude=lon)


	if fio.has_hourly() is True:
		hourly = FIOHourly.FIOHourly(fio)
		print('Hourly')
		print('Summary:', hourly.summary)
		print('Icon:', hourly.icon)

		now = datetime.datetime.today()
		mod = now.hour
		print(mod)
		output = "This is the 12 hour forecast for SIUE\n"
		for i in range(0, 13, 2):
			output+=((str(i+mod)+":00 -- "))
			temp=hourly.get_hour(i)['temperature']
			temp = ((temp*9)/5)+32
			output+=(str(round(temp)) + "º F, ")
			output+=(str(int(hourly.get_hour(i)['precipProbability']*100)) + "% chance to rain, ")
			output+=(str(int(hourly.get_hour(i)['windSpeed'])) + " MPH wind, ")
			output+=(str(int(hourly.get_hour(i)['humidity']*100)) + "% humidity\n")

		output += "Accurate within +/-2U.  Brought to you by Carls Jr and Darksky"
		return(output)


#this function is passed a message and decides what all to do with it.  Details inline.
async def public(message):

	#print content to console for my records
	print(str(message.author.name) + " in " + str(message.channel.name) +" said \n\t" + ascii(message.content))

	author = message.author
	global saved
	global _skip_flag
	global q
	saved = message.channel
	global player
	global session
	global dank
	global board
	global wordStates
	#check how dank we are, if we've received too many shitposts we need to inspire those godless heathens
	if message.channel is client.get_channel(shitpostingstreet):
		dank+=1
	if dank > 6:
		dank=0
		time.sleep(random.randint(600,18000))
		outputtext = subprocess.check_output(["wget","-qO-","http://inspirobot.me/api?generate=true"])
		await client.send_message(message.channel, outputtext.decode("utf-8"))


	if message.content.lower().startswith("~play"):
		if message.author.voice_channel != None:
			await play(message)
		else:
			await client.send_message(message.channel, "You must be in a voice channel to use voice commands")
	elif message.content.lower().startswith("~skip"):
		if message.author.voice_channel != None:
			_skip_flag = True
		else:
			await client.send_message(message.channel, "You must be in a voice channel to use voice commands")
	elif message.content.lower().startswith("~queue"):
		if message.channel != None:
			q.put(message)
			await client.send_message(message.channel, "Enqueued "+message.content[6:])
	elif message.content.lower().startswith("~qlist"):
		if q.empty():
			await client.send_message(message.channel,"No songs in queue.")
		else:
			outp = "Requested Songs:\n"
			tq = queue.Queue(maxsize = 0)
			while not q.empty():
				temp = q.get()
				outp = outp + temp.content[6:] + "\n"
				tq.put(temp)
			q = tq
			await client.send_message(message.channel,outp)
	elif message.content.lower().startswith("~help"):
		await client.send_message(message.channel, "no")
	elif message.content.lower().startswith("ayy"):
		await client.send_message(message.channel, "lmao")
	elif message.content.lower().startswith("heh"):
		await client.send_message(message.channel, "*Teleports behind you*")
		await asyncio.sleep(1)
		await client.send_message(message.channel, "Nothing personnel, kid")
	elif message.content.lower().startswith("wew"):
		await client.send_message(message.channel, "lads")
	elif message.content.lower().startswith("thanks bot"):
		await client.send_message(message.channel, "You're Welcome")
	elif message.content.lower().startswith("sorry bot"):
		await client.send_message(message.channel, "Its OK.  Its what I'm here for.")
	elif message.content.lower().startswith("rip") or message.content.lower().startswith("~rip") or message.content.lower().startswith("r.i.p"):
		await client.send_message(message.channel, "o7")
	elif message.content == ("DICKS"):
		await client.send_message(message.channel, "OUT")
	elif message.content.lower().startswith("~weather"):
		output = await weather()
		await client.send_message(message.channel, output)
	elif message.content.startswith("WAKE ME UP"):
		await client.send_message(message.channel, "(CAN'T WAKE UP)")
	elif "wetback" in message.content.lower():
		await client.send_message(message.channel, "o7")
	elif message.content.lower().startswith("~inspire"):
		#this uses wget, a linux terminal command to get an inspirational image.  The URL seen below, if plugged into a browser, will give the URL of a new generated image.  wget is a command to access and return contents of a webpage.  When this line is ran outputtext will be the URL of a new image, so we make sure its decoded correctly then post it.  Discord will embed the image automatically, but in the future I would like to have the bot post the actual image, instead of relying on Discord's embed.
		outputtext = subprocess.check_output(["wget","-qO-","http://inspirobot.me/api?generate=true"])
		await client.send_message(message.channel, outputtext.decode("utf-8"))
	elif message.content.count("(╯°□°）╯︵ ┻━┻") > 0:
		await client.send_message(message.channel, "┬─┬﻿ ノ( ゜-゜ノ)")
	elif message.content.lower().startswith("~lenny"):
		await client.send_message(message.channel, "( ͡° ͜ʖ ͡°)")
	elif message.content.lower().startswith(("~restart","~reboot")):
		client.close()
		client.logout()
		time.sleep(1)
		subprocess.check_output(["reboot"])
	elif message.content.lower().startswith(("~ip","ipconfig","ifconfig")):
		await client.send_message(message.channel, subprocess.check_output(["ifconfig"]))
	elif message.content.lower().startswith("fuck you"):
		await client.send_message(message.channel, "That's rude, <@!"+message.author.id+">")
	elif message.content.lower().startswith("~r"):
		#regex to search for # of dice (number before 'd') if no number specified default fo 1
		t=re.search("([0-9])+(d)", message.content.lower())
		if t:
			#get entire matching part of string except for the last char (the d) that we drop
			numberofdice=int(t.group(0)[0:-1])
		else:
			numberofdice=1
		print("number: "+str(numberofdice))
		#same process for dice size, except the d will be leading not trailing
		dicesize=int(re.search("(d)([0-9])+", message.content.lower()).group(0)[1:])
		print("size: "+str(dicesize))
		#to prevent breakage cap at 100 dice
		if numberofdice > 100:
			numberofdice = 100
			time.sleep(1)
			await client.send_message(message.channel, "Wait, I don't have that many dice, I'll roll 100")
		print(str(numberofdice+dicesize))
		total=0
		current=random.randint(1,dicesize)
		response=""
		total+=current
		response+=str(current)
		#go through and generate our numbers.
		for i in range (1, numberofdice):
			#add results to output string and to "total"
			response+=", "
			current=random.randint(1,dicesize)
			total+=current
			#crits are bold
			if current != 20:
				response+=str(current)
			else:
				response+="**"+str(current)+"**"
		t=re.search("(\+)([0-9])+", message.content.lower())
		if t:
			#get entire matching part of string except for the last char (the d) that we drop
			dicemod=int(t.group(0)[1:])
		else:
			dicemod=0
		#print list of results + total sum
		if not int(dicemod) > 0:
			dicemod = 0
		await client.send_message(message.channel, response+"\nTotal of: "+str(total+dicemod))
	elif message.content.lower().startswith("~map"):
		f = open("map.txt", "r+")
		msg = await client.send_message(message.channel, f.read())
		f.close()
		session = True
		while session:
			f = open("map.txt", "r+")
			time.sleep(2)
			await client.edit_message(msg, f.read())
	elif message.content.lower().startswith("~endmap"):
		session = False
	elif message.content.lower().startswith("~ff"):
		await ffmpeg(message)
	elif message.content.lower().startswith("~auroraborealis"):
		await client.send_message(message.channel, "At this time of year, at this time of day, in this part of the country, localized entirely within your kitchen?")
	elif message.content.lower().startswith("~credits"):
		await client.send_message(message.channel, "Dale made this bot, but Jacob made this command.")
	elif message.content.lower().startswith("in awe at the size of this lad"):
		await client.send_message(message.channel, "Absolute unit")
	elif message.content.lower().startswith("~clearq"):
		await rmq(message)
	elif message.content.lower().startswith("~game"):
		await client.send_message(message.channel, "Oh nice, I love playing "+message.content[6:]+"!")
		mygame = discord.Game(name=message.content[6:])
		await client.change_status(game=mygame)
	elif message.content.lower().startswith("~crash"):
		print("Exiting...\n\n")
		sys.exit()
	elif message.content.lower().startswith("~codename"):
		gamestart = True
		wordlist = open("words.txt", "r").read()
		board = []
		for a in range(0, 36):
			r = random.randint(0, len(wordlist.split("\n"))-1 )
			board.append('{word: <14}'.format(word=wordlist.split("\n")[r])[:-2]+"  ")

		#playing field initialized, post it
		outstring = ""
		c = 0
		for instance in board:
			outstring += instance
			c += 1
			if c > 5:
				c = 0
				outstring += "\n"
		await client.send_message(message.channel, outstring)

		wordStates = shuffle(wordStates)

		# POPULATE wordStates

	elif message.content.lower().startswith("~flip"):
               #playing field initialized, post it
		for each in range(0, len(board)):
			if board[each].split(" ")[0].lower() == message.content.lower().split(" ")[1]:
				if board[each][0] != "*":
					if wordStates[each] == 0:
						client.send_message(message.channel, "That card was Red")
						board[each] = "*"+board[each].split(" ", 1)[0]+"*"+board[each].split(" ", 1)[1]
					if wordStates[each] == 1:
						client.send_message(message.channel, "That card was Blue")
						board[each] = "*"+board[each].split(" ", 1)[0]+"*"+board[each].split(" ", 1)[1]
					if wordStates[each] == 2:
						client.send_message(message.channel, "That card was a civilian.  It is now the other teams turn.")
						board[each] = "~~"+board[each].split(" ", 1)[0]+"~~"+board[each].split(" ", 1)[1]
					if wordStates[each] == 3:
						client.send_message(message.channel, "That card was the Assassin.  Game over.  You lose")
						break
				else:
					client.send_message(message.channel, "That card has already been flipped")

		outstring = ""


		c = 0
		for instance in board:
			outstring += instance
			c += 1
			if c > 5:
				c = 0
				outstring += "\n"
		await client.send_message(message.channel, outstring)

	elif message.content.lower().startswith("~spy"):
		masterList = ""
		for each in range(0, len(board)):
			if wordStates[each] == 0:
				 masterList += board[each] + " is red"
			if wordStates[each] == 1:
				 masterList += board[each] + " is blue"
			if wordStates[each] == 0:
				 masterList += board[each] + " is civilian"
			if wordStates[each] == 0:
				 masterList += board[each] + " is assassin"
			wordList += "\n"

			client.send_message(message.author, masterList)


	#1 in 50 chance to react with a random server-specific image
	if random.randint(0,50) == 0:
		list = []
		for e in client.get_all_emojis():
			print(str(e))
			list.append(e)
		await client.add_reaction(message, list[random.randint(0,len(list)-1)])



#Discord event listener.  When  we recieve a message pass it to public() which handles that stuff
@client.event
async def on_message(message):
	await public(message)

#Discord event listener.  When a reaction is added, the bot adds that same reaction.  We also update that user's emoji count
@client.event
async def on_reaction_add(reaction, user):
	await client.add_reaction(reaction.message, reaction.emoji)
	for u in users:
		if u.ID == user.id:

			u.emojis+=1

#Discord event listener.  If a reaction is removed from a post we update that user's emoji count.  If that was the last reaction we also remove the bot's
@client.event
async def on_reaction_remove(reaction, user):
	if reaction.count == 1:
		await client.remove_reaction(reaction.message, reaction.emoji, client.user)
	for u in users:
		if u.ID == user.id:
			u.emojis-=1


#Discord event listener.  This is run when the bot is finished launching
@client.event
async def on_ready():
	print("Bot running.")
	global started
	global calendar
	global users

#uggh can I just leave the voice parts uncommented?  no?  shit.
async def voiceCmd(message):

	#there's going to be some light fuckery going on so lets make it so we don't have to worry about scope.
	global voice
	global player
	global _in_voice
	global q
	global _skip_flag

	#this is slightly redundant, since the voice commands should never even get this function called if the user isn't in a channel.
	#we just double check to make sure they are in fact in voice since things break if they aren't
	if message.author.voice_channel != None:
		#first check if we already have a player make...
		if not player == None:
			#...if we do, then what we do is add their song to the front of the queue and skip the current song
			#make a temp queue, add their message,
			tq = queue.Queue(maxsize = 0)
			tq.put(message)

			#then copy over the contents of the old queue to the temp queue
			while not q.empty():
				tq.put(q.get())

			#and set the old queue to be equal to the temp queue.
			q = tq

			#finally we enable out global skip flag.  Our manager will skip the song very soon.
			_skip_flag = True

			#we did what we needed to let's leave before we break more than we probably already did
			return 0

		#we check our flag to see if we are in voice.  If we are not...
		if not _in_voice:
			#...then we get in voice!  set the flag...
			_in_voice = True
			#...make it clear we are joining, then join the same channel the poster was in.
			await client.send_message(message.channel, "Attempting to join...")
			voice = await client.join_voice_channel(message.author.voice_channel)

	#this is the slightly redundant part.
	elif not _in_voice:
		await client.send_message(message.channel, "Please be in a voice channel to make requests")
		return 0

	if len(message.content.split(" ")) == 0:
		await client.send_message(message.channel, "I don't think you gave me a song to play?  Please try again.")
		return 0
	#it can cause issues because sometimes message.content starts with ~play and sometimes ~queue, so we drop the parts before the first space
	address = message.content.split(" ", 1)[1]
	#if the user uploaded a URL then we just use that URL as a video.  Otherwise, we reformat the string to search youtube.
	#this is to the specifications of youtube-dl, which is some good shit :ok_hand: good shit right there
	if not address.startswith("https://"):
		video = "ytsearch:"+address

	#if player is still up.  Stop.  Why are you up you don't need to do that'll it'll break everything.
	if player != None:
		player.stop()

	#do some good ol fashioned unix based black magic to jump in voice and then download and start a song.
	player = await voice.create_ytdl_player(video)
	await client.send_message(message.channel, "Starting "+player.title)
	player.start()


	#here we just wait for the song to finish.  If ever the skip flag is enabled then we stop the song, allowing us to progress.
	while player.is_playing():
		await asyncio.sleep(1)
		if _skip_flag:
			player.pause()
			_skip_flag = False

	#once we finish, either because the song ended or we skipped it, we stop and close the player then return the number of songs left to play.
	player.stop()
	player = None
	return q.qsize()

#this is the manager for voice
async def play(message):
	#again, we need some variables
	global q
	global voice
	global _in_voice
	ours = message

	#Recall that voiceCmd() returns the size of the queue.  As long as the queue has something in it we play the next song.
	#Actual process looks like this:  get song from queue ==> pass song to voiceCmd(), waiting for it to finish ==> check if we need to repeat
	while (await voiceCmd(ours)) > 0:
		ours = q.get()

	#if the queue if finally empty we are done and need to disconnect.
	await voice.disconnect()
	_in_voice = False

async def ffmpeg(message):
	global voice
	global player
	#do some good ol fashioned unix based black magic to jump in voice and then download and start a song.
	if player is not None:
		player.stop()
		await voice.disconnect()
		player = None
		voice = None
	voice = await client.join_voice_channel(message.author.voice_channel)
	player = voice.create_ffmpeg_player("test.mp3")
	#await client.send_message(message.channel, "Starting "+player.title)
	player.start()

async def rmq(message):
	global q
	tq = queue.Queue(maxsize = 0)
	#then copy over the contents of the old queue to the temp queue
	while not q.empty():
		t = q.get()
		if not (t.content.lower().split(" ",1)[1] == message.content.lower().split(" ",1)[1]):
			tq.put(t)
		time.sleep(1)

	#and set the old queue to be equal to the temp queue.
	q = tq

#actually starts the bot.  client.run() gets passes my client secret, which is basically botty mcbotface's soul
print("Launching bot...")
client.run("NDQzOTgzNTA0MzQ3MjM0MzE0.Dt4bUQ.uaAiExgl6FI5WspyjHh57RB2dFg")
