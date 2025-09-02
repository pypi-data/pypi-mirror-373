"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import json
from enum import Enum
import os
import datetime
from . import Dates, Configuration, FTP, Connection


class Fixing(Enum):
    EOD = -1
    F_0000 = 0
    F_0030 = 30
    F_0100 = 100
    F_0130 = 130
    F_0200 = 200
    F_0230 = 230
    F_0300 = 300
    F_0330 = 330
    F_0400 = 400
    F_0430 = 430
    F_0500 = 500
    F_0530 = 530
    F_0600 = 600
    F_0630 = 630
    F_0700 = 700
    F_0730 = 730
    F_0800 = 800
    F_0830 = 830
    F_0900 = 900
    F_0930 = 930
    F_1000 = 1000
    F_1030 = 1030
    F_1100 = 1100
    F_1130 = 1130
    F_1200 = 1200
    F_1230 = 1230
    F_1300 = 1300
    F_1330 = 1330
    F_1400 = 1400
    F_1430 = 1430
    F_1500 = 1500
    F_1530 = 1530
    F_1600 = 1600
    F_1630 = 1630
    F_1700 = 1700
    F_1730 = 1730
    F_1800 = 1800
    F_1830 = 1830
    F_1900 = 1900
    F_1930 = 1930
    F_2000 = 2000
    F_2030 = 2030
    F_2100 = 2100
    F_2130 = 2130
    F_2200 = 2200
    F_2230 = 2230
    F_2300 = 2300
    F_2330 = 2330

    @staticmethod
    def getTime(fixing):
        if not isinstance(fixing, Fixing):
            raise TypeError("The fixing should be set to a class 'Enumerations.Fixing'.")
        if fixing == Fixing.EOD:
            hour = 17
            minute = 0
            second = 0
        else:
            hour = int(fixing.name[2]) * 10 + int(fixing.name[3])
            minute = int(fixing.name[4]) * 10 + int(fixing.name[5])
            second = 0
        return hour, minute, second

    @staticmethod
    def getString(fixing):
        return fixing.name

class Country(Enum):
    Country_RiskFactors = -1
    Country_Unspecified = 0
    Country_Chile = 1
    Country_Colombia = 2
    Country_Peru = 3
    Country_Mexico = 4
    Country_Argentina = 5
    Country_United_States = 6
    Country_Europe = 7
    Country_Japan = 8
    Country_International = 999

    @staticmethod
    def fromString(string):
        if string == 'Chile':
            return Country.Country_Chile
        elif string == 'Colombia':
            return Country.Country_Colombia
        elif string == 'Peru':
            return Country.Country_Peru
        elif string == 'Mexico':
            return Country.Country_Mexico
        elif string == 'Argentina':
            return Country.Country_Argentina
        elif string == 'United States':
            return Country.Country_United_States
        elif string == 'Europe':
            return Country.Country_Europe
        elif string == 'Japan':
            return Country.Country_Japan
        elif string == 'International':
            return Country.Country_International
        elif string == 'Risk Factors' or string == 'RiskFactors':
            return Country.Country_RiskFactors
        else:
            return Country.Country_Unspecified

    @staticmethod
    def getString(country):
        countryString = country.name.split('_')[1:]
        returnString = ''
        for string in countryString:
            returnString += string + ' '
        return returnString[:-1]

class FieldType(Enum):
    Field_Unspecified = 0
    Field_Price = 1
    Field_Yield = 2
    Field_Duration = 3
    Field_Convexity = 4
    Field_Delta = 5
    Field_Gamma = 6
    Field_Vega = 7
    Field_Volatility = 8
    Field_Quote = 9
    Field_CleanPrice = 10
    Field_CleanQuote = 11
    Field_MarketPresence = 12
    Field_DirtyQuote = 13
    Field_Metadata = 14
    Field_DirtyPrice = 15

    @staticmethod
    def getString(fieldType):
        fieldTypeString = fieldType.name.split('_')[1]
        if 'Clean' in fieldTypeString:
            fieldTypeString = fieldTypeString.replace('Clean', 'Clean ')
        elif 'Market' in fieldTypeString:
            fieldTypeString = fieldTypeString.replace('Market', 'Market ')
        elif 'Dirty' in fieldTypeString:
            fieldTypeString = fieldTypeString.replace('Dirty', 'Dirty ')
        return fieldTypeString

    @staticmethod
    def fromString(fieldTypeString):
        fieldTypeString = fieldTypeString.lower()
        if fieldTypeString == 'unspecified':
            return FieldType.Field_Unspecified
        elif fieldTypeString == 'price':
            return FieldType.Field_Price
        elif fieldTypeString == 'yield':
            return FieldType.Field_Yield
        elif fieldTypeString == 'duration':
            return FieldType.Field_Duration
        elif fieldTypeString == 'convexity':
            return FieldType.Field_Convexity
        elif fieldTypeString == 'delta':
            return FieldType.Field_Delta
        elif fieldTypeString == 'gamma':
            return FieldType.Field_Gamma
        elif fieldTypeString == 'vega':
            return FieldType.Field_Vega
        elif fieldTypeString == 'volatility':
            return FieldType.Field_Volatility
        elif fieldTypeString == 'quote':
            return FieldType.Field_Quote
        elif fieldTypeString == 'clean price':
            return FieldType.Field_CleanPrice
        elif fieldTypeString == 'clean quote':
            return FieldType.Field_CleanQuote
        elif fieldTypeString == 'market presence':
            return FieldType.Field_MarketPresence
        elif fieldTypeString == 'dirty quote':
            return FieldType.Field_DirtyQuote
        elif fieldTypeString == 'metadata':
            return FieldType.Field_Metadata
        else:
            return FieldType.Field_Unspecified

    @staticmethod
    def fromValueOrString(valueOrString):
        if isinstance(valueOrString, int):
            return FieldType(valueOrString)
        elif isinstance(valueOrString, str):
            return FieldType.fromString(valueOrString)
        else:
            return None

class Quality(Enum):
    Quality_Unspecified = 0
    Quality_Production = 1
    Quality_Certification = 2
    Quality_Development = 3

    @staticmethod
    def getString(quality):
        qualityString = quality.name.split('_')[1]
        return qualityString

    @staticmethod
    def fromString(qualityString):
        if qualityString == 'Unspecified':
            return Quality.Quality_Unspecified
        elif qualityString == 'Production':
            return Quality.Quality_Production
        elif qualityString == 'Certification':
            return Quality.Quality_Certification
        elif qualityString == 'Development':
            return Quality.Quality_Development
        else:
            return Quality.Quality_Unspecified

class VersionType(Enum):
    Version_Pricing = 1
    Version_Prediction = 2
    Version_Unspecified = 0

    @staticmethod
    def getString(versionType):
        versionTypeString = versionType.name.split('_')[1]
        return versionTypeString

    @staticmethod
    def fromString(versionTypeString):
        if versionTypeString == 'Pricing':
            return VersionType.Version_Pricing
        elif versionTypeString == 'Prediction':
            return VersionType.Version_Prediction
        elif versionTypeString == 'Unspecified':
            return VersionType.Version_Unspecified
        else:
            return VersionType.Version_Unspecified

class ObjectType(Enum):
    Identification = 100
    IdentificationName = 110
    IdentificationFamily = 111
    IdentificationGroup = 112
    IdentificationMarket = 113
    IdentificationMnemo = 114
    IdentificationChileRut = 120
    IdentificationColombiaNit = 121
    IdentificationMexicoRfc = 122
    IdentificationPeruRuc = 123
    IdentificationTicker = 130
    Agent = 200
    AgentUser = 210
    DataPoint = 300
    DataPointComment = 310
    DataPointTicker = 320
    Version = 400
    Authentification = 500
    AuthentificationAWSAPIKey = 510

class PeruRucType(Enum):
    PERU_RUC_TYPE_PERSONA_NATURAL = 10
    PERU_RUC_TYPE_PERSONA_JURIDICA = 20
    PERU_RUC_TYPE_OTROS = 15 # sucesiones indivisas, sociedades conyugales, C FFAA, C FFPP, DPI, Carnet de Extranjeria
    PERU_RUC_TYPE_VALIDO = 16
    PERU_RUC_TYPE_INSCRIPCION_ENTRE_1993_Y_2000 = 17

class UsagePlan(Enum):
    UsagePlan_Client = 0
    UsagePlan_Author = 1
    UsagePlan_Administrator = 2

class Action(Enum):
    Action_Enable = 1
    Action_Disable = -1

class Providers(Enum):
    Provider_BFI = 0
    # Provider_AlphaVantage = 1

class Format(Enum):
    Json = 1
    Dictionary = 2
    DataFrame = 3

    @staticmethod
    def fromString(formatString):
        if formatString == 'json' or formatString == 'JSON':
            return Format.Json
        elif formatString == 'dictionary' or formatString == 'dict':
            return Format.Dictionary
        elif formatString == 'dataFrame' or formatString == 'DataFrame' or formatString == 'df':
            return Format.DataFrame
        else:
            return None

class ValueType(Enum):
    ValueType_Bool = 0
    ValueType_Integer = 1
    ValueType_Double = 2
    ValueType_String = 3
    ValueType_Date = 4
    ValueType_DateTime = 5
    ValueType_Url = 6
    ValueType_File = 7
    ValueType_Browser = 8
    # List versions
    ValueType_List_Bool = 1000
    ValueType_List_Integer = 1001
    ValueType_List_Double = 1002
    ValueType_List_String = 1003
    ValueType_List_Date = 1004
    ValueType_List_DateTime = 1005
    ValueType_List_Url = 1006
    ValueType_List_File = 1007
    ValueType_List_Browser = 1008

    def getString(self):
        return ' '.join(self.name.split('_')[1:])

    @staticmethod
    def fromString(valueTypeString):
        for valueTypeEnum in ValueType:
            if valueTypeString == valueTypeEnum.getString():
                return valueTypeEnum

    def forceType(self, value):
        if not isinstance(value, self.getType()):
            if self == ValueType.ValueType_Bool:
                return bool(value)
            elif self == ValueType.ValueType_Integer:
                if isinstance(value, str):
                    value = float(value)
                return int(value)
            elif self == ValueType.ValueType_Double:
                return float(value)
            elif self == ValueType.ValueType_String:
                return str(value)
            elif self == ValueType.ValueType_Date:
                if isinstance(value, str):
                    return Dates.dateFromString(value)
                return Dates.julianToDate(float(value))
            elif self == ValueType.ValueType_DateTime:
                if isinstance(value, str):
                    return Dates.dateTimeFromString(value)
                return Dates.julianToDateTime(float(value))
            elif self == ValueType.ValueType_Url:
                return str(value)
            elif self == ValueType.ValueType_File:
                return str(value)
            elif self == ValueType.ValueType_Browser:
                return str(value)
            elif 'list' in self.getString().lower():
                if isinstance(value, str):
                    if '[' in value:
                        value = json.loads(value)
                    else:
                        value = value.split(',')
                newValue = []
                for listValue in value:
                    innerValueTypeString = self.getString().replace('List', '').strip()
                    innerType = ValueType.fromString(innerValueTypeString)
                    newListValue = innerType.forceType(listValue)
                    newValue.append(newListValue)
                return newValue
            else:
                return None
        else:
            return value

    def fromDB(self, value):
        if self == ValueType.ValueType_Bool:
            if isinstance(value, (int, float)):
                return bool(int(value))
            if isinstance(value, str):
                if value.isnumeric():
                    return bool(int(value))
                else:
                    if value.lower() in ['false', 'f']:
                        return False
                    else:
                        return True
        elif self == ValueType.ValueType_Integer:
            return int(value)
        elif self == ValueType.ValueType_Double:
            return float(value)
        elif self == ValueType.ValueType_String:
            return str(value)
        elif self == ValueType.ValueType_Date:
            return Dates.getDateString(Dates.julianToDate(float(value)))
        elif self == ValueType.ValueType_DateTime:
            return Dates.getDateTimeString(Dates.julianToDateTime(float(value)))
        elif self == ValueType.ValueType_Url:
            return str(value)
        elif self == ValueType.ValueType_File:
            return str(value)
        elif self == ValueType.ValueType_Browser:
            return str(value)
        elif 'list' in self.getString().lower():
            return value
        else:
            return None

    def getJson(self, value):
        if self == ValueType.ValueType_Bool:
            return bool(value)
        elif self == ValueType.ValueType_Integer:
            return int(value)
        elif self == ValueType.ValueType_Double:
            return float(value)
        elif self == ValueType.ValueType_String:
            return str(value)
        elif self == ValueType.ValueType_Date:
            return Dates.getDateString(Dates.julianToDate(float(value)))
        elif self == ValueType.ValueType_DateTime:
            return Dates.getDateTimeString(Dates.julianToDateTime(float(value)))
        elif self == ValueType.ValueType_Url:
            return str(value)
        elif self == ValueType.ValueType_File:
            return str(value)
        elif self == ValueType.ValueType_Browser:
            return str(value)
        elif 'list' in self.getString().lower():
            return json.dumps(value)
        else:
            return None

    def getType(self):
        if self == ValueType.ValueType_Bool:
            return bool
        elif self == ValueType.ValueType_Integer:
            return int
        elif self == ValueType.ValueType_Double:
            return float
        elif self == ValueType.ValueType_String:
            return str
        elif self == ValueType.ValueType_Date:
            return datetime.date
        elif self == ValueType.ValueType_DateTime:
            return datetime.datetime
        elif self == ValueType.ValueType_Url:
            return str
        elif self == ValueType.ValueType_File:
            return str
        elif self == ValueType.ValueType_Browser:
            return str
        elif 'list' in self.getString().lower():
            return type([])
        else:
            return type(None)

    def fromJson(self, value):
        if self == ValueType.ValueType_Bool:
            return bool(value)
        elif self == ValueType.ValueType_Integer:
            return int(value)
        elif self == ValueType.ValueType_Double:
            return float(value)
        elif self == ValueType.ValueType_String:
            return str(value)
        elif self == ValueType.ValueType_Date:
            return datetime.date.fromisoformat(value)
        elif self == ValueType.ValueType_DateTime:
            return datetime.datetime.fromisoformat(value)
        elif self == ValueType.ValueType_Url:
            return str(value)
        elif self == ValueType.ValueType_File:
            return str(value)
        elif self == ValueType.ValueType_Browser:
            return str(value)
        elif 'list' in self.getString().lower():
            return json.loads(value)
        else:
            return None

class Protocol(Enum):
    Direct = 0
    FTP = 1
    S3 = 2

    def getService(self, service, host='', user='', password='', port='', filepath='', tmp=False):
        if self == Protocol.Direct:
            return service
        elif self == Protocol.FTP:
            from api.src.core.Service.ServiceFTP import ServiceFTP
            FTP.uploadFileFromString(service.getJson(), host, user, password, port, filepath)
            return ServiceFTP.ServiceFTP(host, user, password, port, filepath)
        elif self == Protocol.S3:
            from api.src.core.Service.ServiceS3 import ServiceS3
            connection = Connection.Connection.connect()
            fileName = str(Dates.getDateTimeTimestamp(datetime.datetime.now())) + '.txt'
            filepath = '1D/{}'.format(fileName)
            if tmp:
                fileName = os.path.join('/tmp', fileName)
            awsAccessKey = Configuration.Configuration.get('AWS_ACCESS_KEY', connection)
            awsSecretKey = Configuration.Configuration.get('AWS_SECRET_KEY', connection)
            from api.src.util import AmazonWebServices
            AmazonWebServices.AmazonWebServices.writeToBucket(service.getJson(), fileName, awsAccessKey, awsSecretKey, bucketFilename=filepath)
            return ServiceS3.ServiceS3(filepath)

class awsUrlAction(Enum):
    GET = 0
    PUT = 1

if __name__ == '__main__':
    list = 'all'
    x = ValueType.ValueType_List_String
    y = ValueType.getString(x)
    z = ValueType.fromString(y)
    print(x)
    print(y)
    print(z)
    print(x.forceType(list))
