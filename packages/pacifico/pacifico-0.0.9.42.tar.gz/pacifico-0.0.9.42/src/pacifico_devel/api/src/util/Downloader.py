"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import requests
import time

def downloadResponse(url, timeOut=300, timeFrecuency=0.5):
    startTime = time.time()
    while time.time() - startTime < timeOut:
        response = requests.get(url)
        if not 'Error' in response.text and not 'processing' in response.text:
            break
        else:
            time.sleep(timeFrecuency)
            if time.time() - startTime > timeOut:
                raise TimeoutError("The time out limit (" + str(timeOut) + " seconds) has been exceeded.")
    return response.text