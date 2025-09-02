"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import os
from ..aws import S3

class Configuration:
    data = {}

    @staticmethod
    def loadConfiguration(awsAccessKey='', awsSecretKey=''):
        try:
            return Configuration._loadConfiguration(awsAccessKey, awsSecretKey)
        except:
            rootFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            filePath = os.path.join(rootFolder, 'aws_credentials.csv')
            with open(filePath, 'r') as cfgFile:
                stringData = cfgFile.read()
            relevantRow = stringData.split('\n')[1]
            username, password, awsAccessKey, awsSecretKey, link = relevantRow.split(',')
            return Configuration._loadConfiguration(awsAccessKey, awsSecretKey)

    @staticmethod
    def _loadConfiguration(awsAccessKey='', awsSecretKey=''):
        if Configuration.data == {}:
            listOflists = S3.getCSVFromBucketAsListOfLists('cfg.csv', 'bfi-cfg', awsAccessKey, awsSecretKey)
            for list in listOflists:
                key, value = list
                Configuration.data.update({key: value})

def get(key, awsAccessKey='', awsSecretKey=''):
    Configuration.loadConfiguration(awsAccessKey, awsSecretKey)
    if key in Configuration.data.keys():
        return Configuration.data[key]
