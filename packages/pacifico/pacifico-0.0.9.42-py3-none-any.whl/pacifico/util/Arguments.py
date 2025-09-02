"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import argparse
import datetime
from pacifico.util import Enumerations


def parseArguments():
    parser = argparse.ArgumentParser()
    # Obligatory Arguments
    parser.add_argument("-service", type=str, default="r", help="Service Type", choices=['r'])
    parser.add_argument("-token", type=str, default="token.key", help="Token as a string or filepath for the token file (.txt, .crt, .cer, .key).")
    # Optional Arguments
    parser.add_argument("-fp", "--filepath", type=str, default="pacifico_data", help="Filepath and name for the output file (.txt).")
    parser.add_argument("-ticker", type=str, default="", help="Requested Ticker (e.g. 'ABNA12 &10')")
    parser.add_argument("-family", type=str, default="", help="Requested Family (e.g. 'LH')")
    parser.add_argument("-group", type=str, default="", help="Requested Group (e.g. 'LH')")
    parser.add_argument("-market", type=str, default="", help="Requested Market (e.g. 'RF')")
    parser.add_argument("-country", type=str, default="", help="Requested Country", choices=['Chile', 'Colombia', 'Peru', 'Mexico', 'Argentina', 'Risk Factors'])
    today = datetime.date.today()
    parser.add_argument("-dateStart", type=str, default=today.strftime("%d/%m/%Y"), help="Request Date Start (format: 'day/month/year')")
    parser.add_argument("-dateEnd", type=str, default=today.strftime("%d/%m/%Y"), help="Request Date End (format: 'day/month/year')")
    parser.add_argument("-f", "--fixing", type=str, default="EOD", help="Requested Fixing", choices=['EOD', 'F_0000', 'F_0030', 'F_0100', 'F_0130', 'F_0200', 'F_0230', 'F_0300', 'F_0330', 'F_0400', 'F_0430', 'F_0500', 'F_0530', 'F_0600', 'F_0630', 'F_0700', 'F_0730', 'F_0800', 'F_0830', 'F_0900', 'F_0930', 'F_1000', 'F_1030', 'F_1100', 'F_1130', 'F_1200', 'F_1230', 'F_1300', 'F_1330', 'F_1400', 'F_1430', 'F_1500', 'F_1530', 'F_1600', 'F_1630', 'F_1700', 'F_1730', 'F_1800', 'F_1830', 'F_1900', 'F_1930', 'F_2000', 'F_2030', 'F_2100', 'F_2130', 'F_2200', 'F_2230', 'F_2300', 'F_2330'])
    parser.add_argument("-ft", "--fieldType", type=str, default="Unspecified", help="Requested Field Type", choices=['Unspecified', 'Price', 'Yield', 'Duration', 'Convexity', 'Delta', 'Gamma', 'Vega', 'Volatility', 'Quote'])
    parser.add_argument("-vt", "--versionType", type=str, default="Unspecified", help="Requested Version Type", choices=['Unspecified', 'Pricing', 'Prediction'])
    parser.add_argument("-author", type=str, default="", help="Requested Author (e.g. 'BFI')")
    parser.add_argument("-version", type=str, default="", help="Requested Version (e.g. '')")
    parser.add_argument("-quality", type=str, default="Unspecified", help="Requested Quality", choices=['Unspecified', 'Production', 'Certification', 'Development'])
    parser.add_argument("-to", "--timeOut", type=int, default=300, help="Request time out limit")
    parser.add_argument("-tf", "--timeFrecuency", type=int, default=5, help="Request checking frecuency")
    parser.add_argument("-format", type=str, default='json', help="Output format", choices=['json', 'dictionary', 'dataFrame'])
    args = parser.parse_args()
    return args

def checkArguments(args):
    # Country
    country = Enumerations.Country.fromString(args.country)
    # Date Start
    try:
        dateStart = datetime.datetime.strptime(args.dateStart, "%d/%m/%Y").date()
    except:
        print(
            'WARNING - dateStart: The date or date format is not valid, the dateStart has been set to default (today).')
        dateStart = datetime.date.today()
    # Date End
    try:
        dateEnd = datetime.datetime.strptime(args.dateEnd, "%d/%m/%Y").date()
    except:
        print('WARNING - dateEnd: The date or date format is not valid, the dateStart has been set to default (today).')
        dateEnd = datetime.date.today()
    # Fixing
    fixing = Enumerations.Fixing[args.fixing]
    # Data Type
    fieldType = Enumerations.FieldType.fromString(args.fieldType)
    # Version Type
    versionType = Enumerations.VersionType.fromString(args.versionType)
    # Quality
    quality = Enumerations.Quality.fromString(args.quality)
    return country, dateStart, dateEnd, fixing, fieldType, versionType, quality

def tokenReader(tokenString=''):
    if tokenString == '':
        with open('token.key', 'r') as file:
            token = file.read()
    elif tokenString[-4:] == '.txt' or tokenString[-4:] == '.key':
        with open(tokenString, 'r') as file:
            token = file.read()
    else:
        token = tokenString
    return token