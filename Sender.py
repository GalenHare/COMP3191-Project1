import sys
import getopt
import datetime
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

    def makePackets(self):
        lst = []
        packetList = []
        fSplit = self.infile.read(1472)
        while fSplit:
            lst.append(fSplit)
            fSplit = self.infile.read(1472)

        packetList.append(self.make_packet("syn",0,""))
        for i in range(len(lst)-1):
            packetList.append(self.make_packet("dat",i+1,lst[i]))

        packetList.append(self.make_packet("fin",len(lst),lst[len(lst)-1]))
        return packetList


    # Main sending loop.
    def start(self):
      #split up packets
      packetSplit = self.makePackets()
      recvBuffer = None 
      while(not recvBuffer):
        try:
          self.send(packetSplit[0])
          recvBuffer = self.receive()
        except (KeyboardInterrupt, SystemExit):
          exit()

      msg_type, seqno, data, checksum = self.split_packet(recvBuffer)
      print(msg_type + " " + seqno + " " + data + " " + checksum)
      #start sending packets
      base = 1
      nextSeqNum = 1
      N = 7
      while(True):
        try:
          if(seqno==0):
            if(recvBuffer and Checksum.validate_checksum(recvBuffer)):
                msg_type, seqno, data, checksum = self.split_packet(recvBuffer)
                print(msg_type + " " + seqno + " " + data + " " + checksum)
                base = seqno
          if(nextSeqNum < int(base)+N):
            self.send(packetSplit[nextSeqNum])
            if(base==nextSeqNum):
              a = datetime.datetime.now()
            nextSeqNum= nextSeqNum+1
            if((datetime.datetime.now() - a).microseconds >= 500000 or (datetime.datetime.now() - a).seconds >= 1 ):
              n=0
              while((n+base)<nextSeqNum):
                self.send(packetSplit[base+n])
                n = n+1
            recvBuffer = self.receive()
            if(recvBuffer and Checksum.validate_checksum(recvBuffer)):
              msg_type, seqno, data, checksum = self.split_packet(recvBuffer)
              print(msg_type + " " + seqno + " " + data + " " + checksum)
              base = seqno
              if(base == nextSeqNum):
                pass
              else:
                a = datetime.datetime.now()
              #check if ack received is the one we expect 
        except (KeyboardInterrupt, SystemExit):
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
