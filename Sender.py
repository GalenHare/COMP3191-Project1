import sys
import getopt
import time

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sackMode = sackMode
        self.debug = debug
        self.window = 7
        self.timeout = 0.5
        self.packetSize = 1471
        self.base = 1
        self.nextSeqNo = 1
        self.packetList = None
        self.timer = True
        self.curAck = None
        self.fastTransmit = False
        self.counter=0

    def log(self,label,msg):
      if debug:
        msg_type, seqNo, data, checksum = self.split_packet(msg)
        if self.sackMode:
          pass
        else:
          print("Sender.py: %s %s|%d|%s|%s" % (label, msg_type, int(seqNo), data[:5], checksum))

    def makePackets(self):
      lst = []
      packetList = []
      fSplit = self.infile.read(self.packetSize)
      while fSplit:
        lst.append(fSplit)
        fSplit = self.infile.read(self.packetSize)

      packetList.append(self.make_packet("syn",0,""))
      for i in range(len(lst)-1):
        packetList.append(self.make_packet("dat",i+1,lst[i]))

      packetList.append(self.make_packet("fin",len(lst),lst[len(lst)-1]))
      return packetList

    def handleAck(self,msg):
      if self.sackMode:
        #gets received packets out of sack thing
        pass
      else:
        if(self.curAck==int(self.split_packet(msg)[1])):
          self.counter = self.counter + 1
        else:
          self.counter = 0
        if(self.counter >= 3):
          self.fastTransmit = True
        self.curAck = int(self.split_packet(msg)[1])
        return int(self.split_packet(msg)[1])

    def startConnection(self):
      recvBuffer = None
      while(recvBuffer==None):
        self.send(self.packetList[0])
        self.log("sent",self.packetList[0])
        recvBuffer = self.receive(0.5)
      self.log("received",recvBuffer)
      if(self.debug):
        print("Connection established")
    
    



    # Main sending loop.
    def start(self):
      # add things here
      self.packetList = self.makePackets()
      self.startConnection()
      while True:
        try:
          while(self.nextSeqNo < self.base+self.window and self.fastTransmit == False):
            if(self.nextSeqNo >= len(self.packetList)):
              break
            self.send(self.packetList[self.nextSeqNo])
            self.log("sent",self.packetList[self.nextSeqNo])
            if(self.base==self.nextSeqNo):
              self.log("Timer started at:",self.packetList[self.nextSeqNo])
              self.timer = True
              a=time.time()
            self.nextSeqNo = self.nextSeqNo + 1
          if(time.time()-a > 0.5 and self.timer==True or self.fastTransmit == True):
            a= time.time()
            for i in range(self.base,self.nextSeqNo):
              self.send(self.packetList[i])
              self.log("resending",self.packetList[i])
          recvBuffer = self.receive(0.5)
          if(not(recvBuffer==None) and Checksum.validate_checksum(recvBuffer)):
            self.log("received",recvBuffer)
            self.base = self.handleAck(recvBuffer)
            if(self.base >= len(self.packetList)):
              if(self.debug):
                print("Exiting...")
              exit()
            if(self.base == self.nextSeqNo):
              self.timer = False
            else:
              self.timer = True
              a = time.time()
              if(not(self.nextSeqNo >= len(self.packetList))):
                self.log("Timer started at:",self.packetList[self.nextSeqNo])
        except(KeyboardInterrupt, SystemExit):
          exit()
            


      
        
'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"
        print "-k | --sack Enable selective acknowledgement mode"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest,port,filename,debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
