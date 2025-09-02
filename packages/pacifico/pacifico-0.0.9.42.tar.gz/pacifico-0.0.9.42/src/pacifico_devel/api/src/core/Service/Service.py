"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import abc
import requests
import json
import datetime
from .. import Object
from ...util import Enumerations, Dates, AmazonWebServices


class Service(Object.Object):

    def getResponse(self, token):
        if not isinstance(token, str):
            raise TypeError('The token must be set to a string.')
        postData = self.getJson()
        headers = {'x-api-key': token}
        # response = requests.post("http://localhost:8000/", data=postData, headers=headers)
        response = requests.post("https://api.pacificoindices.com/", data=postData, headers=headers)
        return response.text

    def saveResponse(self, fileName, token, awsAccessKey, awsSecretKey, connection):
        try:
            content = self.makeResponse(token, awsAccessKey, awsSecretKey, connection, fileName)
        except Exception as exception:
            exception = str(exception)
            content = json.dumps({"message": "Exception: {}".format(exception), "status": "500 ERROR"})
        AmazonWebServices.AmazonWebServices.writeToBucket(content, fileName, awsAccessKey, awsSecretKey)

    @abc.abstractmethod
    def makeResponse(self, token, awsAccessKey, awsSecretKey, connection, fileName=''):
        pass

    @staticmethod
    def getURL(awsAccessKey, awsSecretKey, awsUrlAction=Enumerations.awsUrlAction.GET):
        fileName = str(Dates.getDateTimeTimestamp(datetime.datetime.now())) + '.txt'
        secondsItLasts = 86400  # 24hrs
        url = AmazonWebServices.AmazonWebServices.getUrl(fileName, secondsItLasts, awsAccessKey, awsSecretKey, awsUrlAction)
        return url, fileName

    @abc.abstractmethod
    def getService(self, token, awsAccessKey, awsSecretKey, connection):
        return self