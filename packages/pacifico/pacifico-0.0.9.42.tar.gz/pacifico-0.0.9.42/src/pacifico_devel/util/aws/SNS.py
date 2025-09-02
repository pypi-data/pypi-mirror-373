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

def getSnsClient(awsAccessKey='', awsSecretKey=''):
    if (awsAccessKey != '' and awsSecretKey != ''):
        sns = boto3.client('sns', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
    else:
        awsAccessKey = Configuration.get('AWS_ACCESS_KEY')
        awsSecretKey = Configuration.get('AWS_SECRET_KEY')
        sns = boto3.client('sns', aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
    return sns

def publish(message, topicARN, awsAccessKey='', awsSecretKey=''):
    sns = getSnsClient(awsAccessKey, awsSecretKey)
    response = sns.publish(TopicArn=topicARN, Message=message, MessageGroupId='Production')
    return response['MessageId']

if __name__ == '__main__':
    from util.cfg import Configuration

    awsAccessKey = Configuration.get('awsAccessKey', '')
    awsSecretKey = Configuration.get('awsSecretKey', '')
    topicARN = 'arn:aws:sns:us-west-2:947040342882:bot-gatekeeper.fifo'
    message = publish('testeddddddddddddd', topicARN, awsAccessKey, awsSecretKey)
    print(message)