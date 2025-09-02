"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import time
import boto3
import json
import os
from ...util.cfg import Configuration
from ...util.aws import S3, SSH, Enumerations

def getEC2Client(awsAccessKey, awsSecretKey):
    return boto3.client('ec2', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')

def getEC2Resource(awsAccessKey, awsSecretKey):
    return boto3.resource('ec2', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')

def getAllInstancesObjects(awsAccessKey, awsSecretKey):
    ec2 = getEC2Resource(awsAccessKey, awsSecretKey)
    return ec2.instances.all()

def getAllInstancesSnapshot(awsAccessKey, awsSecretKey):
    instancesObjectsList = getAllInstancesObjects(awsAccessKey, awsSecretKey)
    instances = {}
    for instance in instancesObjectsList:
        # Get name
        name = None
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                name = tag['Value']
        # Get memory
        ec2 = getEC2Client(awsAccessKey, awsSecretKey)
        # type = ec2.describe_instance_attribute(Attribute='instanceType', InstanceId=instance.id)
        details = ec2.describe_instance_types(InstanceTypes=[instance.instance_type])
        memory = details['InstanceTypes'][0]['MemoryInfo']['SizeInMiB']
        data = {'Name': name, 'Platform': instance.platform, 'Type': instance.instance_type,
                'Public IPv4': instance.public_ip_address, 'AMI': instance.image.id, 'State': instance.state,
                'CPU': instance.cpu_options, 'Memory': memory}
        instances.update({instance.id: data})
    return instances

def getInstance(instanceId, awsAccessKey, awsSecretKey):
    ec2 = boto3.resource('ec2', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
    return ec2.Instance(id=instanceId)

def getInstanceState(instanceId, awsAccessKey, awsSecretKey):
    instance = getInstance(instanceId, awsAccessKey, awsSecretKey)
    return instance.state  # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_InstanceState.html

def getInstanceStateCode(instanceId, awsAccessKey, awsSecretKey):
    state = getInstanceState(instanceId, awsAccessKey, awsSecretKey)
    return state['Code']

def isInstanceRunning(instanceId, awsAccessKey, awsSecretKey):
    code = getInstanceStateCode(instanceId, awsAccessKey, awsSecretKey)
    if code == 16:
        return True
    else:
        return False

def isInstanceStopped(instanceId, awsAccessKey, awsSecretKey):
    code = getInstanceStateCode(instanceId, awsAccessKey, awsSecretKey)
    if code == 80:
        return True
    else:
        return False

def getInstancePublicIPAddress(instanceId, awsAccessKey, awsSecretKey):
    instance = getInstance(instanceId, awsAccessKey, awsSecretKey)
    return instance.public_ip_address

def startInstace(instanceId, awsAccessKey, awsSecretKey):
    instance = getInstance(instanceId, awsAccessKey, awsSecretKey)
    response = instance.start()
    return response

def stopInstace(instanceId, awsAccessKey, awsSecretKey):
    instance = getInstance(instanceId, awsAccessKey, awsSecretKey)
    response = instance.stop()
    return response

def rebootInstace(instanceId, awsAccessKey, awsSecretKey):
    instance = getInstance(instanceId, awsAccessKey, awsSecretKey)
    response = instance.reboot()
    return response

def getAllRunningInstances(awsAccessKey, awsSecretKey):
    running = []
    instances = getAllInstancesObjects(awsAccessKey, awsSecretKey)
    for instance in instances:
        if instance.state['Name'] == 'running':
            running.append(instance)
    return running

def getAllStopedInstances(awsAccessKey, awsSecretKey):
    running = []
    instances = getAllInstancesObjects(awsAccessKey, awsSecretKey)
    for instance in instances:
        if instance.state['Name'] == 'stopped':
            running.append(instance)
    return running

def __getFileName(dateNow, folder):
    """This function creates a filename based on the current time (timestamp)."""
    path = '{}{}/'.format(__getRoot(), folder)
    filename = dateNow.strftime("%d.%m.%Y-%H.%M.%S.%f") + '.txt'
    return '{}{}'.format(path, filename)

def __getRoot():
    return '/bfi/'

def getFileNameOutput(dateNow):
    return __getFileName(dateNow, 'output')

def getFileNameInput(dateNow):
    return __getFileName(dateNow, 'input')

def getFileNameError():
    return '{}output/error.txt'.format(__getRoot())

def getCommand(message, dateNow, instanceId, pemFilePath, awsAccessKey, awsSecretKey):
    filenameOutput = getFileNameOutput(dateNow)  # '/bfi/output/fileOpen.txt'
    filenameInput = ''
    if message.getTask() == '':
        command = 'error'
    elif message.getTask() == 'tickers':
        command = '-tickers {}'.format(filenameOutput)
    elif message.getTask() == 'job':
        filenameInput = getFileNameInput(dateNow)
        filenameError = getFileNameError()
        payload = S3.downloadFromBucket(filepathBucket=message.getFilenameInput(), filepathLocal='/{}'.format(message.getFilenameInput()), read=True)
        __saveFile(payload, filenameInput, instanceId, pemFilePath, awsAccessKey, awsSecretKey)
        command = '-job {} {} {}'.format(filenameInput, filenameError, filenameOutput)
    else:
        command = '-{}'.format(message.getTask())
        args = message.getArguments()
        for arg in args:
            command = '{} {}'.format(command, arg)
    if command != 'error':
        command = './bfi_api ' + command  # Testing: './bfi_test '
    return command, filenameOutput, filenameInput

def getResponse(status, filenameOutput, instanceId, pemFilePath, awsAccessKey, awsSecretKey):
    if status != 0:
        return 'error'
    keysString = __loadFile(filenameOutput, instanceId, pemFilePath, awsAccessKey, awsSecretKey) # linea es un input de la "lista"
    keys = keysString.splitlines()
    content = {}
    counter = -1
    for key in keys:
        if key[:5] == __getRoot():
            value = __loadFile(key, instanceId, pemFilePath, awsAccessKey, awsSecretKey)
        else:
            value = key
            counter += 1
        if value == key and value != '':
            content.update({'message_{}'.format(counter): value})
        elif value != '':
            content.update({key: value})
    return json.dumps(content)

def __loadFile(filename, instanceId, pemFilePath, awsAccessKey, awsSecretKey):
    if filename[:5] == '/bfi/':
        file = SSH.readFileFromInstance(filename, instanceId, pemFilePath, awsAccessKey, awsSecretKey)
    else:
        file = ''
    return file

def __saveFile(data, filename, instanceId, pemFilePath, awsAccessKey, awsSecretKey):
    if filename[:5] == '/bfi/':
        SSH.writeFileStringToInstance(data, filename, instanceId, pemFilePath, awsAccessKey, awsSecretKey)

def __deleteFile(filename, instanceId, pemFilePath, awsAccessKey, awsSecretKey):
    if filename[:5] == '/bfi/':
        SSH.deleteFileFromInstance(filename, instanceId, pemFilePath, awsAccessKey, awsSecretKey)

def getInstanceId(message, dateNow):
    computerStatic2InstanceId = Configuration.get('COMPUTER_STATIC_2_INSTANCE_ID')
    computer2InstanceId = Configuration.get('COMPUTER_2_INSTANCE_ID')
    difficulty = message.getDifficulty()
    if difficulty == Enumerations.Difficulty.Difficulty_Low:
        return computerStatic2InstanceId
    elif difficulty == Enumerations.Difficulty.Difficulty_Standard:
        return computerStatic2InstanceId
    elif difficulty == Enumerations.Difficulty.Difficulty_Static:
        return computerStatic2InstanceId
    elif difficulty == Enumerations.Difficulty.Difficulty_High:
        return computer2InstanceId
    else:
        return computerStatic2InstanceId

def downloadPemFile(instanceId, awsAccessKey='', awsSecretKey='', tmp=False):
    filepathLocal = 'computer_key.pem'
    filepathBucket = 'keys/{}'.format(filepathLocal)
    if tmp:
        filepathLocal = '{}{}'.format('/tmp/', filepathLocal)
    bucket = 'bfi-cfg'
    if os.path.isfile(filepathLocal):
        os.remove(filepathLocal)
    S3.downloadFromBucket(filepathBucket, filepathLocal, bucket, awsAccessKey, awsSecretKey)
    if not os.path.isfile(filepathLocal):
        time.sleep(3)
        S3.downloadFromBucket(filepathBucket, filepathLocal, bucket, awsAccessKey, awsSecretKey)
        time.sleep(3)
    return filepathLocal

if __name__ == '__main__':
    awsAccessKey = Configuration.get('AWS_ACCESS_KEY')
    awsSecretKey = Configuration.get('AWS_SECRET_KEY')
    instanceId = Configuration.get('COMPUTER_STATIC_2_INSTANCE_ID')
    print(instanceId)
    running = isInstanceRunning(instanceId, awsAccessKey, awsSecretKey)
    print(running)
    stopped = isInstanceStopped(instanceId, awsAccessKey, awsSecretKey)
    print(stopped)
    pemFilePath = downloadPemFile(instanceId, awsAccessKey, awsSecretKey, tmp=False)
    print(pemFilePath)
    response = getResponse(0, '/bfi/output/fileOpen.txt', instanceId, pemFilePath, awsAccessKey, awsSecretKey)
    print(response)