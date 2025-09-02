"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import json
from pacifico_devel.api.src.util import Dates, Enumerations, AmazonWebServices

def DataPointReportFromMessageReport(reports, awsAccessKey, awsSecretKey, author='BFI', versionName='', largeOutputs=True):
    if largeOutputs:
        if len(reports) > 10000:  # If it's too big, the compression will be done locally
            if author == 'BFI':
                author = 'Pacifico'
            if versionName == '':
                authorKey = author
            else:
                authorKey = author + '-' + versionName
            return json.dumps([authorKey] + [report.getJson(False) for report in reports])
    allDataPointReports = {}
    for report in reports:
        dataPointValues = {}
        # author = dataPointList[18]
        # versionName = dataPointList[17]
        datePublication = Dates.getDateString(report.getDatepublication())
        # dataPointValues['datePublication'] = datePublication
        if report.getFixingPublication() != Enumerations.Fixing.EOD.value:
            fixing = Enumerations.Fixing.getString(report.getFixingPublication())
            dataPointValues['fixing'] = fixing
        dateEffective = Dates.getDateTimeString(report.getDateEffective())
        # dataPointValues['dateEffective'] = dateEffective
        document = report.getDocument()
        chapter = report.getChapter()
        section = report.getSection()
        subsection = report.getSubsection()
        paragraph = report.getParagraph()
        item = report.getItem()
        variant = report.getVariant()
        variantValueType = variant.getValueType()  # Enumerations.ValueType(dataPointList[8])
        variantValue = variantValueType.fromDB(variant.getValue(asString=True))
        try:
            if variantValueType == Enumerations.ValueType.ValueType_File:
                fileName = variantValue.split('.amazonaws.com/', 1)[1]
                bucketName = variantValue.split('.s3.')[0].replace('https://', '')
                secondsItLasts = 86400  # 24hrs
                variantValue = AmazonWebServices.AmazonWebServices.getUrl(fileName, secondsItLasts, awsAccessKey, awsSecretKey, bucketName)
        except:
            pass
        variantValueType = variantValueType.getString()
        dataPointValues['variant'] = {'value': variantValue, 'type': variantValueType}
        #if dataPointList[9] not in [0, 1]:
        #    dataPointValues['quality'] = Enumerations.Quality.getString(Enumerations.Quality(dataPointList[9]))
        dateTenor = Dates.getDateTimeString(report.getDateTenor())
        if dateTenor != dateEffective:
            dataPointValues['dateTenor'] = dateTenor
        other = report.getComment()
        if other != '':
            dataPointValues['other'] = other
        addDataPointReports(author, versionName, datePublication, dateEffective, document, chapter, section, subsection, paragraph, item, dataPointValues, allDataPointReports)
    data = json.dumps(allDataPointReports)
    return data

def DataPointReportFromDB(dataPointsLists, awsAccessKey, awsSecretKey):
    allDataPointReports = {}
    for dataPointList in dataPointsLists:
        dataPointValues = {}
        author = dataPointList[18]
        versionName = dataPointList[17]
        datePublication = Dates.getDateString(Dates.julianToDate(float(dataPointList[9])))
        # dataPointValues['datePublication'] = datePublication
        if dataPointList[10] != Enumerations.Fixing.EOD.value:
            fixing = Enumerations.Fixing.getString(Enumerations.Fixing(dataPointList[10]))
            dataPointValues['fixing'] = fixing
        dateEffective = Dates.getDateTimeString(Dates.julianToDateTime(float(dataPointList[11])))
        # dataPointValues['dateEffective'] = dateEffective
        document = dataPointList[1]
        chapter = dataPointList[2]
        section = dataPointList[3]
        subsection = dataPointList[4]
        paragraph = dataPointList[5]
        item = dataPointList[6]
        variantValueType = Enumerations.ValueType(dataPointList[8])
        variantValue = variantValueType.fromDB(dataPointList[7])
        if variantValueType == Enumerations.ValueType.ValueType_File:
            fileName = variantValue.split('.amazonaws.com/', 1)[1]
            bucketName = variantValue.split('.s3.')[0].replace('https://', '')
            secondsItLasts = 86400  # 24hrs
            variantValue = AmazonWebServices.AmazonWebServices.getUrl(fileName, secondsItLasts, awsAccessKey, awsSecretKey, bucketName)
        variantValueType = variantValueType.getString()
        dataPointValues['variant'] = {'value': variantValue, 'type': variantValueType}
        #if dataPointList[9] not in [0, 1]:
        #    dataPointValues['quality'] = Enumerations.Quality.getString(Enumerations.Quality(dataPointList[9]))
        dateTenor = Dates.getDateTimeString(Dates.julianToDateTime(float(dataPointList[12])))
        if dateTenor != dateEffective:
            dataPointValues['dateTenor'] = dateTenor
        other = dataPointList[19]
        if other != '':
            dataPointValues['other'] = other
        addDataPointReports(author, versionName, datePublication, dateEffective, document, chapter, section, subsection, paragraph, item, dataPointValues, allDataPointReports)
    data = json.dumps(allDataPointReports)
    return data

def addDataPointReports(author, versionName, datePublication, dateEffective, document, chapter, section, subsection, paragraph, item, dataPointValues, allDataPointReports):
    if author == 'BFI':
        author = 'Pacifico'
    if versionName == '':
        authorKey = author
    else:
        authorKey = author + '-' + versionName
    if authorKey in allDataPointReports.keys():
        if datePublication in allDataPointReports[authorKey].keys():
            if dateEffective in allDataPointReports[authorKey][datePublication].keys():
                if document in allDataPointReports[authorKey][datePublication][dateEffective].keys():
                    if chapter in allDataPointReports[authorKey][datePublication][dateEffective][document].keys():
                        if section in allDataPointReports[authorKey][datePublication][dateEffective][document][chapter].keys():
                            if subsection in allDataPointReports[authorKey][datePublication][dateEffective][document][chapter][section].keys():
                                if paragraph in allDataPointReports[authorKey][datePublication][dateEffective][document][chapter][section][subsection].keys():
                                    if item in allDataPointReports[authorKey][datePublication][dateEffective][document][chapter][section][subsection][paragraph].keys():
                                        if dataPointValues in allDataPointReports[authorKey][datePublication][dateEffective][document][chapter][section][subsection][paragraph][item]:
                                            print('ioDataPointReport: This should never happen.')
                                        else:
                                            allDataPointReports[authorKey][datePublication][dateEffective][document][chapter][section][subsection][paragraph][item].append(dataPointValues)
                                    else:
                                        allDataPointReports[authorKey][datePublication][dateEffective][document][chapter][section][subsection][paragraph].update({item: [dataPointValues]})
                                else:
                                    allDataPointReports[authorKey][datePublication][dateEffective][document][chapter][section][subsection].update({paragraph: {item: [dataPointValues]}})
                            else:
                                allDataPointReports[authorKey][datePublication][dateEffective][document][chapter][section].update({subsection: {paragraph: {item: [dataPointValues]}}})
                        else:
                            allDataPointReports[authorKey][datePublication][dateEffective][document][chapter].update({section: {subsection: {paragraph: {item: [dataPointValues]}}}})
                    else:
                        allDataPointReports[authorKey][datePublication][dateEffective][document].update({chapter: {section: {subsection: {paragraph: {item: [dataPointValues]}}}}})
                else:
                    allDataPointReports[authorKey][datePublication][dateEffective].update({document: {chapter: {section: {subsection: {paragraph: {item: [dataPointValues]}}}}}})
            else:
                allDataPointReports[authorKey][datePublication].update({dateEffective: {document: {chapter: {section: {subsection: {paragraph: {item: [dataPointValues]}}}}}}})
        else:
            allDataPointReports[authorKey].update({datePublication: {dateEffective: {document: {chapter: {section: {subsection: {paragraph: {item: [dataPointValues]}}}}}}}})
    else:
        allDataPointReports.update({authorKey: {datePublication: {dateEffective: {document: {chapter: {section: {subsection: {paragraph: {item: [dataPointValues]}}}}}}}}})

def _recursive__addDataPointReports(author, versionName, document, chapter, section, subsection, paragraph, item, dataPointValues, allDataPointReports):
    if versionName == '':
        authorKey = author
    else:
        authorKey = author + '-' + versionName
    if authorKey in allDataPointReports.keys():
        if document in allDataPointReports[authorKey].keys():
            if chapter in allDataPointReports[authorKey][document].keys():
                if section in allDataPointReports[authorKey][document][chapter].keys():
                    if subsection in allDataPointReports[authorKey][document][chapter][section].keys():
                        if paragraph in allDataPointReports[authorKey][document][chapter][section][subsection].keys():
                            if item in allDataPointReports[authorKey][document][chapter][section][subsection][paragraph].keys():
                                print('ioDataPointReport: This should never happen.')
                            else:
                                allDataPointReports[authorKey][document][chapter][section][subsection][paragraph].update({item: dataPointValues})
                        else:
                            if paragraph != '':
                                allDataPointReports[authorKey][document][chapter][section][subsection].update({paragraph: {item: dataPointValues}})
                            else:
                                allDataPointReports[authorKey][document][chapter][section][subsection].update({item: dataPointValues})
                    else:
                        if subsection != '':
                            if paragraph != '':
                                allDataPointReports[authorKey][document][chapter][section].update({subsection: {paragraph: {item: dataPointValues}}})
                            else:
                                allDataPointReports[authorKey][document][chapter][section].update({subsection: {item: dataPointValues}})
                        else:
                            allDataPointReports[authorKey][document][chapter][section].update({item: dataPointValues})
                else:
                    if section != '':
                        if subsection != '':
                            if paragraph != '':
                                allDataPointReports[authorKey][document][chapter].update({section: {subsection: {paragraph: {item: dataPointValues}}}})
                            else:
                                allDataPointReports[authorKey][document][chapter].update({section: {subsection: {item: dataPointValues}}})
                        else:
                            allDataPointReports[authorKey][document][chapter].update({section: {item: dataPointValues}})
                    else:
                        allDataPointReports[authorKey][document][chapter].update({item: dataPointValues})
            else:
                if chapter != '':
                    if section != '':
                        if subsection != '':
                            if paragraph != '':
                                allDataPointReports[authorKey][document].update({chapter: {section: {subsection: {paragraph: {item: dataPointValues}}}}})
                            else:
                                allDataPointReports[authorKey][document].update({chapter: {section: {subsection: {item: dataPointValues}}}})
                        else:
                            allDataPointReports[authorKey][document].update({chapter: {section: {item: dataPointValues}}})
                    else:
                        allDataPointReports[authorKey][document].update({chapter: {item: dataPointValues}})
                else:
                    allDataPointReports[authorKey][document].update({item: dataPointValues})
        else:
            if chapter != '':
                if section != '':
                    if subsection != '':
                        if paragraph != '':
                            allDataPointReports[authorKey].update({document: {chapter: {section: {subsection: {paragraph: {item: dataPointValues}}}}}})
                        else:
                            allDataPointReports[authorKey].update({document: {chapter: {section: {subsection: {item: dataPointValues}}}}})
                    else:
                        allDataPointReports[authorKey].update({document: {chapter: {section: {item: dataPointValues}}}})
                else:
                    allDataPointReports[authorKey].update({document: {chapter: {item: dataPointValues}}})
            else:
                allDataPointReports[authorKey].update({document: {item: dataPointValues}})
    else:
        if chapter != '':
            if section != '':
                if subsection != '':
                    if paragraph != '':
                        allDataPointReports.update({authorKey: {document: {chapter: {section: {subsection: {paragraph: {item: dataPointValues}}}}}}})
                    else:
                        allDataPointReports.update({authorKey: {document: {chapter: {section: {subsection: {item: dataPointValues}}}}}})
                else:
                    allDataPointReports.update({authorKey: {document: {chapter: {section: {item: dataPointValues}}}}})
            else:
                allDataPointReports.update({authorKey: {document: {chapter: {item: dataPointValues}}}})
        else:
            allDataPointReports.update({authorKey: {document: {item: dataPointValues}}})