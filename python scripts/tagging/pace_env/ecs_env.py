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

all_clusters = []

clusters = ecs.list_clusters()
cluster_arns = clusters['clusterArns']

next_token = True
while next_token != False:
    print(len(clusters['clusterArns']))
    for cluster in clusters['clusterArns']:
        all_clusters.append(cluster)

    if 'nextToken' in clusters:
        next_token = True
        clusters = ecs.list_clusters(
            nextToken = clusters['nextToken']
            )
    else:
        next_token = False


#print(Style.RESET_ALL)

for clusterarn in all_clusters:
    try:
        #input('proceed ???')
        cluster_name = clusterarn.split('/')[-1]
        instances = ecs.list_container_instances(
            cluster=clusterarn
        )

        #print(cluster_name)
        ec2_instances = []
        if len(instances['containerInstanceArns']) > 0:
            desc = ecs.describe_container_instances(
                cluster=clusterarn,
                containerInstances=instances['containerInstanceArns']
            )
            for instance in desc['containerInstances']:
                ec2_instances.append(instance['ec2InstanceId'])

            #print('cluster. instances............')
            #print(ec2_instances)
            tags = ec2.describe_tags(
                Filters=[
                    {
                        'Name': 'resource-id',
                        'Values': [ ec2_instances[0] ]
                    }])
            
            #print(tags)
            asg_name = [ asg['Value'] for asg in tags['Tags'] if asg['Key'] == 'aws:autoscaling:groupName']
            asg_name = ''.join(asg_name)        
            
            #print('asg name ------------- ' + asg_name)

            desc_asg = asg.describe_auto_scaling_groups(
                AutoScalingGroupNames=[asg_name]
            )



            pace_tag = [tag['Value'] for tag in desc_asg['AutoScalingGroups'][0]['Tags'] if tag['Key'] == 'pace_env']
            

            env_name = cluster_name.split('-')[-1]
            print(Fore.GREEN + cluster_name + ' => ' + env_name)
            print(Style.RESET_ALL)
            
            if len(pace_tag) == 0:
                

                #print('adding tag to asg:\t' + asg_name)
                add_asg_tag_resp = asg.create_or_update_tags(
                    Tags=[{
                            'ResourceId': asg_name,
                            'ResourceType': 'auto-scaling-group',
                            'Key': 'pace_env',
                            'Value': env_name,
                            'PropagateAtLaunch': True
                        },]
                )
                print(Fore.GREEN + '\t*Tag has been updated to asg[' + cluster_name + ']:\t' + asg_name)
                print(Style.RESET_ALL)
            else:
                print(Style.RESET_ALL + '\t* Tag already exist:\t' + asg_name) 
            

            #tagging ec2 instances under autoscaling
            asg_instances = [instance['InstanceId'] for instance in desc_asg['AutoScalingGroups'][0]['Instances']]

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
                            'Value': env_name
                        }]
                        )

                    print(Fore.GREEN + '\t\t* Tag has been updated to instance:\t' + instance)
                    print(Style.RESET_ALL)
                else:
                    print(Style.RESET_ALL + '\t\t* Tag already exist.....:\t' + instance)
                 
                #input('proceed with instance tagging//...???')   

    except Exception as e:
        print(Fore.RED + str(e))

    print(Style.RESET_ALL)

