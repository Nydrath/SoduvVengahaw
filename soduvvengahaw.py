import sys
import os
import time
import random
import socket
import string
from math import *

from PIL import Image
from imgurpython import ImgurClient

import decks

with open("corpus", "w") as f:
    f.write(str(os.getpid()))

def parsemsg(s):
    # Stolen from Twisted. Parses a message to it's prefix, command and arguments.
    prefix = ''
    trailing = []
    if s == "":
        print("Empty line.")
    if s[0] == ':':
        prefix, s = s[1:].split(' ', 1)
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()
    command = args.pop(0)
    return prefix, command, args


def isNumber(s):
    # Returns true if s is a number, false if not
    try:
        int(s)
        return True
    except ValueError:
        return False


class Bot:
    def __init__(self, host='irc.sorcery.net', port=6667):
        self.host = host
        self.port = port

        self.nickName = 'SoduvVengahaw'
        self.ident = 'SoduvVengahaw'
        self.realName = 'SoduvVengahaw'

        self.receiveBuffer = ""

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_id = '05c4e4c8869eb82'
        client_secret =  '711339dbcc785ad5d2da165e9bf6b22f0f4b8136'
        self.imgurclient = ImgurClient(client_id, client_secret)

        self.runeworker = None

    def connect(self):
        self.socket.connect((self.host, self.port))
        self.socket.send("NICK %s\r\n" % self.nickName)
        self.socket.send("USER %s %s bla :%s\r\n" % (self.ident, self.host, self.realName))

    def send(self, msg):
        self.socket.send('{0}\r\n'.format(msg).encode())

    def sendMsg(self, chan, msg):
        sendString = "PRIVMSG "+chan+" :"+msg
        self.send(sendString)

    def receive(self):
        self.receiveBuffer = ""
        try:
            self.receiveBuffer=self.socket.recv(1024)
        except socket.error, e:
            if e.args[0] != 11:
                # We don't just have a "no data received" error
                print(e)
                sys.exit(1)
        temp=string.split(self.receiveBuffer, "\n")
        for line in temp:
            try:
                line=string.rstrip(line)
                line=string.split(line)
            
                if(line[0]=="PING"):
                    self.socket.send("PONG %s\r\n" % line[1])
            except:
                pass

    def join(self, channel):
        self.socket.send("JOIN {} \r\n".format(channel))

    def handleInput(self):
        if len(self.receiveBuffer) > 0:
            alwaysTalk = False
            prefix, command, args = parsemsg(self.receiveBuffer)

            if command == "PRIVMSG":
                name = prefix[:prefix.index("!")]

                channel = args[0]
                if channel == self.nickName:
                    # Someone sent a private message, to send a private message back we have to use their name as a channel
                    channel = name
                    alwaysTalk = True

                inputString = args[1]
                inputString = inputString[:-2]
                if self.nickName.lower() in inputString.lower() or alwaysTalk:
                    time.sleep(0.4)
                    if "rune" in inputString.lower():
                        card = random.choice(decks.RUNES)
                        if "spread" in inputString.lower():
                            if self.runeworker == None:
                                runes = random.sample(decks.RUNES, 3)
                                self.runeworker = RuneWorker(channel, name, runes)
                                card = "Throwing runes.."
                            else:
                                card = "Already creating a spread. Please wait."
                    elif "morgan" in inputString.lower():
                        if "spread" in inputString.lower():
                            card = ' / '.join(random.sample(decks.MORGAN, 3))
                        else:
                            card = random.choice(decks.MORGAN)
                    elif "spread" in inputString.lower():
                        card = ' / '.join(random.sample(decks.THOTH, 3))
                    else:
                        card = random.choice(decks.THOTH)
                    self.sendMsg(channel, name+": "+card)

    def checkrunes(self):
        if self.runeworker != None:
            if not self.runeworker.done:
                self.runeworker.work()
            else:
                upload = self.imgurclient.upload_from_path(os.getcwd()+"/runethrow.png")
                self.sendMsg(self.runeworker.channel, self.runeworker.querent+": "+upload['link'])
                self.runeworker = None

class RuneWorker:
    RUNEWIDTH = 149
    RUNEHEIGHT = 197
    IMAGE_WIDTH = RUNEWIDTH*5
    IMAGE_HEIGHT = RUNEHEIGHT*2

    # This class relies on each function happening fast enough that the IRC won't disconnect the bot, to simulate nonblocking.
    # As such, it isn't guaranteed portable anymore. Ugly, but only way I know of without using subprocess.

    def __init__(self, channel, querent, runes):
        self.done = False
        self.channel = channel
        self.querent = querent
        self.images = []
        self.runenames = runes
        self.positions = []
        self.background = Image.new('RGB', (self.IMAGE_WIDTH, self.IMAGE_HEIGHT), (0,0,0))

    def work(self):
        if len(self.runenames) > 0:
            # We're not done opening all the runes yet, unpack the next one
            rune = self.runenames.pop(0)
            index = decks.RUNES.index(rune)
            name = "[{0}] ".format(index+1) + rune.split()[0] + ".png"
            self.images.append(Image.open("Runes/"+name))
        elif len(self.images) > 0:
            # We're not done pasting all the images yet, paste the next one
            while True:
                x, y = random.randint(1, self.IMAGE_WIDTH-self.RUNEWIDTH), random.randint(1, self.IMAGE_HEIGHT-self.RUNEHEIGHT)
                colliding = False
                for otherx, othery in self.positions:
                    if x in range(otherx-self.RUNEWIDTH-1, otherx+self.RUNEWIDTH+1) and y in range(othery-self.RUNEHEIGHT-1, othery+self.RUNEHEIGHT+1):
                        colliding = True
                        break
                if not colliding:
                    break
            # We have the future position of this rune
            self.positions.append((x, y))
            self.background.paste(self.images.pop(0), (x, y))
        else:
            self.background.save("runethrow.png")
            self.done = True
            

bot = Bot()
bot.connect()
time.sleep(2)
bot.receive()
bot.join("#/div/ination")
bot.socket.setblocking(False)
while True:
    bot.receive()
    bot.handleInput()
    bot.checkrunes()

    try:
        with open("corpus", "r") as f:
            pass
    except:
        sys.exit(1)

