
import boto3
import json
import os
import datetime
import gspread

from oauth2client.service_account import ServiceAccountCredentials

region = input('RegionName:\t')


ecs = boto3.client('ecs', region_name=region)
ec2 = boto3.client('ec2', region_name=region)
next_token = True
clusters = []
all_clusters = ecs.list_clusters()

while next_token != False:
    print(len(all_clusters['clusterArns']))
    for cluster in all_clusters['clusterArns']:
        clusters.append(cluster)

    if 'nextToken' in all_clusters:
        next_token = True
        all_clusters = ecs.list_clusters(
            nextToken = all_clusters['nextToken']
            )
    else:
        next_token = False



#print(clusters)
#print(len(clusters))
current_time = datetime.datetime.now().isoformat()
file_name = 'ECS_HOST_Report_' + region + '_' + str(current_time) + '.csv'

f = open(file_name, 'w+')
f.write("ClusterName,InstanceId,RunningTasks,InstanceType,bapp_id,environment,executiveowner")
f.write('\n')
filevar = "ClusterName,InstanceId,RunningTasks,InstanceType,bapp_id,environment,executiveowner" + "\n"
clustername = ''
InstanceId = ''
RunningTasks = ''
InstanceType = ''
TotalECSInstances = 0
bapp_id = ''
environment = ''
executiveowner = ''



for cluster in clusters:
    clustername = cluster.split('/')[-1]
    cluster_instances = ecs.list_container_instances(
        cluster = cluster
        )
    TotalECSInstances += len(cluster_instances['containerInstanceArns'])
    if len(cluster_instances['containerInstanceArns']) > 0:
        for ecs_instance in cluster_instances['containerInstanceArns']:
            ecs_instance_desc = ecs.describe_container_instances(
                cluster = cluster,
                containerInstances = [
                    ecs_instance
                ])
            InstanceId = ecs_instance_desc['containerInstances'][0]['ec2InstanceId']
            RunningTasks = ecs_instance_desc['containerInstances'][0]['runningTasksCount']
            for attribute in ecs_instance_desc['containerInstances'][0]['attributes']:
                if attribute['name'] == 'ecs.instance-type':
                    InstanceType = attribute['value']

            ec2_tags = ec2.describe_tags(
                Filters = [{
                    'Name': 'resource-id',
                    'Values': [ InstanceId ]
                }
                ])
            print(ec2_tags)
            for tag in ec2_tags['Tags']:
                print('\n')
                print(tag)
                print(tag['Key'])
                if tag['Key'] == "bapp_id":
                    print('yessssssss')
                    print(tag['Key'])

                    bapp_id = tag['Value']
                    break
                
                else:
                    bapp_id = 'NA'
                    print('Noooo')

            print(ec2_tags)
            for tag in ec2_tags['Tags']:
                print('\n')
                print(tag)
                print(tag['Key'])
                if tag['Key'] == "environment":
                    print('yessssssss')
                    print(tag['Key'])

                    environment = tag['Value']
                    break
                
                else:
                    environment = 'NA'
                    print('Noooo')

            print(ec2_tags)
            for tag in ec2_tags['Tags']:
                print('\n')
                print(tag)
                print(tag['Key'])
                if tag['Key'] == "executiveowner":
                    print('yessssssss')
                    print(tag['Key'])

                    executiveowner = tag['Value']
                    break
                
                else:
                    executiveowner = 'NA'
                    print('Noooo')


                    
                    #print('\n\n')
                    #print(bapp_id)


            #input('proceed??')
            print(clustername + '.......' + InstanceId + '........' + str(RunningTasks) + '.......' + InstanceType + '...........' + bapp_id + '.........' + environment + '.........' + executiveowner)
            #input('proceed..?')
            f.write(clustername + ',' + InstanceId + ',' + str(RunningTasks) + ',' + InstanceType + ',' + bapp_id + ',' + environment + ',' + executiveowner +'\n')
            filevar += clustername + ',' + InstanceId + ',' + str(RunningTasks) + ',' + InstanceType + ',' + bapp_id + ',' + environment + ',' + executiveowner +'\n'


    else:
        InstanceId = 'NA'
        RunningTasks = 'NA'
        InstanceType = 'NA'
        bapp_id = 'NA'
        environment = 'NA'
        executiveowner = 'NA'

        #print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

        print(clustername + '.......' + InstanceId + '........' + str(RunningTasks) + '.......' + InstanceType + '.......' + bapp_id + '.......' + environment + '.........' + executiveowner)
        f.write(clustername + ',' + InstanceId + ',' + str(RunningTasks) + ',' + InstanceType + ',' + bapp_id + ',' + environment + ',' + executiveowner + '\n')

        filevar += clustername + ',' + InstanceId + ',' + str(RunningTasks) + ',' + InstanceType + ',' + bapp_id + ',' + environment + ',' + executiveowner + '\n' 

f.close()
print('TotalECSInstances:\t' + str(TotalECSInstances))

scope=[
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name('pace-cred.json', scope)
gs = gspread.authorize(credentials)

#gsheet = gs.open("testawsdoc_for_inventory")
#wsheet = gsheet.worksheet("Sheet1")

#gs.import_csv('1oWVOfyn0w8WBcSIBZCLbGxfcv2NbRTwT9dI_coZTI6Q', filevar)

gs.import_csv('1ssr7vYRv3WGsp02bp6Fs1qIyiooLluHTAS_zqXPs_eE', filevar)





