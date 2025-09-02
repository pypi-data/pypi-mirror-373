"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

from .util.cfg import Configuration
from .util.aws import S3, SQS, SNS, AppRunner
from .util import Dates
from .api.src.util import Enumerations as pacificoEnumerations
from .util.aws import Enumerations as awsEnumerations
import datetime
import json
import abc
import base64
import sys
import os


class Message:
    """This is the Message class. It's used for formatting and transmitting information received from either the API
    Gateway or the internal SNS messaging system; the received data is then transmitted, based on the service request
    of the incoming message, to the corresponding lambda function."""
    def __init__(self, service='', payload='', task='', arguments=[], author='', filenameInput='', filenameOutput='', difficulty=awsEnumerations.Difficulty.Difficulty_Standard, waitForCompletion=awsEnumerations.WaitForCompletion.Wait):
        self.service = service.lower()
        self.task = task
        self.arguments = arguments
        self.author = author
        self.difficulty = difficulty
        self.waitForCompletion = waitForCompletion
        self.origin = ''
        self.length = ''
        dateNow = Message.__getDateNow()
        self.__setPayload(payload, dateNow, filenameInput)
        self.__setPresignedUrl(dateNow, filenameOutput)

    def getService(self):
        """This function returns the service attribute of the Message object. """
        return self.service

    def getPresignedUrl(self):
        """This function returns the destination presigned url for the output of the request (created upon object
        creation). """
        return self.presignedUrl

    def getTask(self):
        """This function returns the task attribute of the Message object. """
        return self.task

    def getArguments(self):
        """This function returns the arguments (list) attribute of the Message object. """
        return self.arguments

    def getFilenameInput(self):
        """This function returns the filenameInput attribute of the Message object, which is the name of the file in the S3 bucket that hold the message input. """
        return self.filenameInput

    def getFilenameOutput(self):
        """This function returns the filenameOutput attribute of the Message object, which is the name of the file in the S3 bucket that hold the message output. """
        return self.filenameOutput

    def getAuthor(self):
        """This function returns the author attribute of the Message object. """
        return self.author

    def getDifficulty(self):
        """This function returns the difficulty attribute of the Message object. """
        return self.difficulty

    def getWaitForCompletion(self):
        """This function returns the waitForCompletion attribute of the Message object. """
        return self.waitForCompletion

    def getOrigin(self):
        return self.origin

    def getLength(self):
        return self.length

    def __setPresignedUrl(self, dateNow, filenameOutput):
        """This function sets the filenameOutput and the presignedUrl attributes of the Message object, the latter
        is generated from the first one. """
        if filenameOutput == '':
            self.filenameOutput = 'output_' + self.__getFileName(dateNow)
            awsAccessKey = Configuration.get('AWS_ACCESS_KEY')
            awsSecretKey = Configuration.get('AWS_SECRET_KEY')
            self.presignedUrl = S3.getUrl(self.filenameOutput, awsAccessKey=awsAccessKey, awsSecretKey=awsSecretKey)
        else:
            self.filenameOutput = filenameOutput

    @staticmethod
    def __getDateNow():
        return datetime.datetime.now()

    @staticmethod
    def __getFileName(dateNow):
        """This function creates a filename based on the current time (timestamp)."""
        return dateNow.strftime("%d.%m.%Y-%H.%M.%S.%f") + '.txt'

    @staticmethod
    def __isFilename(string):
        if isinstance(string, str):
            if string[-4:] == '.txt':
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def __uploadPayloadToS3(payload, dateNow):
        awsAccessKey = Configuration.get('AWS_ACCESS_KEY')
        awsSecretKey = Configuration.get('AWS_SECRET_KEY')
        if not isinstance(payload, str):
            payload = json.dumps(payload)
        filenameInputLocal = Message.__getFileName(dateNow)
        filenameInput = 'tmp/input_' + filenameInputLocal
        # filenameInputLocal = '/' + filenameInput
        S3.writeToBucket(payload, filenameInputLocal, 'bfi-media', bucketFilename=filenameInput, awsAccessKey=awsAccessKey, awsSecretKey=awsSecretKey)
        return filenameInput

    def __setPayload(self, payload, dateNow, filenameInput):
        """This function uploads the payload to the 'bfi-media' bucket and sets it's filename as the filenameInput
        attribute of the Message object. """
        if not isinstance(payload, str):
            payload = json.dumps(payload)
        if filenameInput == '':
            if payload == '' or payload == '{}' or payload == {}:
                self.filenameInput = ''
            else:
                self.filenameInput = Message.__uploadPayloadToS3(payload, dateNow)
        else:
            self.filenameInput = filenameInput

    def __isPayload(self):
        """This function returns the boolean of whether there is a payload."""
        return self.filenameInput != ''

    @staticmethod
    def create(event):
        """This function creates a Message object base on the source of the incoming message."""
        if isinstance(event, str):
            event = json.loads(event)
        if 'Records' in event.keys():
            return Message.__fromSNS(event)
        else:
            return Message.__fromGateway(event)

    @staticmethod
    def __checkAndParseContentType(event):
        if isinstance(event, str):
            event = json.loads(event)
        if 'params' in event.keys() and 'body' in event.keys():
            if 'header' in event['params'].keys():
                contentKeys = [key for key in event['params']['header'].keys() if 'content-type' in key.lower()]
                if len(contentKeys) > 0:
                    contentKey = contentKeys[0]
                    if event['params']['header'][contentKey] == 'application/xml':
                        encodedData = event['body']
                        data = {'bfi': base64.b64decode(encodedData).decode("utf-8")}
                    elif event['params']['header'][contentKey] == 'application/json':
                        encodedData = event['body']
                        data = {'pacifico': base64.b64decode(encodedData).decode("utf-8")}
                    else:
                        data = event
                else:
                    data = event
        else:
            data = event
        return data

    @staticmethod
    def __fromGateway(input):
        """This function formats an API Gateway message into an acceptable JSON input message."""
        jsonDict = Message.__checkAndParseContentType(input)  # Formats into a json or dict {bfi: postData}
        message = Message.__fromJson(jsonDict)
        if message.getService() == 'pacifico':
            message.task = 'application'
            return message
        return Message.__fromGatewayBFI(message, jsonDict)

    @staticmethod
    def __fromGatewayBFI(message, jsonDict):
        message.service = 'bfi'
        if message.__isPayload():
            message.task = 'job'
        else:
            message.task = 'tickers'
        if message.service in jsonDict.keys():
            payload = jsonDict[message.service]
        else:
            payload = jsonDict
        if isinstance(payload, str):
            if payload == '' or payload == '{}':
                message.difficulty = awsEnumerations.Difficulty.Difficulty_Low
            elif 'bootstrapping' in payload[:100].lower():
                message.difficulty = awsEnumerations.Difficulty.Difficulty_High
                message.waitForCompletion = awsEnumerations.WaitForCompletion.StartStop
            elif 'JobApplication' in payload:
                message.difficulty = awsEnumerations.Difficulty.Difficulty_Application
            else:
                message.difficulty = awsEnumerations.Difficulty.Difficulty_Standard
        elif payload == {}:
            message.difficulty = awsEnumerations.Difficulty.Difficulty_Low
        else:
            message.difficulty = awsEnumerations.Difficulty.Difficulty_Standard
        return message

    @staticmethod
    def __fromSNS(input):
        """This function formats an SNS message into an acceptable JSON input message."""
        jsonString = input['Records'][0]['body']  # Formats into a json {bfi: postData}
        return Message.__fromJson(jsonString)

    @staticmethod
    def __fromJson(jsonString):
        """This function creates a Message object from the JSON input message."""
        # {service: message, extra: extraValue}
        if isinstance(jsonString, str):
            data = json.loads(jsonString)
        else:
            data = jsonString
        if 'pacifico' in data.keys():
            service = 'pacifico'
        else:
            service = 'bfi'
        if service in data.keys():
            payload = data[service]
        else:
            payload = data
        if Message.__isFilename(payload):
            message = Message(service=service, filenameInput=payload)
        else:
            message = Message(service=service, payload=payload)
        if 'task' in data.keys():
            message.task = data['task']
        if 'author' in data.keys():
            message.author = data['author']
        if 'arguments' in data.keys():
            message.arguments = data['arguments']
        if 'difficulty' in data.keys():
            message.difficulty = awsEnumerations.Difficulty(data['difficulty'])
        if 'waitForCompletion' in data.keys():
            message.waitForCompletion = awsEnumerations.WaitForCompletion.fromValue(data['waitForCompletion'])
        if 'origin' in data.keys():
            message.origin = data['origin']
        if 'length' in data.keys():
            message.length = data['length']
        return message

    @staticmethod
    def __serializeAndClean(dictionary):
        delete = []
        for key, value in zip(dictionary.keys(), dictionary.values()):
            if value == None:
                delete.append(key)
            elif isinstance(value, (pacificoEnumerations.Enum, awsEnumerations.Enum)):
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

    def getJson(self, dropPresignedUrl=True):
        """This function returns the JSON format representation of the Message object."""
        data = self.__dict__.copy()
        if 'presignedUrl' in data.keys():
            if dropPresignedUrl:
                del data['presignedUrl']
        data = self.__serializeAndClean(data)
        dataJson = json.dumps(data)
        return dataJson

    def __getQueueName(self):
        """This function returns the SQS queue name base on the service of the Message object."""
        return 'gatekeeper-computer_' + self.service

    def __getAppRunnerName(self):
        """This function returns the AppRunner name base on the service of the Message object."""
        return 'ComputerApplication'

    def send(self, log=True):
        """This function sends the Message object to the corresponding SQS queue based on the service associated with
        it. """
        awsAccessKey = Configuration.get('AWS_ACCESS_KEY')
        awsSecretKey = Configuration.get('AWS_SECRET_KEY')
        if self.task == 'application':
            AppRunner.publish(self.__getAppRunnerName(), self.getJson())
        else:
            SQS.publish(self.__getQueueName(), self.getJson(), awsAccessKey=awsAccessKey, awsSecretKey=awsSecretKey)
        if log:
            self.log()

    def log(self):
        if self.getService() == 'pacifico':
            Message.logToMessenger(self.getLength(), self.getOrigin())

    def publishSelf(self):
        return Message.publish(service=self.getService(), task=self.getTask(), arguments=self.getArguments(), author=self.getAuthor(), difficulty=self.getDifficulty(), waitForCompletion=self.getWaitForCompletion())

    @staticmethod
    def publish(service='pacifico', payload='', task='', arguments=[], author='', difficulty=awsEnumerations.Difficulty.Difficulty_Standard, waitForCompletion=awsEnumerations.WaitForCompletion.Wait, dumped=True, origin=''):
        """This function publishes the Message object to the bot-gatekeeper.fifo SNS topic."""
        payloadLength = len(payload)
        payloadSize = sys.getsizeof(json.dumps(payload))
        if int(payloadSize) > 250000:  # maximum message size of 256000 bytes
            dateNow = Message.__getDateNow()
            payload = Message.__uploadPayloadToS3(payload, dateNow)  # filenameInput is the payload now
        delete = []
        topicARN = 'arn:aws:sns:us-west-2:947040342882:bot-gatekeeper.fifo'
        data = {service: payload, 'task': task, 'arguments': arguments, 'author': author, 'difficulty': difficulty.value, 'waitForCompletion': waitForCompletion.getValue(), 'origin': origin, 'length': payloadLength}
        for key in data.keys():
            if key != service:
                if data[key] == '' or data[key] == []:
                    delete.append(key)
        for key in delete:
            del data[key]
        if dumped:
            data = json.dumps(data)
        awsAccessKey = Configuration.get('AWS_ACCESS_KEY')
        awsSecretKey = Configuration.get('AWS_SECRET_KEY')
        return SNS.publish(data, topicARN, awsAccessKey=awsAccessKey, awsSecretKey=awsSecretKey)

    @staticmethod
    def logToMessenger(message, origin, arn=''):
        messageJson = json.dumps({'origin': str(origin), 'arn': arn, 'message': str(message)})
        queueName = 'messenger'
        awsAccessKey = Configuration.get('AWS_ACCESS_KEY')
        awsSecretKey = Configuration.get('AWS_SECRET_KEY')
        SQS.publish(queueName, messageJson, awsAccessKey=awsAccessKey, awsSecretKey=awsSecretKey)

    # Computer Methods
    @staticmethod
    def fromSQS(event):
        """This function builds a Message object from it's JSON version (string) incoming directly from an SQS queue
        event. """
        body = event['Records'][0]['body']
        return Message.fromJson(body)

    @staticmethod
    def fromJson(jsonString):
        """This function builds a Message object from it's JSON version (string)."""
        try:
            data = json.loads(jsonString)
        except:
            data = jsonString
        message = Message(service=data['service'], task=data['task'], arguments=data['arguments'], author=data['author'], filenameInput=data['filenameInput'], filenameOutput=data['filenameOutput'], difficulty=awsEnumerations.Difficulty(data['difficulty']), waitForCompletion=awsEnumerations.WaitForCompletion.fromValue(data['waitForCompletion']))
        return message

    # Send to API (Computer Pacifico)

    @staticmethod
    def sendTickers(tickerList, arguments, author=None, verbose=True):
        if author is None:
            author = 76136279
        tickerJsonList = Ticker.getJsonList(tickerList, False)
        Message.publish(payload=tickerJsonList, task='tickers', author=author, origin=arguments.get("BOT_NAME"))
        if verbose:
            print(f"Amount of tickers sent: {len(tickerJsonList)}")
            if len(tickerJsonList) > 0:
                print(f"Example Ticker: {tickerJsonList[0]}")

    @staticmethod
    def sendValues(author, valueObjects, arguments, verbose=True):
        valueObjectsJsonList = Value.getJsonList(valueObjects, False)
        Message.publish(payload=valueObjectsJsonList, task='publish', author=author, origin=arguments.get("BOT_NAME"))
        if verbose:
            print(f"Amount of values sent: {len(valueObjectsJsonList)}")
            if len(valueObjectsJsonList) > 0:
                print(f"Example Value: {valueObjectsJsonList[0]}")

    @staticmethod
    def sendReports(author, reportsList, arguments, verbose=True):
        reportObjectsJsonList = Report.getJsonList(reportsList, False)
        Message.publish(payload=reportObjectsJsonList, task='reports', author=author, origin=arguments.get("BOT_NAME"))
        if verbose:
            print(f"Amount of reports sent: {len(reportObjectsJsonList)}")
            if len(reportObjectsJsonList) > 0:
                print(f"Example Report: {reportObjectsJsonList[0]}")
                print(f"Example Report Variant: {reportObjectsJsonList[0]['variant']}")

class _Data:
    def __init__(self, datePublication, dateEffective, quality, comment):
        self.datePublication = self.validate(datePublication)
        self.dateEffective = self.validate(dateEffective)
        self.quality = self.validate(quality)
        self.comment = self.validate(comment)

    def validate(self, attribute):
        if attribute is None:
            return ''
        else:
            return attribute

    def getDatepublication(self):
        return self.datePublication

    def getDateEffective(self):
        return self.dateEffective

    def getQuality(self):
        return self.quality

    def getComment(self):
        return self.comment

    @staticmethod
    def __serializeAndClean(dictionary):
        delete = []
        for key, value in zip(dictionary.keys(), dictionary.values()):
            if value == None:
                delete.append(key)
            elif isinstance(value, pacificoEnumerations.Enum):
                dictionary[key] = value.value
            elif isinstance(value, (datetime.date, datetime.datetime)):
                dictionary[key] = value.isoformat()
            else:
                dictionary[key] = value
        for key in delete:
            del dictionary[key]
        return dictionary

    def getJson(self, dumped=True):
        data = self.__dict__.copy()
        data = self.__serializeAndClean(data)
        if dumped:
            data = json.dumps(data)
        return data

class Value(_Data):
    def __init__(self, ticker, dateEffective, value, fieldType=pacificoEnumerations.FieldType.Field_Quote,
                 datePublication=datetime.date.today(), fixingPublication=pacificoEnumerations.Fixing.EOD,
                 dateTenor=datetime.date(1900, 1, 1), scenario='', comment='',
                 quality=pacificoEnumerations.Quality.Quality_Production):
        _Data.__init__(self, datePublication, dateEffective, quality, comment)
        self.ticker = self.validate(ticker)
        self.value = self.validate(value)
        self.fieldType = self.validate(fieldType)
        self.fixingPublication = self.validate(fixingPublication)
        if dateTenor == datetime.date(1900, 1, 1):
            self.dateTenor = self.dateEffective
        else:
            self.dateTenor = self.validate(dateTenor)
        self.scenario = self.validate(scenario)

    def getTicker(self):
        return self.ticker

    def getValue(self):
        return self.value

    def getFieldType(self):
        return self.fieldType

    def getFixingPublication(self):
        return self.fixingPublication

    def getDateTenor(self):
        return self.dateTenor

    def getScenario(self):
        return self.scenario

    @staticmethod
    def __checkExistenceAndReturnValue(data, name):
        if name in data.keys():
            value = data[name]
        else:
            value = ''
        return value

    @staticmethod
    def fromJson(jsonString):
        if isinstance(jsonString, str):
            data = json.loads(jsonString)
        else:
            data = jsonString
        ticker = Value.__checkExistenceAndReturnValue(data, 'ticker')
        dateEffective = datetime.datetime.fromisoformat(Value.__checkExistenceAndReturnValue(data, 'dateEffective'))
        value = Value.__checkExistenceAndReturnValue(data, 'value')
        fieldType = pacificoEnumerations.FieldType(Value.__checkExistenceAndReturnValue(data, 'fieldType'))
        datePublication = datetime.date.fromisoformat(Value.__checkExistenceAndReturnValue(data, 'datePublication'))
        fixingPublication = pacificoEnumerations.Fixing(Value.__checkExistenceAndReturnValue(data, 'fixingPublication'))
        dateTenor = datetime.datetime.fromisoformat(Value.__checkExistenceAndReturnValue(data, 'dateTenor'))
        scenario = Value.__checkExistenceAndReturnValue(data, 'scenario')
        comment = Value.__checkExistenceAndReturnValue(data, 'comment')
        quality = pacificoEnumerations.Quality(Value.__checkExistenceAndReturnValue(data, 'quality'))
        return Value(ticker, dateEffective, value, fieldType, datePublication, fixingPublication, dateTenor, scenario, comment, quality)

    @staticmethod
    def getJsonList(items, dumped=True):
        jsonList = [item.getJson(dumped=False) for item in items]
        if dumped:
            jsonList = json.dumps(jsonList)
        return jsonList

    @staticmethod
    def fromJsonList(jsonString):
        if isinstance(jsonString, str):
            items = json.loads(jsonString)
        else:
            items = jsonString
        return [Value.fromJson(item) for item in items]

    def getFieldValue(self):
        from api.src.core.Service.Field import FieldValue
        datePublication = self.getDatepublication()
        fixing = pacificoEnumerations.Fixing(self.getFixingPublication().value)
        ticker = self.getTicker()
        field = pacificoEnumerations.FieldType(self.getFieldType().value)
        dateEffective = self.getDateEffective()
        dateTenor = self.getDateTenor()
        value = self.getValue()
        other = self.getComment()
        return FieldValue.FieldValue(datePublication, fixing, ticker, field, dateEffective, dateTenor, value, other)

    @staticmethod
    def getFieldValueListFromJsonList(jsonString):
        jsonList = Value.fromJsonList(jsonString)
        return [item.getFieldValue() for item in jsonList]

class Report(_Data):
    def __init__(self, document, chapter, item, variant, dateEffective, section='', subsection='', paragraph='',
                 datePublication=datetime.date.today(), fixingPublication=pacificoEnumerations.Fixing.EOD,
                 dateTenor=datetime.date(1900, 1, 1), comment='',
                 quality=pacificoEnumerations.Quality.Quality_Production):
        _Data.__init__(self, datePublication, dateEffective, quality, comment)
        self.document = self.validate(document)
        self.chapter = self.validate(chapter)
        self.section = self.validate(section)
        self.subsection = self.validate(subsection)
        self.paragraph = self.validate(paragraph)
        self.item = self.validate(item)
        self.variant = self.validate(variant)
        self.fixingPublication = self.validate(fixingPublication)
        if dateTenor == datetime.date(1900, 1, 1):
            self.dateTenor = self.dateEffective
        else:
            self.dateTenor = self.validate(dateTenor)

    def getFixingPublication(self):
        return self.fixingPublication

    def getDateTenor(self):
        return self.dateTenor

    def getDocument(self):
        return self.document

    def getItem(self):
        return self.item

    def getChapter(self):
        return self.chapter

    def getSection(self):
        return self.section

    def getSubsection(self):
        return self.subsection

    def getParagraph(self):
        return self.paragraph

    def getVariant(self):
        return self.variant

    @staticmethod
    def __serializeAndClean(dictionary):
        from .api.src.util import Variant
        delete = []
        for key, value in zip(dictionary.keys(), dictionary.values()):
            if value == None:
                delete.append(key)
            elif isinstance(value, pacificoEnumerations.Enum):
                dictionary[key] = value.value
            elif isinstance(value, (datetime.date, datetime.datetime)):
                dictionary[key] = value.isoformat()
            elif isinstance(value, Variant.Variant):
                dictionary[key] = value.getJson()
            else:
                dictionary[key] = value
        for key in delete:
            del dictionary[key]
        return dictionary

    def getJson(self, dumped=True):
        data = self.__dict__.copy()
        data = self.__serializeAndClean(data)
        if dumped:
            data = json.dumps(data)
        return data

    @staticmethod
    def __checkExistenceAndReturnValue(data, name):
        if name in data.keys():
            value = data[name]
        else:
            value = ''
        return value

    @staticmethod
    def fromJson(jsonString):
        from .api.src.util import Variant
        if isinstance(jsonString, str):
            data = json.loads(jsonString)
        else:
            data = jsonString
        document = Report.__checkExistenceAndReturnValue(data, 'document')
        chapter = Report.__checkExistenceAndReturnValue(data, 'chapter')
        section = Report.__checkExistenceAndReturnValue(data, 'section')
        subsection = Report.__checkExistenceAndReturnValue(data, 'subsection')
        paragraph = Report.__checkExistenceAndReturnValue(data, 'paragraph')
        item = Report.__checkExistenceAndReturnValue(data, 'item')
        variant = Variant.Variant.fromJson(Report.__checkExistenceAndReturnValue(data, 'variant'))
        dateEffective = Report.__parseDateFromJson(Report.__checkExistenceAndReturnValue(data, 'dateEffective'))
        try:
            datePublication = Report.__parseDateFromJson(Report.__checkExistenceAndReturnValue(data, 'datePublication')).date()
        except:
            datePublication = datetime.date.today()
        try:
            fixingPublication = pacificoEnumerations.Fixing(Report.__checkExistenceAndReturnValue(data, 'fixingPublication'))
        except:
            fixingPublication = pacificoEnumerations.Fixing.EOD
        try:
            dateTenor = Report.__parseDateFromJson(Report.__checkExistenceAndReturnValue(data, 'dateTenor'))
        except:
            dateTenor = datetime.date(1900, 1, 1)
        comment = Report.__checkExistenceAndReturnValue(data, 'comment')
        try:
            quality = pacificoEnumerations.Quality(Report.__checkExistenceAndReturnValue(data, 'quality'))
        except:
            quality = pacificoEnumerations.Quality.Quality_Production
        return Report(document, chapter, item, variant, dateEffective, section, subsection, paragraph, datePublication, fixingPublication, dateTenor, comment, quality)

    @staticmethod
    def __parseDateFromJson(dateString):
        try:
            return datetime.datetime.fromisoformat(dateString)
        except:
            return Dates.dateTimeFromString(dateString)

    @staticmethod
    def getJsonList(items, dumped=True):
        jsonList = [item.getJson(dumped=False) for item in items]
        if dumped:
            jsonList = json.dumps(jsonList)
        return jsonList

    @staticmethod
    def fromJsonList(jsonString):
        if isinstance(jsonString, str):
            items = json.loads(jsonString)
        else:
            items = jsonString
        return [Report.fromJson(item) for item in items]

    def getFieldReport(self):
        from api.src.core.Service.Field import FieldReport
        datePublication = self.getDatepublication()
        fixing = pacificoEnumerations.Fixing(self.getFixingPublication().value)
        dateEffective = self.getDateEffective()
        dateTenor = self.getDateTenor()
        document = self.getDocument()
        item = self.getItem()
        chapter = self.getChapter()
        section = self.getSection()
        subsection = self.getSubsection()
        paragraph = self.getParagraph()
        variant = self.getVariant()
        other = self.getComment()
        return FieldReport.FieldReport(datePublication, fixing, dateEffective, dateTenor, document, item, chapter, section, subsection, paragraph, variant, other)

    @staticmethod
    def getFieldReportListFromJsonList(jsonString):
        jsonList = Report.fromJsonList(jsonString)
        return [item.getFieldReport() for item in jsonList]

    @staticmethod
    def buildFileReportPath(filePath, fileOrigin='', user='', host='', password='', extension=''):
        if fileOrigin in ['ec2', 'sftp', 'https', 'dropbox', '']:
            if user != '' or host != '' or password != '':
                filePath = '{}@{}:{}/{}'.format(user, host, password, filePath)
            reportFilepath = '{}/{}'.format(fileOrigin, filePath)
            if extension != '':
                reportFilepath = '{}${}'.format(reportFilepath, extension)
            return reportFilepath

    @staticmethod
    def uploadTemporalFileAndGetUrl(localFilepath):
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y-%H.%M.%S.%f")
        splittedLocalFilepath = str(localFilepath).rsplit('.', 1)
        localFilepathWithoutExtension = splittedLocalFilepath[0]
        extension = splittedLocalFilepath[-1]
        filepathBucket = f"{localFilepathWithoutExtension}_{timestamp}.{extension}"
        bucketName = "media-pacifico"
        awsAccessKey = Configuration.get("AWS_ACCESS_KEY_PACIFICO")
        awsSecretKey = Configuration.get("AWS_SECRET_KEY_PACIFICO")
        S3.writeFileToBucket(localFilepath, bucketName, awsAccessKey, awsSecretKey, filepathBucket, False)
        url = S3.getUrl(filepathBucket, bucketName, awsAccessKey=awsAccessKey, awsSecretKey=awsSecretKey)
        return url

class Entry(_Data):
    def __init__(self, nationalIdentificationNumber, nationalIdentificationNumberType, field, dateEffective, value,
                 valueType=pacificoEnumerations.ValueType.ValueType_Double, datePublication=datetime.date.today(),
                 comment='', quality=pacificoEnumerations.Quality.Quality_Production):
        _Data.__init__(self, datePublication, dateEffective, quality, comment)
        self.nationalIdentificationNumber = nationalIdentificationNumber
        self.nationalIdentificationNumberType = nationalIdentificationNumberType
        self.field = field
        self.value = value
        self.valueType = valueType

    @staticmethod
    def fromJson(jsonString):
        pass

    @staticmethod
    def getJsonList(items):
        pass

    @staticmethod
    def fromJsonList(jsonString):
        pass

class Ticker:
    def __init__(self, ticker, family, group='', market='',
                 country=pacificoEnumerations.Country.Country_Chile, description=''):
        self.ticker = ticker
        self.family = family
        self.group = group
        self.market = market
        self.country = country
        self.description = description

    def getTicker(self):
        return self.ticker

    def getFamily(self):
        return self.family

    def getGroup(self):
        return self.group

    def getMarket(self):
        return self.market

    def getCountry(self):
        return self.country

    def getDescription(self):
        return self.description

    @staticmethod
    def __serializeAndClean(dictionary):
        delete = []
        for key, value in zip(dictionary.keys(), dictionary.values()):
            if value == None:
                delete.append(key)
            elif isinstance(value, pacificoEnumerations.Enum):
                dictionary[key] = value.value
            elif isinstance(value, (datetime.date, datetime.datetime)):
                dictionary[key] = value.isoformat()
            else:
                dictionary[key] = value
        for key in delete:
            del dictionary[key]
        return dictionary

    def getJson(self, dumped=True):
        data = self.__dict__.copy()
        data = self.__serializeAndClean(data)
        if dumped:
            data = json.dumps(data)
        return data

    @staticmethod
    def __checkExistenceAndReturnValue(data, name):
        if name in data.keys():
            value = data[name]
        else:
            value = ''
        return value

    @staticmethod
    def fromJson(jsonString):
        if isinstance(jsonString, str):
            data = json.loads(jsonString)
        else:
            data = jsonString
        ticker = Ticker.__checkExistenceAndReturnValue(data, 'ticker')
        family = Ticker.__checkExistenceAndReturnValue(data, 'family')
        group = Ticker.__checkExistenceAndReturnValue(data, 'group')
        market = Ticker.__checkExistenceAndReturnValue(data, 'market')
        country = pacificoEnumerations.Country(Ticker.__checkExistenceAndReturnValue(data, 'country'))
        description = Ticker.__checkExistenceAndReturnValue(data, 'description')
        return Ticker(ticker, family, group, market, country, description)

    @staticmethod
    def getJsonList(items, dumped=True):
        jsonList = [item.getJson(dumped=False) for item in items]
        if dumped:
            jsonList = json.dumps(jsonList)
        return jsonList

    @staticmethod
    def fromJsonList(jsonString):
        if isinstance(jsonString, str):
            items = json.loads(jsonString)
        else:
            items = jsonString
        return [Ticker.fromJson(item) for item in items]

    def getFieldTicker(self):
        from api.src.core.Service.Field import FieldTicker
        mnemo = self.getTicker()
        family = self.getFamily()
        group = self.getGroup()
        market = self.getMarket()
        country = pacificoEnumerations.Country(self.getCountry().value)
        other = self.getDescription()
        return FieldTicker.FieldTicker(mnemo, family, group, market, country, other)

    @staticmethod
    def getFieldTickerListFromJsonList(jsonString):
        jsonList = Ticker.fromJsonList(jsonString)
        return [item.getFieldTicker() for item in jsonList]

class Property(Ticker):
    def __init__(self, field, family, group='', market='',
                 valueType=pacificoEnumerations.ValueType.ValueType_Double,
                 country=pacificoEnumerations.Country.Country_Unspecified, description=''):
        Ticker.__init__(self, field, family, group, market, country, description)
        self.valueType = valueType

    @abc.abstractmethod
    def getJson(self):
        pass

    @staticmethod
    def fromJson(jsonString):
        pass

    @staticmethod
    def getJsonList(items):
        pass

    @staticmethod
    def fromJsonList(jsonString):
        pass

if __name__ == '__main__':
    '''
    from util import Configuration
    awsAccessKey = Configuration.get('awsAccessKey', '')
    awsSecretKey = Configuration.get('awsSecretKey', '')
    m = Message._Message__fromJson('{"bfi": "tester"}')
    url = m.getPresignedUrl()
    print(url)
    mjson = m.getJson()
    print(mjson)
    print(m.send())
    n = Message.fromJson(mjson)
    print(n.getJson())

    #value = Value('IBM', datetime.date(2020, 12, 23), 1.2)
    #print(value.getJson())
    ticker1 = Ticker('X', 'Fam')
    ticker2 = Ticker('Y', 'Fam')
    tickerList = [ticker1, ticker2]
    jsonList = Ticker.getJsonList(tickerList)
    print(jsonList, type(jsonList))
    print(Ticker.fromJsonList(jsonList)[0].__dict__)
    #SENDED
    fieldTickersList = Ticker.getFieldTickerListFromJsonList(jsonList)
    print(fieldTickersList)
    print('-------------------------------------')
    value1 = Value('X', datetime.date.today(), 1)
    value2 = Value('Y', datetime.date.today(), 5)
    tickerList = [value1, value2]
    jsonList = Value.getJsonList(tickerList)
    print(jsonList, type(jsonList))
    print(Value.fromJsonList(jsonList)[0].__dict__)
    # SENDED
    fieldTickersList = Value.getFieldValueListFromJsonList(jsonList)
    print(fieldTickersList)
    
    event = """{"body": "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48Sm9iT3Blbj48c2VydmljZUxldmVsPjA8L3NlcnZpY2VMZXZlbD48Y2xpZW50PjxMb2NhdGlvblVzZXI+PGlkPjI1PC9pZD48L0xvY2F0aW9uVXNlcj48L2NsaWVudD48anVsaWFuUmVxdWVzdD4wPC9qdWxpYW5SZXF1ZXN0PjxmaWxlT3V0cHV0Pi9iZmkvb3V0cHV0L2ZpbGVPcGVuLnR4dDwvZmlsZU91dHB1dD48ZmlsZT48T2JqZWN0U3RvcmFibGU+PGlkPjY8L2lkPjwvT2JqZWN0U3RvcmFibGU+PC9maWxlPjwvSm9iT3Blbj4=", "params": {"path": {}, "querystring": {}, "header": {"Accept": "*/*", "Accept-Encoding": "gzip, deflate, br", "Content-Type": "application/xml", "Host": "api.bfi.lat", "Postman-Token": "9f07001b-b48f-484d-bd61-2eac1a0dcc82", "User-Agent": "PostmanRuntime/7.26.8", "X-Amzn-Trace-Id": "Root=1-600b2fb7-4d577b156d638412139f3762", "x-api-key": "5IKcBdC0iD7F5r1UtgoQJaTHXX74V2AU9tKywyOw", "X-Forwarded-For": "200.104.23.77", "X-Forwarded-Port": "443", "X-Forwarded-Proto": "https"}}, "stage-variables": {}, "context": {"account-id": "", "api-id": "0n18tlxoy1", "api-key": "5IKcBdC0iD7F5r1UtgoQJaTHXX74V2AU9tKywyOw", "authorizer-principal-id": "", "caller": "", "cognito-authentication-provider": "", "cognito-authentication-type": "", "cognito-identity-id": "", "cognito-identity-pool-id": "", "http-method": "POST", "stage": "gatekeeper", "source-ip": "200.104.23.77", "user": "", "user-agent": "PostmanRuntime/7.26.8", "user-arn": "", "request-id": "ee9ffc27-aafa-4540-a41d-00f6bb9e912d", "resource-id": "6pmb92t8yj", "resource-path": "/"}}"""
    message = Message.create(event)
    print(message)
    '''
    # variant = Variant.Variant(1, Enumerations.ValueType.ValueType_Integer)
    # x = Report('xx', 'xx', 'xx', variant, datetime.datetime.now())
    # xlist = Report.getFie