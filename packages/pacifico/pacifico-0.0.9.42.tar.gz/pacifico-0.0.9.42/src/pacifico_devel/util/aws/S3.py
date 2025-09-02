"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import datetime
import boto3
import os
import requests
import time
from ..cfg import Configuration
from .. import Dates

def getS3Client(awsAccessKey='', awsSecretKey=''):
    if (awsAccessKey != '' and awsSecretKey != ''):
        s3 = boto3.client('s3', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
    else:
        s3 = boto3.client('s3', region_name='us-west-2')
    return s3

def getUrl(fileName, bucketName='bfi-media', timeout_s=86400, awsAccessKey='', awsSecretKey=''):
    client = getS3Client(awsAccessKey, awsSecretKey)
    response = client.generate_presigned_url('get_object', Params={'Bucket': bucketName, 'Key': fileName}, ExpiresIn=timeout_s)
    return response

def writeToBucket(stringData, filename, bucketName='bfi-media', awsAccessKey='', awsSecretKey='', bucketFilename=''):
    with open(filename, 'w') as outFile:
        outFile.write(stringData)
    writeFileToBucket(filename, bucketName, awsAccessKey, awsSecretKey, bucketFilename)

def writeFileToBucket(filename, bucketName='bfi-media', awsAccessKey='', awsSecretKey='', bucketFilename='', eraseLocalFile: bool=True):
    if bucketFilename == '':
        bucketFilename = filename
    client = getS3Client(awsAccessKey, awsSecretKey)
    client.upload_file(filename, bucketName, bucketFilename)
    if eraseLocalFile:
        removeLocalFile(filename)

def deleteFileFromBucket(bucketFilepath, bucketName='bfi-media', awsAccessKey='', awsSecretKey=''):
    client = getS3Client(awsAccessKey, awsSecretKey)
    client.delete_object(Bucket=bucketName, Key=bucketFilepath)

def listFilesFromBucket(bucketName='bfi-media', prefix='', awsAccessKey='', awsSecretKey=''):
    client = getS3Client(awsAccessKey, awsSecretKey)
    response = client.list_objects_v2(Bucket=bucketName, Prefix=prefix)
    return response

def downloadFromBucket(filepathBucket, filepathLocal='', bucketName='bfi-media', awsAccessKey='', awsSecretKey='', read=False):
    client = getS3Client(awsAccessKey, awsSecretKey)
    if filepathLocal == '':
        filepathLocal = filepathBucket.split('/')[-1]
    client.download_file(bucketName, filepathBucket, filepathLocal)
    time.sleep(0.1)
    if not os.path.isfile(filepathLocal):
        return downloadFromBucket(filepathBucket, filepathLocal, bucketName, awsAccessKey, awsSecretKey, read)
    else:
        if read:
            with open(filepathLocal) as f:
                inputString = f.read()
            return inputString

def getFileFromBucketAsString(filepathBucket, bucketName='bfi-media', awsAccessKey='', awsSecretKey=''):
    client = getS3Client(awsAccessKey, awsSecretKey)
    data = client.get_object(Bucket=bucketName, Key=filepathBucket)['Body'].read()
    return data.decode("utf-8-sig")

def removeLocalFile(filename):
    if os.path.isfile(filename):
        os.remove(filename)

def _readCSVFromString(csvString, separator=';'):
    csvAsMatrix = []
    lines = csvString.splitlines()
    for line in lines:
        values = line.split(separator)
        csvAsMatrix.append(values)
    return csvAsMatrix

def getCSVFromBucketAsListOfLists(filepathBucket, bucketName='bfi-media', awsAccessKey='', awsSecretKey='', separator=';'):
    stringData = getFileFromBucketAsString(filepathBucket, bucketName, awsAccessKey, awsSecretKey)
    listOflists = _readCSVFromString(stringData, separator)
    return listOflists

def writeToUrl(url, response):
    filename = str(Dates.getDateTimeTimestamp(datetime.datetime.now())) + '.txt'
    with open(filename, 'w') as outFile:
        outFile.write(response)
    with open(filename, 'rb') as readFile:
        response = requests.post(url['url'], data=url['fields'], files={'file': readFile})
    # print(str(response.content), str(response.text))
    removeLocalFile(filename)


if __name__ == '__main__':
    awsAccessKey = Configuration.get('AWS_ACCESS_KEY')
    awsSecretKey = Configuration.get('AWS_SECRET_KEY')
    filenpath = 'keys/computer_key.pem'
    bucketName = 'bfi-cfg'
    #downloadFromBucket(filenpath, '', bucketName, awsAccessKey, awsSecretKey)
    print(getFileFromBucketAsString(filenpath, bucketName, awsAccessKey, awsSecretKey))