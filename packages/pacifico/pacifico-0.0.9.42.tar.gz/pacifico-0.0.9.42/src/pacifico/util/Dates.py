"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import datetime

def getDateString(date):
    return date.strftime("%d/%m/%Y")

def getDateTimeString(dateTime):
    return dateTime.strftime("%d/%m/%Y %H:%M:%S")

def getDateTimeTimestamp(dateTime):
    return dateTime.strftime("%d.%m.%Y-%H.%M.%S.%f")

def getDateOrDateTimeString(dateOrDateTime):
    if isinstance(dateOrDateTime, datetime.datetime):
        string = getDateTimeString(dateOrDateTime)
    elif isinstance(dateOrDateTime, datetime.date):
        string = getDateString(dateOrDateTime)
    else:
        string = None
    return string

def dateTimeFromString(dateTimeString):
    return datetime.datetime.strptime(dateTimeString, "%d/%m/%Y %H:%M:%S")

def dateFromString(dateString):
    try:
        dateFromString = datetime.datetime.strptime(dateString, "%d/%m/%Y")
    except:
        dateFromString = datetime.datetime.strptime(dateString, "%Y-%m-%d")
    return dateFromString

def dateFromDateTimeOrDateString(dateTimeOrDateString):
    try:
        dateTimeOrDate = dateTimeFromString(dateTimeOrDateString)
    except:
        dateTimeOrDate = dateFromString(dateTimeOrDateString)
    return dateTimeOrDate.date()

def isDateTimeFromDateTimeOrDateString(dateTimeOrDateString):
    try:
        dateTimeOrDate = dateTimeFromString(dateTimeOrDateString)
        isDateTime = True
    except:
        dateTimeOrDate = dateFromString(dateTimeOrDateString)
        isDateTime = False
    return isDateTime

def createDateTimeFromValues(year, month, day, hour, minute, second):
    return datetime.datetime(year, month, day, hour, minute, second)


def roundToSeconds(dateTime):
    microseconds = int(str(dateTime.microsecond)[0])
    if microseconds >= 5:
        secondAdjustment = 1
    else:
        secondAdjustment = 0
    return datetime.datetime(dateTime.year, dateTime.month, dateTime.day, dateTime.hour, dateTime.minute, dateTime.second + secondAdjustment)
