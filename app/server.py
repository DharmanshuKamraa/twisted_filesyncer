import ast

from twisted.internet import defer
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver

import settings
import lib

LineReceiver.MAX_LENGTH = 1024*1024*64

class FileSyncProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.num_of_clients += 1
        print 'Connection made from ' + str(self.transport.getPeer())

    def lineReceived(self, data):
        print data
        data = ast.literal_eval(data)

        # TODO : Handle this using state machine
        if data.get('state') == settings.PROTOCOL_STATE_GET_FULL_FILE_STRUCTURE:
            response = {
                'state': settings.PROTOCOL_STATE_SEND_FULL_FILE_STRUCTURE,
                'directory_structure': str(lib.get_full_folder_structure(settings.SYNC_FOLDER))
            }
            self.sendLine(str(response))
            pass

        if data.get('state') == settings.PROTOCOL_STATE_GET_FILE:
            file_name = settings.SYNC_FOLDER + '/' + data.get('file_name')
            f = open(file_name, 'rb')
            # TODO handle file not found error here.
            while True:
                piece = f.read(1024*1024)
                if not piece:
                    self.sendLine(str(
                        {
                            'state': settings.PROTOCOL_STATE_SENDING_FILE_FINISHED,
                            'file_name': file_name
                        })
                    )
                    break

                self.sendLine(str({
                    'state': settings.PROTOCOL_STATE_SENDING_FILE,
                    'file_name': file_name,
                    'piece': str(piece)
                }))
            print "Sending " + file_name + ' completed.'
            f.close()

    def connectionLost(self, reason=None):
        print reason


class FileSyncProtocolFactory(ServerFactory):

    protocol = FileSyncProtocol
    num_of_clients = 0

    def __init__(self):
        self.deferred = defer.Deferred()
        pass

    def fileTransferFinished(self, file_name, client_number):
        pass

    def clientRequestingEndConnection(self):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback()

def main():
    from twisted.internet import reactor
    port = reactor.listenTCP(9001, FileSyncProtocolFactory())
    print 'Started'
    reactor.run()
    pass

if __name__ == '__main__':
    main()