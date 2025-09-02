"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import boto3
from ...util.aws import Enumerations
from ...util.cfg import Configuration


def getToken(tokenId, awsAccessKey, awsSecretKey):
    client = boto3.client('apigateway', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey,
                          region_name='us-west-2')
    response = client.get_api_key(apiKey=tokenId, includeValue=True)
    token = response['value']
    return token

def getName(tokenId, awsAccessKey, awsSecretKey):
    client = boto3.client('apigateway', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey,
                          region_name='us-west-2')
    response = client.get_api_key(apiKey=tokenId, includeValue=True)
    token = response['name']
    return token

def createToken(name, awsAccessKey, awsSecretKey):
    client = boto3.client('apigateway', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey,
                          region_name='us-west-2')
    response = client.create_api_key(name=name, enabled=True)
    return response

def __applySingleAction(tokenId, usagePlan, action, awsAccessKey, awsSecretKey, connection):
    if not isinstance(usagePlan, Enumerations.UsagePlan):
        raise TypeError("The usagePlan must be set to a class 'Enumerations.UsagePlan'.")
    if not isinstance(action, Enumerations.Action):
        raise TypeError("The action must be set to a class 'Enumerations.Action'.")
    client = boto3.client('apigateway', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey,
                          region_name='us-west-2')
    try:
        if action == Enumerations.Action.Action_Enable:
            if usagePlan == Enumerations.UsagePlan.UsagePlan_Administrator:
                response = client.create_usage_plan_key(
                    usagePlanId=Configuration.get('AWS_UsagePlanAdminID', connection),
                    keyId=tokenId,
                    keyType='API_KEY'
                )
            elif usagePlan == Enumerations.UsagePlan.UsagePlan_Author:
                response = client.create_usage_plan_key(
                    usagePlanId=Configuration.get('AWS_UsagePlanAuthorID', connection),
                    keyId=tokenId,
                    keyType='API_KEY'
                )
            elif usagePlan == Enumerations.UsagePlan.UsagePlan_Client:
                response = client.create_usage_plan_key(
                    usagePlanId=Configuration.get('AWS_UsagePlanUserID', connection),
                    keyId=tokenId,
                    keyType='API_KEY'
                )
        elif action == Enumerations.Action.Action_Disable:
            if usagePlan == Enumerations.UsagePlan.UsagePlan_Administrator:
                response = client.delete_usage_plan_key(
                    usagePlanId=Configuration.get('AWS_UsagePlanAdminID', connection),
                    keyId=tokenId
                )
            elif usagePlan == Enumerations.UsagePlan.UsagePlan_Author:
                response = client.delete_usage_plan_key(
                    usagePlanId=Configuration.get('AWS_UsagePlanAuthorID', connection),
                    keyId=tokenId
                )
            elif usagePlan == Enumerations.UsagePlan.UsagePlan_Client:
                response = client.delete_usage_plan_key(
                    usagePlanId=Configuration.get('AWS_UsagePlanUserID', connection),
                    keyId=tokenId
                )
    except:
        #print('AmazonWebServices.apply : This action ( ' + action.serial + ' - ' + usagePlan.serial + ' ) has already been applied to this token.')
        pass
    # print(response) # Uncomment to print response

@staticmethod
def apply(tokenId, usagePlan, action, awsAccessKey, awsSecretKey, connection):
    if action == Enumerations.Action.Action_Enable:
        if usagePlan == Enumerations.UsagePlan.UsagePlan_Administrator:
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Client, action, awsAccessKey, awsSecretKey, connection)
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Author, action, awsAccessKey, awsSecretKey, connection)
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Administrator, action, awsAccessKey, awsSecretKey, connection)
        elif usagePlan == Enumerations.UsagePlan.UsagePlan_Author:
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Client, action, awsAccessKey, awsSecretKey, connection)
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Author, action, awsAccessKey, awsSecretKey, connection)
        elif usagePlan == Enumerations.UsagePlan.UsagePlan_Client:
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Client, action, awsAccessKey, awsSecretKey, connection)
    elif action == Enumerations.Action.Action_Disable:
        if usagePlan == Enumerations.UsagePlan.UsagePlan_Administrator:
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Administrator, action, awsAccessKey, awsSecretKey, connection)
        elif usagePlan == Enumerations.UsagePlan.UsagePlan_Author:
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Author, action, awsAccessKey, awsSecretKey, connection)
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Administrator, action, awsAccessKey, awsSecretKey, connection)
        elif usagePlan == Enumerations.UsagePlan.UsagePlan_Client:
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Client, action, awsAccessKey, awsSecretKey, connection)
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Author, action, awsAccessKey, awsSecretKey, connection)
            __applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Administrator, action, awsAccessKey, awsSecretKey, connection)

def getUsagePlanKeys(usagePlan, awsAccessKey, awsSecretKey, connection):
    client = boto3.client('apigateway', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey,
                          region_name='us-west-2')
    if usagePlan == Enumerations.UsagePlan.UsagePlan_Client:
        plan = Configuration.get("AWS_UsagePlanUserID", connection)
    elif usagePlan == Enumerations.UsagePlan.UsagePlan_Author:
        plan = Configuration.get("AWS_UsagePlanAuthorID", connection)
    elif usagePlan == Enumerations.UsagePlan.UsagePlan_Administrator:
        plan = Configuration.get("AWS_UsagePlanAdminID", connection)
    response = client.get_usage_plan_keys(
        usagePlanId=plan,
        #position='1',
        limit=500,
        #nameQuery='a'
    )
    return response['items']

def getTokens(awsAccessKey, awsSecretKey):
    client = boto3.client('apigateway', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey,
                          region_name='us-west-2')
    response = client.get_api_keys(
        #position='string',
        limit=500,
        #nameQuery='string',
        #customerId='string',
        includeValues=True | False
    )
    return response['items']

def getTokenId(token, awsAccessKey, awsSecretKey):
    tokens = getTokens(awsAccessKey, awsSecretKey)
    print(tokens)
    tokenId = None
    for item in tokens:
        if item['value'] == token:
            tokenId = item['id']
    if tokenId != None:
        return tokenId
    else:
        raise KeyError('The token is not valid.')

def isUsagePlanPermitted(token, usagePlan, awsAccessKey, awsSecretKey, connection):
    permitted = False
    tokenId = getTokenId(token, awsAccessKey, awsSecretKey)
    keys = getUsagePlanKeys(usagePlan, awsAccessKey, awsSecretKey, connection)
    for key in keys:
        if key['id'] == tokenId:
            permitted = True
    return permitted