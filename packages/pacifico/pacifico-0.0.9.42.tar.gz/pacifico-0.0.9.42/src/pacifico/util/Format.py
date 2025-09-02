"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import json
import pandas
import requests
import datetime
from pacifico.util import Enumerations, Dates
from pacifico_devel.api.src.util import Enumerations as pacificoEnumerations
from pacifico_devel.util.cfg import Configuration
from pacifico_devel import Message
from pacifico_devel.api.src.io.DataPoint.DataPointReport import DataPointReport as ioDataPointReport
try:
    from pacifico_devel.util.selenium import SeleniumWebdriver
except Exception as e:
    print(f'Format: Importing SeleniumWebdriver error: {str(e)}.')


def jsonToFormat(format, response):
    if len(response) < 100 and 'error' in response:
        response = None
    if format == Enumerations.Format.Json:
        if response is None:
            return '{"Error": "There has been an internal error processing the request!"}'
        return response
    elif format == Enumerations.Format.Dictionary:
        if response is None:
            return {'Error': 'There has been an internal error processing the request!'}
        return json.loads(response)
    elif format == Enumerations.Format.DataFrame:
        if response is None:
            scenario = 'Pacifico'
            datePublicationAux = datetime.date.today()
            dateEffectiveAux = datetime.datetime.now()
            country = Enumerations.Country.Country_Unspecified
            market = ''
            group = ''
            family = ''
            ticker = 'Error'
            value = ''
            field = Enumerations.FieldType.Field_Unspecified
            dateTenor = datePublicationAux
            other = 'There has been an internal error processing the request!'
            dataFrameData = [[scenario, datePublicationAux, dateEffectiveAux, country, market, group, family, ticker, value, field, dateTenor, other]]
            return pandas.DataFrame(dataFrameData, columns=['Scenario', 'Date Publication', 'Date Effective', 'Country', 'Market', 'Group', 'Family', 'Ticker', 'Value', 'Field', 'Date Tenor', 'Other'])

    return jsonToDataFrame(response)

def jsonToDataFrame(jsonString):
    # Is a json value
    isJsonValue = '"field"' in jsonString
    # Is a json Report
    isJsonReport = '"variant"' in jsonString or '/bfi/input/reports' in jsonString or jsonString is None
    if isJsonValue:
        return jsonValuesToDataFrame(jsonString)
    elif isJsonReport:
        return jsonReportsToDataFrame(jsonString)
    else:
        return jsonValuesToDataFrame(jsonString)

def jsonReportsToDataFrame(jsonString):
    try:
        return _jsonReportsToDataFrame(jsonString)
    except:
        dataFrameData = []
        author = 'Pacifico'
        document = 'Error'
        chapter = ''
        section = ''
        subsection = ''
        paragraph = ''
        item = ''
        datePublicationObject = datetime.date.today()
        dateEffectiveObject = datetime.datetime.now()
        fixing = ''
        appString = ''
        if '/bfi/input/reports' in jsonString:
            appString = 'application '
        variantValue = f'There has been an error receiving (parsing) the {appString}requested reports data!'
        variantValueType = Enumerations.ValueType.ValueType_String
        dateTenor = ''
        other = jsonString[:100]
        dataFrameData.append([author, document, chapter, section, subsection, paragraph, item, datePublicationObject,
                              dateEffectiveObject, fixing, variantValue, variantValueType, dateTenor, other])
        return pandas.DataFrame(dataFrameData,
                                columns=['Author', 'Document', 'Chapter', 'Section', 'Subsection', 'Paragraph', 'Item',
                                         'Date Publication', 'Date Effective', 'Fixing', 'Value', 'Value Type',
                                         'Date Tenor', 'Other'])

def _jsonReportsToDataFrame(jsonString):
    dataFrameData = []
    firstBrowser = True
    windowCount = 0
    data = json.loads(jsonString)
    # Pre processed
    if isinstance(data, list):  # C++ response
        try:  # Could be just a very big response
            reports = parseRawReports(data)
            awsAccessKey = None
            awsSecretKey = None
            jsonString = ioDataPointReport.DataPointReportFromMessageReport(reports, awsAccessKey, awsSecretKey)
            data = json.loads(jsonString)
        except:
            pass
    if isinstance(data, list):  # Response is too big, over 5000 reports
        # print('Large response received, parsing...', end='')
        author = data[0]
        for reportJson in data[1:]:
            document = reportJson.get('document', '')
            chapter = reportJson.get('chapter', '')
            section = reportJson.get('section', '')
            subsection = reportJson.get('subsection', '')
            paragraph = reportJson.get('paragraph', '')
            item = reportJson.get('item', '')
            datePublicationObject = datetime.datetime.fromisoformat(reportJson.get('datePublication'))
            dateEffectiveObject = datetime.datetime.fromisoformat(reportJson.get('dateEffective'))
            fixing = reportJson.get('fixingPublication', '')
            variant = json.loads(reportJson.get('variant'))
            variantValueType = Enumerations.ValueType(int(variant['valueType']))
            variantValue = variantValueType.forceType(variant['value'])
            variantValueType = variantValueType.getString()
            dateTenor = reportJson.get('dateTenor')
            if dateTenor is None:
                dateTenor = ''
            else:
                dateTenor = datetime.datetime.fromisoformat(dateTenor)
            other = reportJson.get('comment', '')
            dataFrameData.append([author, document, chapter, section, subsection, paragraph, item, datePublicationObject, dateEffectiveObject, fixing, variantValue, variantValueType, dateTenor, other])
        # print('Done!')
    else:
        for author in data.keys():
            for datePublication in data[author].keys():
                for dateEffective in data[author][datePublication].keys():
                    for document in data[author][datePublication][dateEffective].keys():
                        for chapter in data[author][datePublication][dateEffective][document].keys():
                            for section in data[author][datePublication][dateEffective][document][chapter].keys():
                                for subsection in data[author][datePublication][dateEffective][document][chapter][section].keys():
                                    for paragraph in data[author][datePublication][dateEffective][document][chapter][section][subsection].keys():
                                        for item in data[author][datePublication][dateEffective][document][chapter][section][subsection][paragraph].keys():
                                            for reportDict in data[author][datePublication][dateEffective][document][chapter][section][subsection][paragraph][item]:
                                                if isinstance(datePublication, str):
                                                    datePublicationObject = datetime.datetime.strptime(datePublication, "%d/%m/%Y")
                                                else:
                                                    datePublicationObject = datePublication
                                                if 'fixing' in reportDict.keys():
                                                    fixing = reportDict['fixing']
                                                else:
                                                    fixing = ''
                                                if isinstance(dateEffective, str):
                                                    dateEffectiveObject = datetime.datetime.strptime(dateEffective, "%d/%m/%Y %H:%M:%S")
                                                else:
                                                    dateEffectiveObject = dateEffective
                                                variant = reportDict['variant']
                                                variantValueType = Enumerations.ValueType.fromString(variant['type'])
                                                variantValue = variantValueType.forceType(variant['value'])
                                                if variantValueType == Enumerations.ValueType.ValueType_Browser:
                                                    try:
                                                        import os
                                                        from selenium.webdriver.common.keys import Keys
                                                        html = requests.get(variantValue).content
                                                        wd = os.getcwd()
                                                        filename = os.path.join(wd, 'browser.html')
                                                        with open(filename, 'wb') as file:
                                                            file.write(html)
                                                        if firstBrowser:
                                                            driver = SeleniumWebdriver.getDriver(detach=True)
                                                            firstBrowser = False
                                                        else:
                                                            windowCount += 1
                                                            tabName = str(windowCount)
                                                            driver.execute_script(f"window.open('about:blank','{tabName}');")
                                                            driver.switch_to.window(f"{tabName}")
                                                        driver.get("file:" + filename)
                                                        os.remove(filename)
                                                    except Exception as e:
                                                        print(f"Formatting Error: Browser type values couldn't be "
                                                              f"displayed, probably because Google Chrome is not "
                                                              f"installed. ({str(e)})")
                                                variantValueType = variantValueType.getString()
                                                if 'dateTenor' in reportDict.keys():
                                                    if isinstance(reportDict['dateTenor'], str):
                                                        dateTenor = datetime.datetime.strptime(reportDict['dateTenor'],"%d/%m/%Y %H:%M:%S")
                                                    else:
                                                        dateTenor = reportDict['dateTenor']
                                                else:
                                                    dateTenor = ''
                                                if 'other' in reportDict.keys():
                                                    other = reportDict['other']
                                                else:
                                                    other = ''
                                                dataFrameData.append([author, document, chapter, section, subsection, paragraph, item, datePublicationObject, dateEffectiveObject, fixing, variantValue, variantValueType, dateTenor, other])
    return pandas.DataFrame(dataFrameData, columns=['Author', 'Document', 'Chapter', 'Section', 'Subsection', 'Paragraph', 'Item', 'Date Publication', 'Date Effective', 'Fixing', 'Value', 'Value Type', 'Date Tenor', 'Other'])

def jsonValuesToDataFrame(jsonString):
    try:
        return _jsonValuesToDataFrame(jsonString)
    except:
        dataFrameData = []
        scenario = 'Pacifico'
        datePublicationAux = datetime.date.today()
        dateEffectiveAux = datetime.datetime.now()
        country = Enumerations.Country.getString(pacificoEnumerations.Country.Country_Unspecified)
        market = ''
        group = ''
        family = ''
        ticker = 'Error'
        value = 'There has been an error receiving (parsing) the requested values data!'
        field = Enumerations.FieldType.getString(pacificoEnumerations.FieldType.Field_Metadata)
        dateTenor = ''
        other = jsonString[:100]
        dataFrameData.append(
            [scenario, datePublicationAux, dateEffectiveAux, country, market, group, family, ticker, value, field,
             dateTenor, other])
        return pandas.DataFrame(dataFrameData,
                                columns=['Scenario', 'Date Publication', 'Date Effective', 'Country', 'Market', 'Group',
                                         'Family', 'Ticker', 'Value', 'Field', 'Date Tenor', 'Other'])


def _jsonValuesToDataFrame(jsonString):
    dataFrameData = []
    data = json.loads(jsonString)
    for scenario in data.keys():
        for datePublication in data[scenario].keys():
            for dateEffective in data[scenario][datePublication].keys():
                for country in data[scenario][datePublication][dateEffective].keys():
                    for market in data[scenario][datePublication][dateEffective][country].keys():
                        for group in data[scenario][datePublication][dateEffective][country][market].keys():
                            for family in data[scenario][datePublication][dateEffective][country][market][group].keys():
                                for ticker in data[scenario][datePublication][dateEffective][country][market][group][family].keys():
                                    for dictValue in data[scenario][datePublication][dateEffective][country][market][group][family][ticker]:
                                        value = dictValue['value']
                                        field = dictValue['field']
                                        if 'dateTenor' in dictValue.keys():
                                            if isinstance(dictValue['dateTenor'], str):
                                                dateTenor = datetime.datetime.strptime(dictValue['dateTenor'], "%d/%m/%Y %H:%M:%S")
                                            else:
                                                dateTenor = dictValue['dateTenor']
                                        else:
                                            dateTenor = ''
                                        if 'other' in dictValue.keys():
                                            other = dictValue['other']
                                        else:
                                            other = ''
                                        if isinstance(dateEffective, str):
                                            dateEffectiveAux = datetime.datetime.strptime(dateEffective, "%d/%m/%Y %H:%M:%S")
                                        else:
                                            dateEffectiveAux = dateEffective
                                        if isinstance(datePublication, str):
                                            datePublicationAux = datetime.datetime.strptime(datePublication, "%d/%m/%Y")
                                        else:
                                            datePublicationAux = datePublication
                                        dataFrameData.append([scenario, datePublicationAux, dateEffectiveAux, country, market, group, family, ticker, value, field, dateTenor, other])
    return pandas.DataFrame(dataFrameData, columns=['Scenario', 'Date Publication', 'Date Effective', 'Country', 'Market', 'Group', 'Family', 'Ticker', 'Value', 'Field', 'Date Tenor', 'Other'])

def parseRawReports(reportsJson, loaded=True):
    if loaded:
        loadedResponse = reportsJson
    else:
        loadedResponse = json.loads(reportsJson)
    reports = []
    # if isinstance(loadedResponse, dict):
    #     for key, item in loadedResponse.items():
    #         if '.json' in key:
    #             reportsRaw = json.loads(item)
    #             for reportRaw in reportsRaw:
    #                 report = Message.Report.fromJson(reportRaw)
    #                 reports.append(report)
    # elif isinstance(loadedResponse, list):
    for reportRaw in loadedResponse:
        if isinstance(reportRaw, list):
            for innerReportRaw in reportRaw:
                report = Message.Report.fromJson(innerReportRaw)
                reports.append(report)
        else:
            report = Message.Report.fromJson(reportRaw)
            reports.append(report)
    return reports
