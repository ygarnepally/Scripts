
import boto3
import json
import os
import datetime
import gspread

#from oauth2client.service_account import ServiceAccountCredentials

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


current_time = datetime.datetime.now().isoformat()
file_name = '/tmp/ECS_HOST_Report_' + region + '_' + str(current_time) + '.csv'

f = open(file_name, 'w+')
f.write("ClusterName,ECSInstanceCount,TotalRunningTasks,TotalRunningServices,InstanceType,servicetasks_count,servicename,task_memory,task_cpu")
f.write('\n')
#filevar = "ClusterName,InstanceId,RunningTasks,InstanceType,bapp_id,environment,executiveowner" +\n"
#clustername = ''
#InstanceId = ''
#RunningTasks = ''
#InstanceType = ''
#TotalECSInstances = 0
#bapp_id = ''
#environment = ''
#executiveowner = ''



for cluster in clusters:
    try:
        clustername = cluster.split('/')[-1]

        desc_cluster = ecs.describe_clusters(
            clusters=[ clustername ],
        )
        desc_cluster = desc_cluster['clusters'][0]
        ecsinstances = desc_cluster['registeredContainerInstancesCount']
        cluster_status = desc_cluster['status']
        RunningTasks = desc_cluster['runningTasksCount']
        ActiveService = desc_cluster['activeServicesCount']


        if ecsinstances > 0:
            cluster_instances = ecs.list_container_instances(
                cluster = cluster
            )
            ecs_instance_desc = ecs.describe_container_instances(
                cluster = cluster,
                containerInstances = [
                    cluster_instances['containerInstanceArns'][0]
            ])

            InstanceId = ecs_instance_desc['containerInstances'][0]['ec2InstanceId']

            desc_instance = ec2.describe_instances(
                InstanceIds=[
                    InstanceId
                ])
            InstanceType = desc_instance['Reservations'][0]['Instances'][0]['InstanceType']

            service_list = ecs.list_services(
                cluster = cluster,
            )
            for service in service_list['serviceArns']:
                servicename = service.split('/')[-1]


                desc_service = ecs.describe_services(
                    cluster = cluster,
                    services = [ service ]
                )
                servicetasks_count = str(desc_service['services'][0]['runningCount'])
                task_def = desc_service['services'][0]['taskDefinition']
                #desc_task = ecs.describe_tasks(
                #    cluster = cluster,
                #    tasks = [ ecs_tasks['taskArns'][0] ]
                #)
                desc_taskdef = ecs.describe_task_definition(
                    taskDefinition = task_def
                )
                #task_memory = desc_taskdef['taskDefinition']['containerDefinitions'][0]['memoryReservation']
                task_memory = desc_taskdef['taskDefinition']['containerDefinitions'][0]['memory']
                task_cpu = desc_taskdef['taskDefinition']['containerDefinitions'][0]['cpu']

                print(clustername + '\t' + str(ecsinstances) + '\t' + str(RunningTasks) + '\t' + str(ActiveService) + '\t' + InstanceType + '\t' + str(servicetasks_count) + '\t' + servicename + '\t' + str(task_memory) + '\t' + str(task_cpu))
                #input('proceed..?')
                f.write(clustername + ',' + str(ecsinstances) + ',' + str(RunningTasks) + ',' + str(ActiveService) + ',' + InstanceType + ',' + str(servicetasks_count) + ',' + servicename + ',' + str(task_memory) + ',' + str(task_cpu) + '\n')
                #filevar += clustername + ',' + InstanceId + ',' + str(RunningTasks) + ',' + InstanceType + ',' + bapp_id + ',' + environment + ',' + executiveowner +'\n'


        else:
            InstanceId = 'NA'
            ecsinstances = 'NA'
            RunningTasks = 'NA'
            InstanceType = 'NA'
            ActiveService = 'NA'
            InstanceType = 'NA'
            servicetasks_count = 'NA'
            servicename = 'NA'
            task_memory = 'NA'
            task_cpu = 'NA'


            #print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            print(clustername + '\t' + str(ecsinstances) + '\t' + str(RunningTasks) + '\t' + str(ActiveService) + '\t' + InstanceType + '\t' + servicetasks_count + '\t' + servicename + '\t' + task_memory + '\t' + task_cpu)
            # input('proceed..?')
            f.write(clustername + ',' + ecsinstances + ',' + str(RunningTasks) + ',' + ActiveService + ',' + InstanceType + ',' + servicetasks_count + ',' + servicename + ',' + task_memory + ',' + task_cpu + '\n')

            #filevar += clustername + ',' + InstanceId + ',' + str(RunningTasks) + ',' + InstanceType + ',' + bapp_id + ',' + environment + ',' + executiveowner + '\n'
    except Exception as e:
        print('-------------------------------------------------------------')
        print(clustername + '----------------')
        print(e)

f.close()

#print('TotalECSInstances:\t' + str(TotalECSInstances))


"""
scope=[
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name('pace-cred.json', scope)
gs = gspread.authorize(credentials)
"""
#-----------------------------
#gsheet = gs.open("testawsdoc_for_inventory")
#wsheet = gsheet.worksheet("Sheet1")

#gs.import_csv('1oWVOfyn0w8WBcSIBZCLbGxfcv2NbRTwT9dI_coZTI6Q', filevar)
#----------------------------
#gs.import_csv('1ssr7vYRv3WGsp02bp6Fs1qIyiooLluHTAS_zqXPs_eE', filevar)





