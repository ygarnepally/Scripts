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


file = open('no-asg-tags.csv', 'w+')
file.write("InstanceId,bapp_id,pace_tag,instance_type,region")
file.write("\n")


def get_env_name(instance_name):
    
    env_name = ''
    if '-prod' in instance_name:
        env_name = 'prod'
    elif '-stage' in instance_name:
        env_name = 'stage'
    elif '-latest' in instance_name:
        env_name = 'latest'
    elif '-load' in instance_name:
        env_name = 'load'
    elif '-lt' in instance_name:
        env_name = 'load'    
    elif '-shadow' in instance_name:
        env_name = 'shadow'
    elif '-training' in instance_name:
        env_name = 'training'
    elif '-train' in instance_name:
        env_name = 'training'
    else:
        env_name = 'NONE'

    return env_name

def get_key_value(instancedata, tagkey):
    output = 'NONE'
    if 'Tags' in instancedata:
        tags = [tag['Value'] for tag in instancedata['Tags'] if tag['Key'].lower() == tagkey.lower()]
        #print(tags)
        if len(tags) > 0:
            output = ''.join(tags)
    return output


all_instances = []
desc_ec2 = ec2.describe_instances()
#print(desc_asg)

next_token = True
while next_token != False:
    #print(len(clusters['clusterArns']))
    for reservation in desc_ec2['Reservations']:
        for instance in reservation['Instances']:
            all_instances.append(instance)

    if 'NextToken' in desc_ec2:
        next_token = True
        desc_ec2 = asg.describe_instances(
            NextToken = desc_ec2['NextToken']
            )
    else:
        next_token = False


#print(Style.RESET_ALL)
print('total instances\t' + str(len(all_instances)))
input('proceed/....................??')
no_asg_count = 0
for instance in all_instances:
    try:
    
        #input('proceed ???')
        #print(instance)
        asg_tag = get_key_value(instancedata=instance, tagkey='aws:autoscaling:groupName')
        
        if asg_tag == 'NONE':
            no_asg_count += 1
            instance_id = instance['InstanceId']
            instance_name = get_key_value(instancedata=instance, tagkey='Name')
            instance_type = instance['InstanceType']
            envname = get_env_name(instance_name)
            
            pace_tag = get_key_value(instancedata=instance, tagkey='pace_env')
            bapp_id = get_key_value(instancedata=instance, tagkey='bapp_id')

            print(instance_id + '\t' + bapp_id + '\t' + pace_tag + '\t' + instance_type + '\t' + region )
            file.write(instance_id + ',' + bapp_id + ',' + pace_tag + ',' + instance_type + ',' + region + "\n")
                
        # else:
        #     print(Fore.RED + '\t*Skipping instance ,not a part of autoscaling:\t' + instance_id)
        #     print(Style.RESET_ALL)


    except Exception as e:
        print(Fore.RED + str(e))

    print(Style.RESET_ALL)

file.close()
print('no asg instances:\t' + str(no_asg_count))
