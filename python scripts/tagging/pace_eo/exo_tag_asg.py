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

all_asgs = []

desc_asg = asg.describe_auto_scaling_groups(
    MaxRecords = 5
    )
#cluster_arns = clusters['clusterArns']

next_token = True
while next_token != False:
    #print(len(clusters['clusterArns']))
    for group in desc_asg['AutoScalingGroups']:
        all_asgs.append(group)

    if 'NextToken' in desc_asg:
        next_token = True
        desc_asg = asg.describe_auto_scaling_groups(
            NextToken = desc_asg['NextToken'],
            MaxRecords = 5
            )
    else:
        next_token = False

    #input('?????')
    #print(len(all_asgs))



print(len(all_asgs))
for record in all_asgs:
    #print(record)
    try:
    #if 0 == 0:
        #print(record)
        #print(record['Tags'])
        bapp_tag = [tag['Value'] for tag in record['Tags'] if tag['Key'] == 'bapp_id']
        bapp_tag = ''.join(bapp_tag)
        print(bapp_tag)
        #matched_record = ''
        #input('?????')
        if len(bapp_tag) > 0:
            for item in json_records:
                if item['bapp_id'] == bapp_tag:
                    matched_record = item

                    print(matched_record)


                    print('adding tag to asg:\t' + record['AutoScalingGroupName'])
                    add_asg_tag_resp = asg.create_or_update_tags(
                        Tags=[{
                                'ResourceId': record['AutoScalingGroupName'],
                                'ResourceType': 'auto-scaling-group',
                                'Key': 'executiveowner',
                                'Value': matched_record['executiveowner'],
                                'PropagateAtLaunch': True
                            },]
                    )
                    #print(add_asg_tag_resp)

                    print('adding tags to all asg instances')

                    desc_asg = asg.describe_auto_scaling_groups(
                        AutoScalingGroupNames=[
                            record['AutoScalingGroupName']
                        ]
                    )
                    if len(desc_asg['AutoScalingGroups'][0]['Instances']) > 0:
                        for instance in desc_asg['AutoScalingGroups'][0]['Instances']:
                            instance_id = instance['InstanceId']

                            print('\t\tAdding tag to instance:\t' + instance_id)
                            create_tag_resp = ec2.create_tags(
                                Resources=[ instance_id ],
                                Tags=[
                                    {
                                        'Key': 'executiveowner',
                                        'Value': matched_record['executiveowner']
                                    },
                                ]
                            )
                            #print(create_tag_resp)
                        # else:
                        #     print('no more iteration available in list')

        else:
            print('no bapp_tag found\t' + record['AutoScalingGroupName'])
    except Exception as e:
        print('-------------------------------------------------------------')
        print(e)    

