import boto3
import json
import os

ec2 = boto3.client('ec2', region_name='us-west-2')
#ec2 = session.client('ec2')
arry = []
for i in range(10):
    response = ec2.allocate_address(
        Domain='vpc'
    )
    print(response['AllocationId'])
    print(response['PublicIp'])

    arry.append(response['AllocationId'])

   # input('proceed ??')


print(arry)