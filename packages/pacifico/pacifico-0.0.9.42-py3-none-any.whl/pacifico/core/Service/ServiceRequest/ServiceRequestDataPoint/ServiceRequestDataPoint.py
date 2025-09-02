"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import json
from pacifico.core.Service.ServiceRequest import ServiceRequest
from pacifico.core.Service.Field import FieldVersion, FieldTicker, FieldReport
from pacifico.core.Service.Field import FieldDataType, FieldQuality, FieldTimeInterval, Field

class ServiceRequestDataPoint(ServiceRequest.ServiceRequest):
    def __init__(self, instruments=[], timeHorizon=[], dataTypes=[], version=[], quality=[], optional={}):
        self.instruments = instruments # Tickers
        self.timeHorizon = timeHorizon
        self.dataTypes = dataTypes # Calculation Types
        self.version = version # Scenario
        self.quality = quality
        self.optional = optional

    # instruments
    def _get_instruments(self):
        return self.__instruments
    def _set_instruments(self, value):
        if not isinstance(value, list):
            raise TypeError("The instruments must be set to a list.")
        if not all(isinstance(item, (FieldTicker.FieldTicker, FieldReport.FieldReport)) for item in value):
            raise TypeError(
                "The instruments must be set to a list of items of class 'FieldTicker.FieldTicker' or 'FieldReport.FieldReport'.")
        self.__instruments = value
    instruments = property(_get_instruments, _set_instruments)

    # timeHorizon
    def _get_timeHorizon(self):
        return self.__timeHorizon
    def _set_timeHorizon(self, value):
        if not isinstance(value, list):
            raise TypeError("The timeHorizon must be set to a list.")
        if not all(isinstance(item, FieldTimeInterval.FieldTimeInterval) for item in value):
            raise TypeError("The timeHorizon must be set to a list of items of class "
                            "'FieldTimeInterval.FieldTimeInterval'.")
        self.__timeHorizon = value
    timeHorizon = property(_get_timeHorizon, _set_timeHorizon)

    # dataTypes
    def _get_dataTypes(self):
        return self.__dataTypes
    def _set_dataTypes(self, value):
        if not isinstance(value, list):
            raise TypeError("The dataTypes must be set to a list.")
        if not all(isinstance(item, FieldDataType.FieldDataType) for item in value):
            raise TypeError(
                "The dataTypes must be set to a list of items of class 'FieldDataType.FieldDataType'.")
        self.__dataTypes = value
    dataTypes = property(_get_dataTypes, _set_dataTypes)

    # version
    def _get_version(self):
        return self.__version
    def _set_version(self, value):
        if not isinstance(value, list):
            raise TypeError("The version must be set to a list.")
        if not all(isinstance(item, FieldVersion.FieldVersion) for item in value):
            raise TypeError(
                "The version must be set to a list of items of class 'FieldVersion.FieldVersion'.")
        self.__version = value
    version = property(_get_version, _set_version)

    # quality
    def _get_quality(self):
        return self.__quality
    def _set_quality(self, value):
        if not isinstance(value, list):
            raise TypeError("The quality must be set to a list.")
        if not all(isinstance(item, FieldQuality.FieldQuality) for item in value):
            raise TypeError(
                "The quality must be set to a list of items of class 'FieldQuality.FieldQuality'.")
        self.__quality = value
    quality = property(_get_quality, _set_quality)

    # optional
    def _get_optional(self):
        return self.__optional
    def _set_optional(self, value):
        if not isinstance(value, dict):
            raise TypeError("The optional must be set to a dictionary.")
        if not all(isinstance(item, Field.Field) for item in value.values()):
            raise TypeError("The optional must be set to a dictionary of items of class 'Field.Field'.")
        self.__optional = value
    optional = property(_get_optional, _set_optional)

    # Class Methods

    def getInstruments(self):
        return self.instruments

    def getReports(self):
        return self.instruments

    def getTimeHorizon(self):
        return self.timeHorizon

    def getDataTypes(self):
        return self.dataTypes

    def getVersions(self):
        return self.version

    def getQualities(self):
        return self.quality

    def getOptionals(self):
        return self.optional

    def getBase(self):
        for base in self.__class__.__bases__:
            return base.__name__

    @staticmethod
    def __serializeAndClean(dictionary):
        delete = []
        for key, value in zip(dictionary.keys(), dictionary.values()):
            if value == [] or value == {} or value == None:
                delete.append(key)
            elif isinstance(value, list):
                dictionary[key] = [item.getJson() for item in value]
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
