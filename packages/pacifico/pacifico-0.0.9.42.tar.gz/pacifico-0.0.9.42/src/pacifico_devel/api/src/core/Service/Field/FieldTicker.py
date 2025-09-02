"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import datetime
from . import Field
from ....util import Enumerations, Dates
import json

class FieldTicker(Field.Field):
    def __init__(self, mnemo='', family='', group='', market='', country=Enumerations.Country.Country_Unspecified, other=''):
        self.mnemo = mnemo
        self.family = family
        self.group = group
        self.market = market
        self.country = country
        self.other = other

    # mnemo
    def _get_mnemo(self):
        return self.__mnemo
    def _set_mnemo(self, value):
        if not isinstance(value, str):
            raise TypeError("The mnemo must be set to a string.")
        self.__mnemo = value
    mnemo = property(_get_mnemo, _set_mnemo)

    # family
    def _get_family(self):
        return self.__family
    def _set_family(self, value):
        if not isinstance(value, str):
            raise TypeError("The family must be set to a string.")
        self.__family = value
    family = property(_get_family, _set_family)

    # group
    def _get_group(self):
        return self.__group
    def _set_group(self, value):
        if not isinstance(value, str):
            raise TypeError("The group must be set to a string.")
        self.__group = value
    group = property(_get_group, _set_group)

    # market
    def _get_market(self):
        return self.__market
    def _set_market(self, value):
        if not isinstance(value, str):
            raise TypeError("The market must be set to a string.")
        self.__market = value
    market = property(_get_market, _set_market)

    # country
    def _get_country(self):
        return self.__country
    def _set_country(self, value):
        if not isinstance(value, Enumerations.Country):
            raise TypeError("The country must be set to a class 'Enumerations.Country'.")
        self.__country = value
    country = property(_get_country, _set_country)

    # other
    def _get_other(self):
        return self.__other
    def _set_other(self, value):
        if not isinstance(value, str):
            raise TypeError("The other value must be set to a string.")
        self.__other = value
    other = property(_get_other, _set_other)

    # Class Methods

    def getMnemo(self):
        return self.mnemo

    def getFamily(self):
        return self.family

    def getGroup(self):
        return self.group

    def getMarket(self):
        return self.market

    def getCountry(self):
        return self.country

    def getOther(self):
        return self.other

    def getBase(self):
        for base in self.__class__.__bases__:
            return base.__name__

    @staticmethod
    def __serializeAndClean(dictionary):
        delete = []
        for key, value in zip(dictionary.keys(), dictionary.values()):
            if value in [[], {}, None, '']:
                delete.append(key)
            elif isinstance(value, list):
                dictionary[key] = [item.getJson() for item in value]
            elif isinstance(value, Enumerations.Enum):
                dictionary[key] = value.value
            elif isinstance(value, (datetime.date, datetime.datetime)):
                dictionary[key] = Dates.getDateOrDateTimeString(value)
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
            newKey = key.replace('_' + self.__class__.__name__ + '__', '')
            newKey = newKey.replace('_' + self.getBase() + '__', '')
            data[newKey] = data.pop(key)
        # Serialize object within the attribute and delete empty attributes
        data = self.__serializeAndClean(data)
        # jsonize data
        dataJson = json.dumps(data)
        return dataJson