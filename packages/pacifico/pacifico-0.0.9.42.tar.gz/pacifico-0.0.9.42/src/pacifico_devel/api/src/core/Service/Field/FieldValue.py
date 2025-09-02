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
from . import Field
from api.src.util import Enumerations, Dates


class FieldValue(Field.Field):
    def __init__(self, datePublication, fixing, ticker, field, dateEffective, dateTenor, value, other=''):
        self.datePublication = datePublication
        self.fixing = fixing
        self.setTicker(ticker)
        self.setField(field)
        self.setDateEffective(dateEffective)
        self.setDateTenor(dateTenor)
        self.value = value
        self.other = other

    # fixing
    def _get_fixing(self):
        return self.__fixing
    def _set_fixing(self, value):
        if not isinstance(value, Enumerations.Fixing):
            raise TypeError("The fixing must be set to a class 'Enumerations.Fixing'.")
        self.__fixing = value
    fixing = property(_get_fixing, _set_fixing)

    # ticker
    def _get_ticker(self):
        return self.__ticker
    def _set_ticker(self, value):
        if not isinstance(value, str):
            raise TypeError("The ticker must be set to a class 'ioIdentificationMnemo.IdentificationMnemo'.")
        self.__ticker = value
    ticker = property(_get_ticker, _set_ticker)

    # field
    def _get_field(self):
        return self.__field
    def _set_field(self, value):
        if not isinstance(value, Enumerations.FieldType):
            raise TypeError("The field must be set to a class 'Enumerations.FieldType'.")
        self.__field = value
    field = property(_get_field, _set_field)

    # dateEffective
    def _get_dateEffective(self):
        return self.__dateEffective
    def _set_dateEffective(self, value):
        if not isinstance(value, datetime.datetime):
            raise TypeError("The dateEffective must be set to a class 'datetime.datetime'.")
        self.__dateEffective = value
    dateEffective = property(_get_dateEffective, _set_dateEffective)

    # value
    def _get_value(self):
        return self.__value
    def _set_value(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("The value must be set to a integer or float.")
        self.__value = value
    value = property(_get_value, _set_value)

    # other
    def _get_other(self):
        return self.__other
    def _set_other(self, value):
        if not isinstance(value, str):
            raise TypeError("The other must be set to a string.")
        self.__other = value
    other = property(_get_other, _set_other)

    def getDatePublication(self):
        return self.datePublication

    def getFixing(self):
        return self.fixing

    def getTicker(self):
        return self.ticker

    def setTicker(self, ticker):
        self.ticker = ticker

    def getField(self):
        return self.field

    def setField(self, field):
        if isinstance(field, Enumerations.FieldType):
            self.field = field
        else:
            self.field = Enumerations.FieldType.fromValueOrString(field)

    def getDateEffective(self):
        return self.dateEffective

    def setDateEffective(self, dateEffective):
        if isinstance(dateEffective, (datetime.datetime, datetime.date)):
            self.dateEffective = dateEffective
        else:
            if dateEffective != '':
                self.dateEffective = Dates.dateTimeFromString(dateEffective)
            else:
                if isinstance(self.getDatePublication(), str):
                    if Dates.isDateTimeFromDateTimeOrDateString(self.getDatePublication()):
                        self.dateEffective = Dates.dateTimeFromString(self.getDatePublication())
                    else:
                        datePublication = Dates.dateFromString(self.getDatePublication())
                        hour, minute, second = Enumerations.Fixing.getTime(self.getFixing())
                        self.dateEffective = Dates.createDateTimeFromValues(datePublication.year, datePublication.month, datePublication.day, hour, minute, second)
                else:
                    hour, minute, second = Enumerations.Fixing.getTime(self.getFixing())
                    self.dateEffective = Dates.createDateTimeFromValues(self.getDatePublication().year, self.getDatePublication().month, self.getDatePublication().day, hour, minute, second)

    def getDateTenor(self):
        return self.dateTenor

    def setDateTenor(self, dateTenor):
        if isinstance(dateTenor, datetime.datetime):
            self.dateTenor = dateTenor
        else:
            if dateTenor != '':
                self.dateTenor = Dates.dateTimeFromString(dateTenor)
            else:
                self.dateTenor = self.getDateEffective()

    def getValue(self):
        return self.value

    def getOther(self):
        return self.other

    def getBase(self):
        for base in self.__class__.__bases__:
            return base.__name__

    @staticmethod
    def __serializeAndClean(dictionary):
        delete = []
        for key, value in zip(dictionary.keys(), dictionary.values()):
            if key in ['fixing', 'datePublication']:
                delete.append(key)
            if value in [[], {}, None, '']:
                delete.append(key)
            elif isinstance(value, list):
                dictionary[key] = [item.getJson(True) for item in value]
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