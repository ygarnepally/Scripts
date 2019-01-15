import json
import os
import boto3
import sys
from colorama import Fore, Back, Style

region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)
ecs = boto3.client('ecs', region_name=region)
asg = boto3.client('autoscaling', region_name=region)
cf = boto3.client('cloudformation', region_name=region)


def get_env_name(asg_name):
    env_name = ''
    if '-prod' in asg_name:
        env_name = 'prod'
    elif '-stage' in asg_name:
        env_name = 'stage'
    elif '-latest' in asg_name:
        env_name = 'latest'
    elif '-load' in asg_name:
        env_name = 'load'
    elif '-shadow' in asg_name:
        env_name = 'shadow'
    elif '-training' in asg_name:
        env_name = 'training'
    elif '-train' in asg_name:
        env_name = 'training'
    else:
        env_name = 'NONE'

    return env_name

all_asg = []
desc_asg = asg.describe_auto_scaling_groups()
#print(desc_asg)

next_token = True
while next_token != False:
    #print(len(clusters['clusterArns']))
    for group in desc_asg['AutoScalingGroups']:
        all_asg.append(group)

    if 'NextToken' in desc_asg:
        next_token = True
        desc_asg = asg.describe_auto_scaling_groups(
            NextToken = desc_asg['NextToken']
            )
    else:
        next_token = False


#print(Style.RESET_ALL)
print('total asgs\t' + str(len(all_asg)))
#input('proceed/....................??')
for group in all_asg:
    try:
        input('proceed ???')
        
        asg_name = group['AutoScalingGroupName']
        envname = get_env_name(asg_name)
        
        #if envname == 'NONE':
        print(Fore.GREEN + asg_name + ' => ' + envname)
        print(Style.RESET_ALL)   

        pace_tag = [tag['Value'] for tag in group['Tags'] if tag['Key'] == 'pace_env']
          
        if envname != 'NONE':     
            if len(pace_tag) == 0:
                
                print('adding tag to asg:\t' + asg_name)
                add_asg_tag_resp = asg.create_or_update_tags(
                    Tags=[{
                            'ResourceId': asg_name,
                            'ResourceType': 'auto-scaling-group',
                            'Key': 'pace_env',
                            'Value': envname,
                            'PropagateAtLaunch': True
                        },]
                )
                print(Fore.GREEN + '\t*Tag has been updated to asg:\t' + asg_name)
                print(Style.RESET_ALL)
            else:
                print(Style.RESET_ALL + '\t*Tag already exist:\t' + asg_name) 
                
        else:
            print(Fore.RED + '\t*Skipping asg as no environment found:\t' + asg_name)
            print(Style.RESET_ALL)


        if envname != 'NONE':

            #tagging ec2 instances under autoscaling
            asg_instances = [instance['InstanceId'] for instance in group['Instances']]

                #print(asg_instances)

            for instance in asg_instances:
                instance_tags = ec2.describe_tags(
                    Filters=[{
                        'Name': 'resource-id',
                        'Values': [ instance ]
                    }]
                    )
                instance_tags = [tag for tag in instance_tags['Tags'] if tag['Key'] == 'pace_env']
                if len(instance_tags) == 0:
                    add_tag = ec2.create_tags(
                        Resources=[ instance ],
                        Tags=[{
                            'Key': 'pace_env',
                            'Value': envname
                        }]
                        )

                    print(Fore.GREEN + '\t\t* Tag has been updated to instance:\t' + instance)
                    print(Style.RESET_ALL)
                else:
                    print(Style.RESET_ALL + '\t\t* Tag already exist.....:\t' + instance)
                 
#             #input('proceed with instance tagging//...???')   

    except Exception as e:
        print(Fore.RED + str(e))

    print(Style.RESET_ALL)

