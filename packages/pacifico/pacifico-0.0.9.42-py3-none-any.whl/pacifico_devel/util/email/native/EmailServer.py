"""Copyright © 2022 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import email
import imaplib
import smtplib
from email.header import decode_header
from email.mime.text import MIMEText

class EmailServer:
    # https://humberto.io/blog/sending-and-receiving-emails-with-python/
    def __init__(self, sendServer, sendPort, receiveServer, receivePort):
        self.sendServer = sendServer
        self.sendPort = sendPort
        self.receiveServer = receiveServer
        self.receivePort = receivePort

    def getSendServer(self):
        return self.sendServer

    def getSendPort(self):
        return self.sendPort

    def getReceiveServer(self):
        return self.receiveServer

    def getReceivePort(self):
        return self.receivePort

    def sendEmail(self, userEmail, userPassword, destinationEmailList, subject, message, html=False):
        # Connect with email provider servers
        smtp_ssl_host = self.getSendServer()  # 'smtp.gmail.com'
        smtp_ssl_port = self.getSendPort()  # 465
        # Use username or email to log in
        username = userEmail  # 'origin@gmail.com'
        password = userPassword  # 'password'
        from_addr = userEmail  # 'origin@gmail.com'
        if not html:
            message = MIMEText(message)  # 'Hello World')
        else:  # https://stackoverflow.com/questions/44322806/sending-email-with-color-formatting-in-python
            message = MIMEText(message, 'html')
        message['subject'] = subject  # 'Hello'
        message['from'] = from_addr
        message['to'] = ', '.join(destinationEmailList)  # ['destiny@gmail.com']
        # We'll connect using SSL
        server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
        server.login(username, password)
        server.sendmail(from_addr, destinationEmailList, message.as_string())
        server.quit()
        print(f'Email with subject "{subject}" from "{userEmail}" to "{", ".join(destinationEmailList)}" was sent correctly!')

    def getInbox(self, userEmail, userPassword, amountOfEmails=None, latest=True, verbose=False):
        emails = []
        EMAIL = userEmail  # 'mymail@mail.com'
        PASSWORD = userPassword  # 'password'
        SERVER = self.getReceiveServer()  # 'imap.gmail.com'
        # Connect to the server and go to its inbox
        mail = imaplib.IMAP4_SSL(SERVER)
        mail.login(EMAIL, PASSWORD)
        # We choose the inbox but you can select others
        mail.select('inbox')
        # We'll search using the ALL criteria to retrieve every message inside the inbox it will return with its status
        # and a list of ids
        status, data = mail.search(None, 'ALL')
        # The list returned is a list of bytes separated by white spaces on this format: [b'1 2 3', b'4 5 6'] so, to
        # separate it first we create an empty list
        mail_ids = []
        # Then we go through the list splitting its blocks of bytes and appending to the mail_ids list
        for block in data:
            # the split function called without parameter transforms the text or bytes into a list using as separator
            # the white spaces:
            # b'1 2 3'.split() => [b'1', b'2', b'3']
            mail_ids += block.split()
        # Now for every id we'll fetch the email
        if latest:  # To get the latest emails first
            mail_ids.reverse()
        if amountOfEmails is not None:  # To retrieve a specific amount of emails
            mail_ids = mail_ids[:amountOfEmails]
        for i in mail_ids:
            # The fetch function fetch the email given its id and format that you want the message to be
            status, data = mail.fetch(i, '(RFC822)')
            # The content data at the '(RFC822)' format comes on a list with a tuple with header, content, and the
            # closing byte b')'
            for response_part in data:
                # So if its a tuple...
                if isinstance(response_part, tuple):
                    # We go for the content at its second element skipping the header at the first and the closing at
                    # the third
                    message = email.message_from_bytes(response_part[1])
                    # With the content we can extract the info about who sent the message and its subject
                    mail_from = message.get('from')
                    mail_to = message.get('to')
                    mail_cc = message.get('cc')
                    mail_datetime = message.get('date')
                    # Mail subject special parsing
                    mail_subject = message.get('subject')
                    result = decode_header(mail_subject)
                    mail_subject_items = []
                    for data, encoding in result:
                        if encoding is not None:
                            data = data.decode(encoding)
                        elif isinstance(data, bytes):
                            data = data.decode('utf-8')
                        mail_subject_items.append(data)
                    mail_subject = ' '.join(mail_subject_items)
                    # Then for the text we have a little more work to do because it can be in plain text or multipart
                    # if its not plain text we need to separate the message from its annexes to get the text
                    if message.is_multipart():
                        mail_content = []
                        # On multipart we have the text message and another things like annex, and html version of the
                        # message, in that case we loop through the email payload
                        for part in message.get_payload():
                            # if part.get_content_type() == 'text/plain':
                            content = (part.get_content_type(), part.get_payload())
                            mail_content.append(content)
                    else:
                        # If the message isn't multipart, just extract it
                        mail_content = message.get_payload()
                    # Let's show its result
                    if verbose:
                        print(f'From: {mail_from}')
                        print(f'To: {mail_to}')
                        print(f'CC: {mail_cc}')
                        print(f'Datetime: {mail_datetime}')
                        print(f'Subject: {mail_subject}')
                        print(f'Content: {mail_content}')
                        print('*' * 100)
                    # Let's return its result
                    emailDict = {'From': mail_from, 'To': mail_to, 'CC': mail_cc, 'Datetime': mail_datetime,
                                 'Subject': mail_subject, 'Content': mail_content}
                    emails.append(emailDict)
        return emails

    def deleteEmail(self, userEmail, userPassword, subject):
        EMAIL = userEmail  # 'mymail@mail.com'
        PASSWORD = userPassword  # 'password'
        SERVER = self.getReceiveServer()  # 'imap.gmail.com'
        # Connect to the server and go to its inbox
        imap = imaplib.IMAP4_SSL(SERVER)
        imap.login(EMAIL, PASSWORD)
        # We choose the inbox but you can select others
        imap.select('inbox')
        # We'll search using the ALL criteria to retrieve every message inside the inbox it will return with its status
        # and a list of ids
        # to get mails by subject
        status, messages = imap.search(None, f'SUBJECT "{subject}"')
        # convert messages to a list of email IDs
        messages = messages[0].split(b' ')
        for mail in messages:
            _, msg = imap.fetch(mail, "(RFC822)")
            # you can delete the for loop for performance if you have a long list of emails
            # because it is only for printing the SUBJECT of target email to delete
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        # if it's a bytes type, decode to str
                        subject = subject.decode()
                    print("Deleting", subject)
            # mark the mail as deleted
            imap.store(mail, "+FLAGS", "\\Deleted")
        # permanently remove mails that are marked as deleted
        # from the selected mailbox (in this case, INBOX)
        imap.expunge()
        # close the mailbox
        imap.close()
        # logout from the account
        imap.logout()

if __name__ == '__main__':
    sendServer = 'bfi.lat'
    sendPort = 465  # 587
    receiveServer = 'mail.bfi.lat'
    receivePort = 110
    server = EmailServer(sendServer, sendPort, receiveServer, receivePort)
    userEmail = 'backoffice@bfi.lat'
    userPassword = 'backoffice2022'
    emails = server.getInbox(userEmail, userPassword, amountOfEmails=100)
    for email in emails:
        print(email['From'])
    destinationEmailList = ['benyin96@gmail.com']
    subject = 'Test email from Python'
    message = 'Hello World!'
    server.sendEmail(userEmail, userPassword, destinationEmailList, subject, message)