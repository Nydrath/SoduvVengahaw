import sys, os, time, random, math, socket, string, pickle

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
    # Album: http://imgur.com/a/24ByN
    THOTH_DECK = [  "0 - The Fool { http://i.imgur.com/PQ2nG95.jpg }",
                    "I - The Magus { http://i.imgur.com/qItZSaz.jpg }",
                    "II - The Priestess { http://i.imgur.com/joRLHGK.jpg }",
                    "III - The Empress { http://i.imgur.com/1xiJAUq.jpg }",
                    "IV - The Emperor { http://i.imgur.com/yVKoH2j.jpg }",
                    "V - The Hierophant { http://i.imgur.com/8q8wkZv.jpg }",
                    "VI - The Lovers { http://i.imgur.com/7fBAtUv.jpg }",
                    "VII - The Chariot { http://i.imgur.com/axTt8o6.jpg }",
                    "VIII - Adjustment { http://i.imgur.com/jFK0rW9.jpg }",
                    "IX - The Hermit { http://i.imgur.com/vKjpFv6.jpg }",
                    "X - Fortune { http://i.imgur.com/SfcEUFi.jpg }",
                    "XI - Lust { http://i.imgur.com/pybCauK.jpg }",
                    "XII - The Hanged Man { http://i.imgur.com/NH0vt4j.jpg }",
                    "XIII - Death { http://i.imgur.com/0RG898u.jpg }",
                    "XIV - Art { http://i.imgur.com/G91EXFL.jpg }",
                    "XV - The Devil { http://i.imgur.com/RnRASpz.jpg }",
                    "XVI - The Tower { http://i.imgur.com/S6Z2f1f.jpg }",
                    "XVII - The Star { http://i.imgur.com/3yYIGvm.jpg }",
                    "XVIII - The Moon { http://i.imgur.com/wECfVYO.jpg }",
                    "XIX - The Sun { http://i.imgur.com/NGwTuoK.jpg }",
                    "XX - The Aeon { http://i.imgur.com/LhXJy0f.jpg }",
                    "XXI - The Universe { http://i.imgur.com/HDwUWBF.jpg }",
                    "Ace of Wands { http://i.imgur.com/UK2efBo.jpg }",
                    "2 of Wands - Dominion { http://i.imgur.com/fbzFflB.jpg }",
                    "3 of Wands - Virtue { http://i.imgur.com/DwU6See.jpg }",
                    "4 of Wands - Completion { http://i.imgur.com/LiMx96X.jpg }",
                    "5 of Wands - Strife { http://i.imgur.com/rPlrbyT.jpg }",
                    "6 of Wands - Victory { http://i.imgur.com/YyB5fCr.jpg }",
                    "7 of Wands - Valour { http://i.imgur.com/nE0HLRN.jpg }",
                    "8 of Wands - Swiftness { http://i.imgur.com/ChFeclc.jpg }",
                    "9 of Wands - Strength { http://i.imgur.com/wEod3NT.jpg }",
                    "10 of Wands - Oppression { http://i.imgur.com/QipWoV0.jpg }",
                    "Knight of Wands { http://i.imgur.com/sDVt9RW.jpg }",
                    "Queen of Wands { http://i.imgur.com/cL17LkX.jpg }",
                    "Prince of Wands { http://i.imgur.com/mB468fd.jpg }",
                    "Princess of Wands { http://i.imgur.com/XMO3bNF.jpg }",
                    "Ace of Cups { http://i.imgur.com/qm5f07V.jpg }",
                    "2 of Cups - Love { http://i.imgur.com/AsweI48.jpg }",
                    "3 of Cups - Abundance { http://i.imgur.com/wzQVmtq.jpg }",
                    "4 of Cups - Luxury { http://i.imgur.com/ONZVO0P.jpg }",
                    "5 of Cups - Disappointment { http://i.imgur.com/xvuIqvn.jpg }",
                    "6 of Cups - Pleasure { http://i.imgur.com/Od1qfVh.jpg }",
                    "7 of Cups - Debauch { http://i.imgur.com/h2F7eFh.jpg }",
                    "8 of Cups - Indolence { http://i.imgur.com/PxdiTDy.jpg }",
                    "9 of Cups - Happiness { http://i.imgur.com/JLGko7R.jpg }",
                    "10 of Cups - Satiety { http://i.imgur.com/Wmm2lQL.jpg }",
                    "Knight of Cups { http://i.imgur.com/rbQZuJ0.jpg }",
                    "Queen of Cups { http://i.imgur.com/WdvOb9X.jpg }",
                    "Prince of Cups { http://i.imgur.com/CqfClbW.jpg }",
                    "Princess of Cups { http://i.imgur.com/BsgXCEO.jpg }",
                    "Ace of Swords { http://i.imgur.com/nbGXZMt.jpg }",
                    "2 of Swords - Peace { http://i.imgur.com/kpwBVKZ.jpg }",
                    "3 of Swords - Sorrow { http://i.imgur.com/0z9d1hY.jpg }",
                    "4 of Swords - Truce { http://i.imgur.com/9LNCSNC.jpg }",
                    "5 of Swords - Defeat { http://i.imgur.com/Gub5DXA.jpg }",
                    "6 of Swords - Science { http://i.imgur.com/etB8X8E.jpg }",
                    "7 of Swords - Futility { http://i.imgur.com/gk1ivXT.jpg }",
                    "8 of Swords - Interference { http://i.imgur.com/8eXSUQj.jpg }",
                    "9 of Swords - Cruelty { http://i.imgur.com/eRQ4XX4.jpg }",
                    "10 of Swords - Ruin { http://i.imgur.com/6E4h4d4.jpg }",
                    "Knight of Swords { http://i.imgur.com/YZIa5um.jpg }",
                    "Queen of Swords { http://i.imgur.com/hb0bjIQ.jpg }",
                    "Prince of Swords { http://i.imgur.com/U8CHSV9.jpg }",
                    "Princess of Swords { http://i.imgur.com/tfJ2Uu8.jpg }",
                    "Ace of Disks { http://i.imgur.com/6FszJp0.jpg }",
                    "2 of Disks - Change { http://i.imgur.com/TC3Z0dv.jpg }",
                    "3 of Disks - Works { http://i.imgur.com/ZRYRFoQ.jpg }",
                    "4 of Disks - Power { http://i.imgur.com/pDi6yuu.jpg }",
                    "5 of Disks - Worry { http://i.imgur.com/pEtyIqx.jpg }",
                    "6 of Disks - Success { http://i.imgur.com/M2HXS5A.jpg }",
                    "7 of Disks - Failure { http://i.imgur.com/ApPSuWl.jpg }",
                    "8 of Disks - Prudence { http://i.imgur.com/wg2g8gu.jpg }",
                    "9 of Disks - Gain { http://i.imgur.com/mEAyRq2.jpg }",
                    "10 of Disks - Wealth { http://i.imgur.com/Z3B5V5E.jpg }",
                    "Knight of Disks { http://i.imgur.com/iseQPhE.jpg }",
                    "Queen of Disks { http://i.imgur.com/NNi2jMu.jpg }",
                    "Prince of Disks { http://i.imgur.com/9CQeGof.jpg }",
                    "Princess of Disks { http://i.imgur.com/i2lye5C.jpg }"
                 ]

    # Album: http://imgur.com/a/zBwe3
    RW_DECK = [     "0 - The Fool { http://i.imgur.com/xwIpqIC.jpg }",
                    "I - The Magician { http://i.imgur.com/mxJtSKd.jpg }",
                    "II - The High Priestess { http://i.imgur.com/d764bKL.jpg }",
                    "III - The Empress { http://i.imgur.com/BVMYp3Z.jpg }",
                    "IV - The Emperor { http://i.imgur.com/VxmSea8.jpg }",
                    "V - The Hierophant { http://i.imgur.com/VbHYvph.jpg }",
                    "VI - The Lovers { http://i.imgur.com/lwsa3LM.jpg }",
                    "VII - The Chariot { http://i.imgur.com/LRMtkTi.jpg }",
                    "VIII - Strength { http://i.imgur.com/rtUPtsZ.jpg }",
                    "IX - The Hermit { http://i.imgur.com/BJVCRmh.jpg }",
                    "X - Wheel of Fortune { http://i.imgur.com/TEceoge.jpg }",
                    "XI - Justice { http://i.imgur.com/xaNM3PW.jpg }",
                    "XII - The Hanged Man { http://i.imgur.com/XL6jhjQ.jpg }",
                    "XIII - Death { http://i.imgur.com/vN8frAu.jpg }",
                    "XIV - Temperance { http://i.imgur.com/b1g6FlS.jpg }",
                    "XV - The Devil { http://i.imgur.com/ppC8WVB.jpg }",
                    "XVI - The Tower { http://i.imgur.com/aBv2lbO.jpg }",
                    "XVII - The Star { http://i.imgur.com/S3WZmhm.jpg }",
                    "XVIII - The Moon { http://i.imgur.com/oZtqyCr.jpg }",
                    "XIX - The Sun { http://i.imgur.com/dalzqXX.jpg }",
                    "XX - Judgement { http://i.imgur.com/1DrOwqp.jpg }",
                    "XXI - The World { http://i.imgur.com/aRGuRFG.jpg }",
                    "Ace of Wands { http://i.imgur.com/DabavYD.jpg }",
                    "2 of Wands { http://i.imgur.com/BMU6WWF.jpg }",
                    "3 of Wands { http://i.imgur.com/GLj7gSc.jpg }",
                    "4 of Wands { http://i.imgur.com/UPqeaU3.jpg }",
                    "5 of Wands { http://i.imgur.com/8bayVFQ.jpg }",
                    "6 of Wands { http://i.imgur.com/y2PDGpt.jpg }",
                    "7 of Wands { http://i.imgur.com/vEbIZC5.jpg }",
                    "8 of Wands { http://i.imgur.com/63Gs9p7.jpg }",
                    "9 of Wands { http://i.imgur.com/DK5D6WT.jpg }",
                    "10 of Wands { http://i.imgur.com/BFKf1UI.jpg }",
                    "King of Wands { http://i.imgur.com/TC4ulvh.jpg }",
                    "Queen of Wands { http://i.imgur.com/qW1mEme.jpg }",
                    "Knight of Wands { http://i.imgur.com/e6KDbgR.jpg }",
                    "Page of Wands { http://i.imgur.com/Yd2jSck.jpg }",
                    "Ace of Cups { http://i.imgur.com/C7tqudR.jpg }",
                    "2 of Cups { http://i.imgur.com/lRYMKvv.jpg }",
                    "3 of Cups { http://i.imgur.com/k3OOClg.jpg }",
                    "4 of Cups { http://i.imgur.com/5a9PJMq.jpg }",
                    "5 of Cups { http://i.imgur.com/CCqnB7K.jpg }",
                    "6 of Cups { http://i.imgur.com/6EYsVJI.jpg }",
                    "7 of Cups { http://i.imgur.com/eKoqpps.jpg }",
                    "8 of Cups { http://i.imgur.com/e4Ga7nE.jpg }",
                    "9 of Cups { http://i.imgur.com/l4Ws2gO.jpg }",
                    "10 of Cups { http://i.imgur.com/dCgX4Ia.jpg }",
                    "King of Cups { http://i.imgur.com/kva3dt9.jpg }",
                    "Queen of Cups { http://i.imgur.com/kJtgSAQ.jpg }",
                    "Knight of Cups { http://i.imgur.com/uqqqLUq.jpg }",
                    "Page of Cups { http://i.imgur.com/UUR02Qn.jpg }",
                    "Ace of Swords { http://i.imgur.com/WnHJVUz.jpg }",
                    "2 of Swords { http://i.imgur.com/hbeuU1m.jpg }",
                    "3 of Swords { http://i.imgur.com/Ut69sBV.jpg }",
                    "4 of Swords { http://i.imgur.com/2jHpfqL.jpg }",
                    "5 of Swords { http://i.imgur.com/iWeFBUh.jpg }",
                    "6 of Swords { http://i.imgur.com/nGvrP0t.jpg }",
                    "7 of Swords { http://i.imgur.com/wOHMCCj.jpg }",
                    "8 of Swords { http://i.imgur.com/EvRHCRT.jpg }",
                    "9 of Swords { http://i.imgur.com/XBpVh02.jpg }",
                    "10 of Swords { http://i.imgur.com/zv74MLW.jpg }",
                    "King of Swords { http://i.imgur.com/OqVhsfE.jpg }",
                    "Queen of Swords { http://i.imgur.com/6ztXVin.jpg }",
                    "Knight of Swords { http://i.imgur.com/sJfwrdN.jpg }",
                    "Page of Swords { http://i.imgur.com/qO0XgXa.jpg }",
                    "Ace of Pentacles { http://i.imgur.com/3mglLg1.jpg }",
                    "2 of Pentacles { http://i.imgur.com/RQORVBu.jpg }",
                    "3 of Pentacles { http://i.imgur.com/ubGCBP8.jpg }",
                    "4 of Pentacles { http://i.imgur.com/rx0nXma.jpg }",
                    "5 of Pentacles { http://i.imgur.com/SxOpbH1.jpg }",
                    "6 of Pentacles { http://i.imgur.com/izANDOZ.jpg }",
                    "7 of Pentacles { http://i.imgur.com/Y180oId.jpg }",
                    "8 of Pentacles { http://i.imgur.com/AikIqPX.jpg }",
                    "9 of Pentacles { http://i.imgur.com/aadANyr.jpg }",
                    "10 of Pentacles { http://i.imgur.com/5W91m6C.jpg }",
                    "King of Pentacles { http://i.imgur.com/In9i1FZ.jpg }",
                    "Queen of Pentacles { http://i.imgur.com/55RpqQY.jpg }",
                    "Knight of Pentacles { http://i.imgur.com/p1291Jn.jpg }",
                    "Page of Pentacles { http://i.imgur.com/xxPXOML.jpg }"
                 ]

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
                    card = random.choice(self.RW_DECK)
                else:
                    card = random.choice(self.THOTH_DECK)
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