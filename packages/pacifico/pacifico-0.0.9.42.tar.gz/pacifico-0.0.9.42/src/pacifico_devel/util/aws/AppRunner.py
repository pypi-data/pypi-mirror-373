"""Copyright © 2021 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import urllib3
import os
import json
from ..cfg import Configuration

def run(arguments={}):
    appRunnerEndpoint = Configuration.get('APP_RUNNER_ENDPOINT')  # 'https://pyjnijtktj.us-west-2.awsapprunner.com/'
    botName = os.environ.get('AWS_LAMBDA_FUNCTION_NAME')  # 'BotCMF'
    data = {"bot name": botName}
    if isinstance(arguments, dict) and arguments != {}:
        data.update({"arguments": arguments})
    encoded_body = json.dumps(data)
    http = urllib3.PoolManager()
    headers = {'Content-Type': 'application/json'}
    response = http.request('POST', appRunnerEndpoint, headers=headers, body=encoded_body)
    return response.data.decode('utf-8')

def publish(appRunnerName, payloadJson):
    appRunnerEndpoint = Configuration.get('APP_RUNNER_ENDPOINT_{}'.format(appRunnerName))  # Add to config.csv file
    encoded_body = payloadJson  # json.dumps(data)
    http = urllib3.PoolManager()
    headers = {'Content-Type': 'application/json'}
    response = http.request('POST', appRunnerEndpoint, headers=headers, body=encoded_body)
    return response.data.decode('utf-8')
