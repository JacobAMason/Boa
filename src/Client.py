#!python
__author__ = 'JacobAMason'

import sys
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
import StringIO


class Bot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname)

    def joined(self, channel):
        print "Joined %s." % (channel)

    def privmsg(self, user, channel, message):
        if not message.startswith(self.nickname):
            return
        else:
            idx = message.find(' ')
            message = message[idx+1:]

        # create file-like string to capture output
        codeOut = StringIO.StringIO()
        codeErr = StringIO.StringIO()

        # capture output and errors
        sys.stdout = codeOut
        sys.stderr = codeErr

        errorText = ""
        try:
            exec message
        except Exception, err:
            errorText = str(err)

        # restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        s = codeErr.getvalue()
        if s:
            self.msg(channel, "error: %s\n" % s)

        if errorText:
            self.msg(channel, "error: %s\n" % errorText)

        s = codeOut.getvalue()
        if s:
            self.msg(channel, "%s" % s)

        codeOut.close()
        codeErr.close()

    def dataReceived(self, bytes):
        print str(bytes).rstrip()
        # Make sure to up-call - otherwise all of the IRC logic is disabled!
        return irc.IRCClient.dataReceived(self, bytes)


class BotFactory(protocol.ClientFactory):
    protocol = Bot

    def __init__(self, channel, nickname="Boa"):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting..." % (reason)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason)


if __name__ == "__main__":
    channel = sys.argv[1]
    nickname = sys.argv[2]
    reactor.connectTCP("coop.test.adtran.com", 6667,
                       BotFactory('#' + channel, nickname))
    reactor.run()
