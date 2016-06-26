import os
import ast

from twisted.internet import defer
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver

import settings

LineReceiver.MAX_LENGTH = 1024*1024*64
class FileProtocol(LineReceiver):
    def __init__(self):
        self.fp = open('check.jpg', 'ab')
        self.currentfp = None
        self.filesToSync = []

    def connectionMade(self):
        d = {'state': settings.PROTOCOL_STATE_GET_FULL_FILE_STRUCTURE}
        self.sendLine(str(d))

    def lineReceived(self, data):
        data = ast.literal_eval(data)

        if data.get('state') == settings.PROTOCOL_STATE_SEND_FULL_FILE_STRUCTURE:
            # TODO : Only sync required files
            self.filesToSync = ast.literal_eval(data.get('directory_structure'))
            print self.filesToSync
            # TODO : move this to multiple connection syncing
            if len(self.filesToSync):
                self.requestSyncFile(self.filesToSync[0])

        if data.get('state') == settings.PROTOCOL_STATE_SENDING_FILE:
            print 'chunk received'
            self.currentfp.write(data.get('piece'))
            pass

        if data.get('state') == settings.PROTOCOL_STATE_SENDING_FILE_FINISHED:
            print 'File received. Closing pointer to {}.'.format(data.get('file_name'))
            self.currentfp.close()
            del self.filesToSync[0]

            if len(self.filesToSync):
                self.requestSyncFile(self.filesToSync[0])
            pass

    def requestSyncFile(self, file):
        print 'Lets sync file ' + file.get('file_name')

        if not os.path.exists(os.path.dirname(settings.CLIENT_SYNC_FOLDER + '/' + file.get('file_name'))):
            os.makedirs(os.path.dirname(settings.CLIENT_SYNC_FOLDER + '/' + file.get('file_name')))

        self.currentfp = open(settings.CLIENT_SYNC_FOLDER + '/' + file.get('file_name'), 'wb')
        self.sendLine(str({
            'state': settings.PROTOCOL_STATE_GET_FILE,
            'file_name': file.get('file_name')
        }))

    def connectionLost(self, reason):
        print reason
        self.factory.deferred.callback('_')


class FileClientFactory(ClientFactory):
    protocol = FileProtocol

    def __init__(self):
        self.deferred = defer.Deferred()


def main():
    from twisted.internet import reactor

    def closeConnectionSafely(msg=None):
        print msg
        reactor.stop()

    def logError(reason):
        print reason

    factory = FileClientFactory()
    d = factory.deferred
    d.addCallbacks(closeConnectionSafely , logError)
    reactor.connectTCP('127.0.0.1', 9001, factory)
    reactor.run()
    pass

if __name__=="__main__":
    main()