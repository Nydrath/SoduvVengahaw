import sys, os, time, random, math, socket, string, pickle
from decks import RW_DECK, THOTH_DECK, RUNES

with open("corpus", "w") as f:
    f.write(str(os.getpid()))
import soduvvengahaw.spark

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

    def __init__(self, host='eu.sorcery.net', port=9000):
        self.host = host
        self.port = port

        self.nickName = 'SoduvVengahaw'
        self.ident = 'SoduvVengahaw'
        self.realName = 'SoduvVengahaw'

        self.receiveBuffer = ""

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        with open("quotes", "r") as f:
            self.quotes = f.readlines()

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
        self.receiveBuffer=self.socket.recv(1024)
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
        alwaysTalk = False
        prefix, command, args = parsemsg(self.receiveBuffer)

        if command == "PRIVMSG":
            channel = args[0]
            if channel == self.nickName:
                # Someone sent a private message, to send a private message back we have to use their name as a channel
                channel = prefix[:prefix.index("!")]
                alwaysTalk = True

            inputString = args[1]
            inputString = inputString[:-2]
            if self.nickName.lower() in inputString.lower() or alwaysTalk:
                time.sleep(0.4)
                if "quote" in inputString.lower():
                    card = random.choice(self.quotes)
                elif "rw" in inputString.lower():
                    card = random.choice(RW_DECK)
                    if "spread" in inputString.lower():
                        card = ' / '.join(random.sample(RW_DECK, 3)) 
                elif "rune" in inputString.lower():
                    card = random.choice(RUNES)
                    if "spread" in inputString.lower():
                        card = ' / '.join(random.sample(RUNES, 3))
                elif "spread" in inputString.lower():
                    card = ' / '.join(random.sample(THOTH_DECK, 3))
                else:
                    card = random.choice(THOTH_DECK)
                self.sendMsg(channel, prefix[:prefix.index("!")]+": "+card)

bot = Bot()
bot.connect()
time.sleep(2)
bot.join("#/div/ination")
while True:
    bot.receive()
    bot.handleInput()

    try:
        with open("life", "r") as f:
            pass
    except:
        sys.exit(1)
