import json
import os
import boto3
import sys

region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)
ecs = boto3.client('ecs', region_name=region)
asg = boto3.client('autoscaling', region_name=region)
cf = boto3.client('cloudformation', region_name=region)

json_file_path = input("Enter the path of your json file: ")
#json_file_path = '/home/ttn/Documents/ysh/scripts/convertcsv.json'


json_records = json.load(open(json_file_path))

for record in json_records:
    print(record)
    try:

        print('adding tag to asg:\t' + record['asg'])
        add_asg_tag_resp = asg.create_or_update_tags(
            Tags=[{
                    'ResourceId': record['asg'],
                    'ResourceType': 'auto-scaling-group',
                    'Key': record['Key'],
                    'Value': record['Value'],
                    'PropagateAtLaunch': True
                },]
        )
        #print(add_asg_tag_resp)

        print('adding tags to all asg instances')

        desc_asg = asg.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
                record['asg']
            ]
        )
        for instance in desc_asg['AutoScalingGroups'][0]['Instances']:
            instance_id = instance['InstanceId']

            print('\t\tAdding tag to instance:\t' + instance_id)
            create_tag_resp = ec2.create_tags(
                Resources=[ instance_id ],
                Tags=[
                    {
                        'Key': record['Key'],
                        'Value': record['Value']
                    },
                ]
            )
            #print(create_tag_resp)
        else:
            print('no more iteration available in list')

    except Exception as e:
        print('-------------------------------------------------------------')
        print(e)    

