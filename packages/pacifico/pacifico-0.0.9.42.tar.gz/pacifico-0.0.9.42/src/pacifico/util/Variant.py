"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import json
import datetime
from pacifico.util import Enumerations, Dates


class Variant:
    def __init__(self, value, valueType=Enumerations.ValueType.ValueType_Double):
        if not isinstance(value, valueType.getType()):
            if isinstance(value, str):
                if self.getValueType() == Enumerations.ValueType.ValueType_Bool:
                    value = bool(value)
                elif self.getValueType() == Enumerations.ValueType.ValueType_Date:
                    value = Dates.julianToDate(float(value))
                elif self.getValueType() == Enumerations.ValueType.ValueType_DateTime:
                    value = Dates.julianToDateTime(float(value))
                elif self.getValueType() == Enumerations.ValueType.ValueType_Integer:
                    value = int(value)
                elif self.getValueType() == Enumerations.ValueType.ValueType_Double:
                    value = float(value)
                else:
                    raise TypeError("The value and the valueType of a Variant object must be coherent.")
            else:
                raise TypeError("The value and the valueType of a Variant object must be coherent.")
        self.value = value
        self.valueType = valueType

    # valueType
    def _get_valueType(self):
        return self.__valueType
    def _set_valueType(self, value):
        if not isinstance(value, Enumerations.ValueType):
            raise TypeError("The valueType must be set to a class 'Enumerations.ValueType'.")
        self.__valueType = value
    valueType = property(_get_valueType, _set_valueType)

    def getValue(self, asString=False):
        if asString:
            if self.getValueType() == Enumerations.ValueType.ValueType_Bool:
                return str(self.value)
            elif self.getValueType() == Enumerations.ValueType.ValueType_Date:
                return str(Dates.dateToJulian(self.value))
            elif self.getValueType() == Enumerations.ValueType.ValueType_DateTime:
                return str(Dates.dateTimeToJulian(self.value))
            elif self.getValueType() == Enumerations.ValueType.ValueType_Integer or self.getValueType() == Enumerations.ValueType.ValueType_Double:
                return str(self.value)
            else:
                return self.value
        else:
            return self.value

    def getValueType(self):
        return self.valueType

    @staticmethod
    def __serializeAndClean(dictionary):
        delete = []
        for key, value in zip(dictionary.keys(), dictionary.values()):
            if value == None:
                delete.append(key)
            elif isinstance(value, Enumerations.Enum):
                dictionary[key] = value.value
            elif isinstance(value, (datetime.date, datetime.datetime)):
                dictionary[key] = value.isoformat()
            elif isinstance(value, bool):
                dictionary[key] = int(value)
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
            data[newKey] = data.pop(key)
        # Serialize object within the attribute and delete empty attributes
        data = self.__serializeAndClean(data)
        # jsonize data
        dataJson = json.dumps(data)
        return dataJson

    @staticmethod
    def fromJson(jsonString):
        if isinstance(jsonString, str):
            variantDict = json.loads(jsonString)
        else:
            variantDict = jsonString
        if 'valueType' in variantDict.keys():
            valueType = Enumerations.ValueType(variantDict['valueType'])
        elif 'type' in variantDict.keys():
            valueType = Enumerations.ValueType(variantDict['type'])
        else:
            valueType = Enumerations.ValueType.ValueType_String
        value = valueType.fromJson(variantDict['value'])
        variant = Variant(value, valueType)
        return variant

    @staticmethod
    def getEmptyVariant():
        return Variant('', Enumerations.ValueType.ValueType_String)

if __name__ == '__main__':
    x = Variant(datetime.date(2020, 1, 1), Enumerations.ValueType.ValueType_Date)
    y = x.getJson()
    print(y)
    print(Variant.fromJson(y).getValueType())
    z = Variant(True, Enumerations.ValueType.ValueType_Bool)
    valueAsString = z.getValue(asString=True)
    print(valueAsString, type(valueAsString))