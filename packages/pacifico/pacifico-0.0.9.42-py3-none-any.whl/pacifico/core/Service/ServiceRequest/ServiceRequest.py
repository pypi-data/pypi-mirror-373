"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import datetime
import json
import abc
from pacifico.core.Service import Service

class ServiceRequest(Service.Service):

    @abc.abstractmethod
    def getJson(self):
        pass

    @staticmethod
    def fromJson(json):
        pass

    @staticmethod
    def __serializeAndClean(dictionary):
        delete = []
        for key, value in zip(dictionary.keys(), dictionary.values()):
            if value == [] or value == {} or value == None:
                delete.append(key)
            elif isinstance(value, (datetime.date, datetime.datetime)):
                dictionary[key] = value.isoformat()
            elif isinstance(value, dict):
                dictionary[key] = ServiceRequest.__serializeAndClean(value)
            elif isinstance(value, list):
                try:
                    dictionary[key] = [item.getJson() for item in value]
                except:
                    dictionary[key] = json.dumps(value)
            else:
                dictionary[key] = value
        for key in delete:
            del dictionary[key]
        return dictionary

    def getJson(self):
        # Get all attributes as a dictionary
        data = self.__dict__.copy()
        # Delete object private prefix from attribute names
        oldKeys = list(data.keys())
        for key in oldKeys:
            newKey = key.replace('_' + self.getClassName() + '__', '')
            newKey = newKey.replace('_' + self.getBase() + '__', '')
            data[newKey] = data.pop(key)
        # Serialize object within the attribute and delete empty attributes
        data = self.__serializeAndClean(data)
        # jsonize data
        dataJson = json.dumps(data)
        return dataJson

    def getClassName(self):
        return self.__class__.__name__

    def getBase(self):
        for base in self.__class__.__bases__:
            return base.__name__