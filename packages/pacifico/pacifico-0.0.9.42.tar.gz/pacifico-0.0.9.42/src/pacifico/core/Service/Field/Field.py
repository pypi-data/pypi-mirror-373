"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import json, datetime
from pacifico.util import Enumerations


class Field:
    @staticmethod
    def __serializeAndClean(dictionary):
        delete = []
        # Serialize complex objects
        for key, value in zip(dictionary.keys(), dictionary.values()):
            if value in ['', Enumerations.Country.Country_Unspecified]:
                delete.append(key)
            elif isinstance(value, Enumerations.Enum):
                dictionary[key] = value.value
            elif isinstance(value, (datetime.date, datetime.datetime)):
                dictionary[key] = value.isoformat()
        # Delete empty attributes
        for key in delete:
            del dictionary[key]
        return dictionary

    def getJson(self, pythonDict=False):
        # Get all attributes as a dictionary
        data = self.__dict__.copy()
        # Delete object private prefix from attribute names
        oldKeys = list(data.keys())
        for key in oldKeys:
            data[key.replace('_' + self.__class__.__name__ + '__', '')] = data.pop(key)
        # Serialize and clean dictionary
        data = self.__serializeAndClean(data)
        # jsonize data or keep as a Python dictionary
        if pythonDict:
            return data
        else:
            return json.dumps(data)
