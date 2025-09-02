"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import pysftp
import os
import pandas

def getConnection(host, user, password, port):
    try:
        cnopts = pysftp.CnOpts()
    except:
        cnopts = pysftp.CnOpts(knownhosts='known_hosts')
    cnopts.hostkeys = None
    try:
        sftp = pysftp.Connection(host, username=user, password=password, cnopts=cnopts, port=port)
        return sftp
    except Exception as e:
        return 'Credentials (host, user, password, port, filepath) not valid. (Exception: {})'.format(e)

def getFile(host, user, password, port, filepath):
    if filepath[0] == '/':
        filepath = filepath[1:]
    sftp = getConnection(host, user, password, port)
    if sftp.isfile(filepath):
        sftp.get(filepath)
    else:
        return "File doesn't exist."
    sftp.close()

def getFileAsString(host, user, password, port, filepath):
    if filepath[0] == '/':
        filepath = filepath[1:]
    filename = filepath.split('/')[-1]
    sftp = getConnection(host, user, password, port)
    if sftp.isfile(filepath):
        sftp.get(filepath)
    else:
        return "File doesn't exist."
    sftp.close()
    file = open(filename, "r").read()
    os.remove(filename)
    return file

def getCSVFileAsPandas(host, user, password, port, filepath):
    if filepath[0] == '/':
        filepath = filepath[1:]
    filename = filepath.split('/')[-1]
    sftp = getConnection(host, user, password, port)
    if sftp.isfile(filepath):
        sftp.get(filepath)
    else:
        return "File doesn't exist."
    sftp.close()
    file = pandas.read_csv(filename)
    os.remove(filename)
    return file

def uploadPandasAsCSV(dataFrame, host, user, password, port, filepath):
    if filepath[0] == '/':
        filepath = filepath[1:]
    filename = filepath.split('/')[-1]
    dataFrame.to_csv(filename, index=False)
    sftp = getConnection(host, user, password, port)
    sftp.put(filename, filepath)
    sftp.close()
    os.remove(filename)

def uploadFileFromString(stringFile, host, user, password, port, filepath):
    if filepath[0] == '/':
        filepath = filepath[1:]
    filename = filepath.split('/')[-1]
    with open(filename, 'w') as outFile:
        outFile.write(stringFile)
    sftp = getConnection(host, user, password, port)
    sftp.put(filename, filepath)
    sftp.close()
    os.remove(filename)

if __name__ == '__main__':
    file = uploadFileFromString('Hey,Ho', 'ec2-54-203-94-208.us-west-2.compute.amazonaws.com', 'bcs', 'bolsa2020', 22, 'pacifico/unavailableTEST.csv')
    print(file)
    #import datetime
    #today = datetime.datetime.now()
    #file = file.append({'Ticker': 'AAPL', 'Date': today, 'Author': 'Benjamin2'}, ignore_index=True)
    #uploadPandasAsCSV(file, 'ec2-54-203-94-208.us-west-2.compute.amazonaws.com', 'bcs', 'bolsa2020', 22, 'pacifico/unavailable.csv')
