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
import datetime
from ..cfg import Configuration
from .. import Dates

def getConnection(host='', user='', password='', port=22):
    try:
        cnopts = pysftp.CnOpts()
    except:
        cnopts = pysftp.CnOpts(knownhosts='known_hosts')
    cnopts.hostkeys = None
    if host == '':
        host = Configuration.get('BFI_FTP_HOST')
    if user == '':
        user = Configuration.get('BFI_FTP_USER')
    if password == '':
        password = Configuration.get('BFI_FTP_PASSWORD')
    try:
        sftp = pysftp.Connection(host, username=user, password=password, cnopts=cnopts, port=port)
        return sftp
    except Exception as e:
        return 'Credentials (host, user, password, port, filepath) not valid. (Exception: {})'.format(e)

def downloadFile(filepath, host='', user='', password='', port=22, tmp=False):
    if filepath[0] == '/':
        filepath = filepath[1:]
    filename = filepath.split('/')[-1]
    if tmp:
        filename = os.path.join('/tmp', filename)
    sftp = getConnection(host, user, password, port)
    if sftp.isfile(filepath):
        sftp.get(filepath, filename)
    else:
        return "File doesn't exist."
    sftp.close()

def getFileAsString(filepath, host='', user='', password='', port=22, tmp=False):
    if filepath[0] == '/':
        filepath = filepath[1:]
    filename = filepath.split('/')[-1]
    downloadFile(filepath, host, user, password, port, tmp)
    try:
        file = open(filename, "r").read()
    except:
        file = open(filename, "r", encoding="utf8").read()
    os.remove(filename)
    return file

def getCSVFileAsPandas(filepath, separator=',', decimal='.', header="infer", host='', user='', password='', port=22, tmp=False):
    if filepath[0] == '/':
        filepath = filepath[1:]
    filename = filepath.split('/')[-1]
    if tmp:
        filename = os.path.join('/tmp', filename)
    sftp = getConnection(host, user, password, port)
    if sftp.isfile(filepath):
        sftp.get(filepath, filename)
    else:
        return "File doesn't exist."
    sftp.close()
    file = pandas.read_csv(filename, sep=separator, index_col=False, decimal=decimal, header=header)
    os.remove(filename)
    return file

def getExcelFileAsPandas(filepath, host='', user='', password='', port=22, tmp=False):
    if filepath[0] == '/':
        filepath = filepath[1:]
    filename = filepath.split('/')[-1]
    if tmp:
        filename = os.path.join('/tmp', filename)
    sftp = getConnection(host, user, password, port)
    if sftp.isfile(filepath):
        sftp.get(filepath, filename)
    else:
        return "File doesn't exist."
    sftp.close()
    file = pandas.read_excel(filename)
    os.remove(filename)
    return file

def uploadPandasAsCSV(dataFrame, filepath, host='', user='', password='', port=22, tmp=False, header=True):
    if filepath[0] == '/':
        filepath = filepath[1:]
    filename = filepath.split('/')[-1]
    if tmp:
        filename = os.path.join('/tmp', filename)
    dataFrame.to_csv(filename, index=False, header=header)
    sftp = getConnection(host, user, password, port)
    sftp.put(filename, filepath)
    sftp.close()
    os.remove(filename)

def uploadFileFromString(stringFile, filepath, host='', user='', password='', port=22, tmp=False):
    if filepath[0] == '/':
        filepath = filepath[1:]
    filename = filepath.split('/')[-1]
    if tmp:
        filename = os.path.join('/tmp', filename)
    with open(filename, 'w', encoding="utf-8") as outFile:
        outFile.write(stringFile)
    sftp = getConnection(host, user, password, port)
    sftp.put(filename, filepath)
    sftp.close()
    os.remove(filename)

def uploadFile(localFilepath, remoteFilepath, host='', user='', password='', port=22, removeFile=False):
    if remoteFilepath[0] == '/':
        remoteFilepath = remoteFilepath[1:]
    sftp = getConnection(host, user, password, port)
    sftp.put(localFilepath, remoteFilepath)
    sftp.close()
    if removeFile:
        os.remove(localFilepath)

def getListOfFilesInDir(dirpath, host='', user='', password='', port=22):
    if dirpath[0] == '/':
        dirpath = dirpath[1:]
    sftp = getConnection(host, user, password, port)
    return [filename for filename in sftp.listdir(dirpath)]

def deleteFile(filepath, host='', user='', password='', port=22):
    if filepath[0] == '/':
        filepath = filepath[1:]
    sftp = getConnection(host, user, password, port)
    sftp.remove(filepath)
    sftp.close()

def deleteMultipleFiles(directoryPath, filenames, host='', user='', password='', port=22):
    if directoryPath[0] == '/':
        directoryPath = directoryPath[1:]
    sftp = getConnection(host, user, password, port)
    for filename in filenames:
        filepath = '{}/{}'.format(directoryPath, filename)
        try:
            sftp.remove(filepath)
        except Exception as e:
            print(e)
    sftp.close()

def cleanDirectory(directoryPath, host='', user='', password='', port=22):
    if directoryPath[0] == '/':
        directoryPath = directoryPath[1:]
    sftp = getConnection(host, user, password, port)
    try:
        filesInRemoteArtifacts = sftp.listdir(directoryPath)
        for file in filesInRemoteArtifacts:
            filePath = '{}/{}'.format(directoryPath, file)
            sftp.remove(filePath)
        sftp.close()
    except:
        print("The directory is empty!")

def cleanTMPDirectory(retentionPeriod=2):
    host = ''
    user = ''
    password = ''
    port = 22
    directoryPath = 'backup/tmp'
    sftp = getConnection(host, user, password, port)
    try:
        filesInRemoteArtifacts = sftp.listdir(directoryPath)
        for file in filesInRemoteArtifacts:
            dateFile = Dates.getDateTimeFromFilenameTimestamp(file)
            if (datetime.datetime.now() - dateFile).days > retentionPeriod:
                filePath = '{}/{}'.format(directoryPath, file)
                sftp.remove(filePath)
        sftp.close()
    except:
        print("The tmp directory is empty!")


if __name__ == '__main__':
    # file = uploadFileFromString('Hey,Ho', 'pacifico/unavailableTEST.csv')
    # print(file)
    #import datetime
    #today = datetime.datetime.now()
    #file = file.append({'Ticker': 'AAPL', 'Date': today, 'Author': 'Benjamin2'}, ignore_index=True)
    #uploadPandasAsCSV(file, 'ec2-54-203-94-208.us-west-2.compute.amazonaws.com', 'bcs', 'bolsa2020', 22, 'pacifico/unavailable.csv')
    ftpDir = 'backup/tmp'
    cleanDirectory(ftpDir)