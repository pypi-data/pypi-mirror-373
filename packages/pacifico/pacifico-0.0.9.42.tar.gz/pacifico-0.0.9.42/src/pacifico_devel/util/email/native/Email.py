"""Copyright © 2022 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

from ..native import EmailServer
from ...cfg import Configuration

class Email:
    def __init__(self, userEmail, userPassword, sendServer=Configuration.get('BFI_EMAIL_SEND_HOST'),
                 sendPort=Configuration.get('BFI_EMAIL_SEND_PORT'),
                 receiveServer=Configuration.get('BFI_EMAIL_RECIEVE_HOST'),
                 receivePort=Configuration.get('BFI_EMAIL_RECIEVE_PORT')):
        self.userEmail = userEmail
        self.userPassword = userPassword
        self.emailServer = EmailServer.EmailServer(sendServer, sendPort, receiveServer, receivePort)

    def getUserEmail(self):
        return self.userEmail

    def getUserPassword(self):
        return self.userPassword

    def getEmailServer(self):
        return self.emailServer

    def sendEmail(self, destinationEmailList, subject, message, signature=None):
        self.getEmailServer().sendEmail(self.getUserEmail(), self.getUserPassword(), destinationEmailList, subject, message, signature)

    def getInbox(self, amountOfEmails=None, latest=True, verbose=False):
        return self.getEmailServer().getInbox(self.getUserEmail(), self.getUserPassword(), amountOfEmails, latest, verbose)

    def deleteEmail(self, subject):
        self.getEmailServer().deleteEmail(self.getUserEmail(), self.getUserPassword(), subject)
