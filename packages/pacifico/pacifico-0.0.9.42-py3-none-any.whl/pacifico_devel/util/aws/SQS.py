"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import boto3
from ..cfg import Configuration

def getSqsClient(awsAccessKey='', awsSecretKey=''):
    if (awsAccessKey != '' and awsSecretKey != ''):
        sqs = boto3.client('sqs', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
    else:
        awsAccessKey = Configuration.get('AWS_ACCESS_KEY')
        awsSecretKey = Configuration.get('AWS_SECRET_KEY')
        sqs = boto3.client('sqs', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
    return sqs

def getQueueURL(queueName, awsAccessKey='', awsSecretKey=''):
    sqs = getSqsClient(awsAccessKey, awsSecretKey)
    response = sqs.get_queue_url(QueueName=queueName)
    return response['QueueUrl']

def publish(queueName, message, awsAccessKey='', awsSecretKey=''):
    sqs = getSqsClient(awsAccessKey, awsSecretKey)
    queue_url = getQueueURL(queueName, awsAccessKey, awsSecretKey)
    last = queueName.split('.')[-1]
    if last == 'fifo':
        # Send message to FIFO SQS queue
        response = sqs.send_message(
            MessageGroupId='Production',
            QueueUrl=queue_url,
            MessageBody=message)
    else:
        # Send message to SQS queue
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message)
    return response['MessageId']

def receive(queueName, awsAccessKey='', awsSecretKey=''):
    sqs = getSqsClient(awsAccessKey, awsSecretKey)
    queue_url = getQueueURL(queueName, awsAccessKey, awsSecretKey)
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=5,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    for message in response['Messages']:
        print(message)
    receipt_handle = message['ReceiptHandle']
    print(receipt_handle)

if __name__ == '__main__':
    from util.cfg import Configuration

    awsAccessKey = Configuration.get('AWS_ACCESS_KEY')
    awsSecretKey = Configuration.get('AWS_SECRET_KEY')
    queueName = 'gatekeeper-computer_bfi'
    message = publish(queueName, 'TesteR', awsAccessKey, awsSecretKey)
    print(message)
    #received = receiveMessages(queueName, awsAccessKey, awsSecretKey)
    #print(received)