"""Copyright © 2022 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import datetime
import requests
from .cfg import Configuration
from ..api.src.util import Downloader

def run(payload: str, dateNow: datetime.datetime, timeOut: int = 1800):
    url = __post(payload, dateNow).replace('"', '')
    response = Downloader.downloadResponse(url, timeOut=timeOut)
    return response

def __post(payload: str, dateNow: datetime.datetime):
    endpoint = Configuration.get('BFI_API_ENDPOINT')
    headers = {
        'x-api-key': Configuration.get('BFI_API_TOKEN_BFI'),
        'Content-Type': 'application/xml'
    }
    url = requests.post(endpoint, data=payload, headers=headers, verify=False).text
    return url
