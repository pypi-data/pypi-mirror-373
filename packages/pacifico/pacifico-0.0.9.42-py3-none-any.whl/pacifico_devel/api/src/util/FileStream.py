"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

def getValue(value):
    value = str(value)
    __saveFile(value)

def __saveFile(value):
    if value[:3].lower() == 'ec2':
        __saveFileEC2(value)
    elif value[:4].lower() == 'sftp':
        __saveFileSFTP(value)
    elif value[:4].lower() == 'http':
        __saveFileHTTPS(value)
    else:
        __saveFileBOX(value)


def __saveFileEC2(value):
    pass

def __saveFileSFTP(value):
    pass

def __saveFileHTTPS(value):
    if value[:5].lower() == 'https':
        pass

def __saveFileBOX(value):
    pass