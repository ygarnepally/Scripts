import json
import os
import boto3
import sys
from colorama import Fore, Back, Style

region = 'us-west-2'
ec2 = boto3.client('ec2', region_name=region)
rds = boto3.client('rds', region_name=region)
ecs = boto3.client('ecs', region_name=region)
asg = boto3.client('autoscaling', region_name=region)
cf = boto3.client('cloudformation', region_name=region)


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
    #if 'Tags' in instancedata:
    tags = [tag['Value'] for tag in instancedata['Tags'] if tag['Key'].lower() == tagkey.lower()]
    #print(tags)
    if len(tags) > 0:
        output = ''.join(tags)
    return output


def get_all_instances(region=None):
    rds = boto3.client('rds', region_name=region)

    all_instances = []
    desc_rds = rds.describe_db_instances(
        MaxRecords = 80 
        )
    #print(desc_asg)

    next_token = True
    while next_token != False:
        #print(len(clusters['clusterArns']))
        # for reservation in desc_rds['Reservations']:
        #     print('total instances\t' + str(len(all_instances)))
        #     for instance in reservation['Instances']:
    
        all_instances.extend(desc_rds['DBInstances'])
        print('total instances\t' + str(len(all_instances)))
        if 'Marker' in desc_rds:
            next_token = True
            desc_rds = rds.describe_db_instances(
                MaxRecords = 80,
                Marker = desc_rds['Marker']
                )
        else:
            next_token = False

    return all_instances

def list_tags(region=None, db_arn=None):
    rds = boto3.client('rds', region_name=region)
    tags = rds.list_tags_for_resource(
        ResourceName=db_arn
        )
    # print(tags)
    return tags


regions = ["us-east-1", "us-west-2"]
#print(Style.RESET_ALL)

for region in regions:
    print('Region:---------------\t\t' + region)
    all_db_instances = get_all_instances(region=region)
    # print('total instances\t' + str(len(all_instances)))
    print(len(all_db_instances))


    rds = boto3.client('rds', region_name=region)
    for instance in all_db_instances:
        try:
        # if 0 == 0:
            #input('proceed ???')
            #print(instance)
            instance_id = instance['DBInstanceIdentifier']
            #print(instance_id)
            arn = instance['DBInstanceArn']
            rds_tags = list_tags(region=region, db_arn=arn)

            #print(rds_tags)

            #instance_name = get_key_value(instancedata=instance, tagkey='Name')

            envname = get_env_name(instance_id)
            #print(envname)

            #pace_tag = get_key_value(instancedata=instance, tagkey='pace_env')
            pace_tag = [tag for tag in rds_tags['TagList'] if tag['Key'] == 'pace_env']
            #print(pace_tag)
            if len(pace_tag) > 0:

                print(region + '=>\tinstance:\t' + instance_id + '\t\talready has pace_env tag \t' + pace_tag[0]['Value'])
            else:
                    
                print(Fore.GREEN + ' => ' + instance_id + ' => ' + envname )
                print(Style.RESET_ALL)
            # #if envname == 'NONE':
            # print(Fore.GREEN + instance_name + ' => ' + envname)
            # print(Style.RESET_ALL)   

            # pace_tag = [tag['Value'] for tag in group['Tags'] if tag['Key'] == 'pace_env']
              
            # if envname != 'NONE':     
            #     if pace_tag == 'NONE':
                    
                #print('adding tag to instance:\t' + instance_id)
                # add_tag = ec2.create_tags(
                #     Resources=[ instance_id ],
                #     Tags=[{
                #             'Key': 'pace_env',
                #             'Value': envname
                #         }]
                #     )
                # print(arn)
                # print(envname)
                if envname != 'NONE':
                    resp_tags = rds.add_tags_to_resource(
                        ResourceName=arn,
                        Tags=[
                            {
                                'Key': 'pace_env',
                                'Value': envname
                            },
                        ])
                    # print(resp_tags)
                    print(Fore.GREEN + region + '=>\t*Tag has been updated to instance:\t' + instance_id)
                    print(Style.RESET_ALL)
                else:
                    print(Style.RESET_ALL + '\t* No Tag NONE:\t' + instance_id) 
        
#                 input('?????????????????????????')            
            # else:
            #     print(Fore.RED + '\t*Skipping asg as no environment found:\t' + instance_id)
            #     print(Style.RESET_ALL)


        except Exception as e:
            print(Fore.RED + str(e))
            print('Exception.............................................................')

        print(Style.RESET_ALL)

