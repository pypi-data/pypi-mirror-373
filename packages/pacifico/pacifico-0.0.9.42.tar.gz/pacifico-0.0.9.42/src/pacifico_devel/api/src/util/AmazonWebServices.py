"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import boto3
import os
from . import Enumerations, Configuration, Connection


class AmazonWebServices:

    @staticmethod
    def getToken(tokenId, awsAccessKey, awsSecretKey):
        client = boto3.client('apigateway', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey,
                              region_name='us-west-2')
        response = client.get_api_key(apiKey=tokenId, includeValue=True)
        token = response['value']
        return token

    @staticmethod
    def getName(tokenId, awsAccessKey, awsSecretKey):
        client = boto3.client('apigateway', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey,
                              region_name='us-west-2')
        response = client.get_api_key(apiKey=tokenId, includeValue=True)
        token = response['name']
        return token

    @staticmethod
    def createToken(name, awsAccessKey, awsSecretKey):
        client = boto3.client('apigateway', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey,
                              region_name='us-west-2')
        response = client.create_api_key(name=name, enabled=True)
        return response

    @staticmethod
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
                        usagePlanId=Configuration.Configuration.get('AWS_UsagePlanAdminID', connection),
                        keyId=tokenId,
                        keyType='API_KEY'
                    )
                elif usagePlan == Enumerations.UsagePlan.UsagePlan_Author:
                    response = client.create_usage_plan_key(
                        usagePlanId=Configuration.Configuration.get('AWS_UsagePlanAuthorID', connection),
                        keyId=tokenId,
                        keyType='API_KEY'
                    )
                elif usagePlan == Enumerations.UsagePlan.UsagePlan_Client:
                    response = client.create_usage_plan_key(
                        usagePlanId=Configuration.Configuration.get('AWS_UsagePlanUserID', connection),
                        keyId=tokenId,
                        keyType='API_KEY'
                    )
            elif action == Enumerations.Action.Action_Disable:
                if usagePlan == Enumerations.UsagePlan.UsagePlan_Administrator:
                    response = client.delete_usage_plan_key(
                        usagePlanId=Configuration.Configuration.get('AWS_UsagePlanAdminID', connection),
                        keyId=tokenId
                    )
                elif usagePlan == Enumerations.UsagePlan.UsagePlan_Author:
                    response = client.delete_usage_plan_key(
                        usagePlanId=Configuration.Configuration.get('AWS_UsagePlanAuthorID', connection),
                        keyId=tokenId
                    )
                elif usagePlan == Enumerations.UsagePlan.UsagePlan_Client:
                    response = client.delete_usage_plan_key(
                        usagePlanId=Configuration.Configuration.get('AWS_UsagePlanUserID', connection),
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
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Client, action, awsAccessKey, awsSecretKey, connection)
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Author, action, awsAccessKey, awsSecretKey, connection)
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Administrator, action, awsAccessKey, awsSecretKey, connection)
            elif usagePlan == Enumerations.UsagePlan.UsagePlan_Author:
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Client, action, awsAccessKey, awsSecretKey, connection)
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Author, action, awsAccessKey, awsSecretKey, connection)
            elif usagePlan == Enumerations.UsagePlan.UsagePlan_Client:
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Client, action, awsAccessKey, awsSecretKey, connection)
        elif action == Enumerations.Action.Action_Disable:
            if usagePlan == Enumerations.UsagePlan.UsagePlan_Administrator:
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Administrator, action, awsAccessKey, awsSecretKey, connection)
            elif usagePlan == Enumerations.UsagePlan.UsagePlan_Author:
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Author, action, awsAccessKey, awsSecretKey, connection)
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Administrator, action, awsAccessKey, awsSecretKey, connection)
            elif usagePlan == Enumerations.UsagePlan.UsagePlan_Client:
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Client, action, awsAccessKey, awsSecretKey, connection)
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Author, action, awsAccessKey, awsSecretKey, connection)
                AmazonWebServices.__applySingleAction(tokenId, Enumerations.UsagePlan.UsagePlan_Administrator, action, awsAccessKey, awsSecretKey, connection)

    @staticmethod
    def getUsagePlanKeys(usagePlan, awsAccessKey, awsSecretKey, connection):
        client = boto3.client('apigateway', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey,
                              region_name='us-west-2')
        if usagePlan == Enumerations.UsagePlan.UsagePlan_Client:
            plan = Configuration.Configuration.get("AWS_UsagePlanUserID", connection)
        elif usagePlan == Enumerations.UsagePlan.UsagePlan_Author:
            plan = Configuration.Configuration.get("AWS_UsagePlanAuthorID", connection)
        elif usagePlan == Enumerations.UsagePlan.UsagePlan_Administrator:
            plan = Configuration.Configuration.get("AWS_UsagePlanAdminID", connection)
        response = client.get_usage_plan_keys(
            usagePlanId=plan,
            #position='1',
            limit=500,
            #nameQuery='a'
        )
        return response['items']

    @staticmethod
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

    @staticmethod
    def getTokenId(token, awsAccessKey, awsSecretKey):
        tokens = AmazonWebServices.getTokens(awsAccessKey, awsSecretKey)
        tokenId = None
        for item in tokens:
            if item['value'] == token:
                tokenId = item['id']
        if tokenId != None:
            return tokenId
        else:
            raise KeyError('The token is not valid.')

    @staticmethod
    def isUsagePlanPermitted(token, usagePlan, awsAccessKey, awsSecretKey, connection):
        permitted = False
        tokenId = AmazonWebServices.getTokenId(token, awsAccessKey, awsSecretKey)
        keys = AmazonWebServices.getUsagePlanKeys(usagePlan, awsAccessKey, awsSecretKey, connection)
        for key in keys:
            if key['id'] == tokenId:
                permitted = True
        return permitted

    @staticmethod
    def getUrl(fileName, secondsItLasts, awsAccessKey, awsSecretKey, bucketName='', awsUrlAction=Enumerations.awsUrlAction.GET):
        if bucketName == '':
            bucketName = "media-pacifico"
        client = boto3.client('s3', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
        if awsUrlAction == Enumerations.awsUrlAction.PUT:
            response = client.generate_presigned_post(Bucket=bucketName, Key=fileName)  # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.generate_presigned_post
            # response = client.generate_presigned_url('put_object', Params={'Bucket': bucketName, 'Key': fileName}, ExpiresIn=secondsItLasts)  # https://stackoverflow.com/questions/52625812/boto3-generate-presigned-url-for-put-object-return-the-request-signature-we
        else:
            response = client.generate_presigned_url('get_object', Params={'Bucket': bucketName, 'Key': fileName}, ExpiresIn=secondsItLasts)
        return response

    @staticmethod
    def getUploadUrl(fileName, secondsItLasts, awsAccessKey, awsSecretKey, bucketName=''):
        if bucketName == '':
            bucketName = "media-pacifico"
        client = boto3.client('s3', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
        response = client.generate_presigned_url('put_object', Params={'Bucket': bucketName, 'Key': fileName}, ExpiresIn=secondsItLasts)
        return response

    @staticmethod
    def writeToBucket(stringData, filename, awsAccessKey, awsSecretKey, bucketFilename=''):
        if bucketFilename == '':
            bucketFilename = filename
        with open(filename, 'w') as outFile:
            outFile.write(stringData)
        client = boto3.client('s3', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
        bucketName = "media-pacifico"
        client.upload_file(filename, bucketName, bucketFilename)
        os.remove(filename)

    @staticmethod
    def downloadFromBucket(filepathBucket, awsAccessKey, awsSecretKey, filepathLocal='', bucketName="media-pacifico", read=True):
        client = boto3.client('s3', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
        if filepathLocal == '':
            filepathLocal = filepathBucket.split('/')[-1]
        client.download_file(bucketName, filepathBucket, filepathLocal)
        if read:
            with open(filepathLocal) as f:
                inputString = f.read()
            return inputString

    @staticmethod
    def getFileFromBucketAsString(filepathBucket, bucketName="media-pacifico", awsAccessKey='', awsSecretKey=''):
        client = boto3.client('s3', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
        data = client.get_object(Bucket=bucketName, Key=filepathBucket)['Body'].read()
        return data.decode("utf-8-sig")


if __name__=='__main__':
    from . import Enumerations

    connection = Connection.Connection.connect()
    token = 'kiHjqpmpIz8myYdoUpuXKa4rQ6IYaLva6wx9tFKy'
    usagePlan = Enumerations.UsagePlan.UsagePlan_Client
    id = AmazonWebServices.getTokenId(token, Configuration.Configuration.get('AWS_ACCESS_KEY', connection), Configuration.Configuration.get('AWS_SECRET_KEY', connection))
    usagePlanKeys = AmazonWebServices.getUsagePlanKeys(usagePlan, Configuration.Configuration.get('AWS_ACCESS_KEY', connection), Configuration.Configuration.get('AWS_SECRET_KEY', connection), connection)
    print(id)
    print(usagePlanKeys)
    permitted = AmazonWebServices.isUsagePlanPermitted(token, usagePlan, Configuration.Configuration.get('AWS_ACCESS_KEY', connection), Configuration.Configuration.get('AWS_SECRET_KEY', connection), connection)
    print(permitted)
    name = AmazonWebServices.getName(id, Configuration.Configuration.get('AWS_ACCESS_KEY', connection), Configuration.Configuration.get('AWS_SECRET_KEY', connection))
    print(name)
