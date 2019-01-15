
import boto3
import json
import os

ec2 = boto3.client('ec2', region_name='us-west-2')

ips = ['eipalloc-d97e85e5', 'eipalloc-6c7f8450', 'eipalloc-04728938', 'eipalloc-317c870d', 'eipalloc-da7e85e6', 'eipalloc-327c870e', 'eipalloc-d87388e4', 'eipalloc-d17289ed', 'eipalloc-2c7c8710', 'eipalloc-90718aac']


for ip in ips:
	response = ec2.release_address(
	    AllocationId= ip
	)

	print(response)