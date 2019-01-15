
import boto3
import json
import os
import datetime
import gspread
import traceback
#from oauth2client.service_account import ServiceAccountCredentials

region = input('RegionName:\t')

ecs = boto3.client('ecs', region_name=region)
ec2 = boto3.client('ec2', region_name=region)
asg = boto3.client('autoscaling', region_name=region)
aasg = boto3.client('application-autoscaling', region_name=region)


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
file_name = 'ECS_HOST_Report_' + region + '_' + str(current_time) + '.csv'

f = open(file_name, 'w+')
#f.write("ClusterName,Environment,ECSInstanceCount,TotalRunningTasks,TotalRunningServices,InstanceType,servicetasks_count,servicename,task_memory,task_cpu")
f.write("cluster,env,i_type,asg_min,asg_max,asg_des,#ser,ser_name,#tasks,ser_min,ser_max,ser_des,cpu,mem")
f.write('\n')

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
            Tags = desc_instance['Reservations'][0]['Instances'][0]['Tags']

            #print(Tags)
            asg_name = [ asg['Value'] for asg in Tags if asg['Key'] == 'aws:autoscaling:groupName']
            asg_name = ''.join(asg_name)
            

            desc_asg = asg.describe_auto_scaling_groups(
                AutoScalingGroupNames=[asg_name]
                )
            asg_minsize = desc_asg['AutoScalingGroups'][0]['MinSize']
            asg_maxsize = desc_asg['AutoScalingGroups'][0]['MaxSize']
            #print(desc_asg)
            env_tag = [tag['Value'] for tag in desc_asg['AutoScalingGroups'][0]['Tags'] if tag['Key'] == 'environment']
            env_tag = ''.join(env_tag)
            
            #print(asg_name)
            #input('process?????????????????????')
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

                #print(clustername)
                desc_aasg = aasg.describe_scalable_targets(
                    ServiceNamespace='ecs',
                    ResourceIds=[ 'service/' + clustername + '/' +  servicename ]
                    )

                #print(desc_aasg)
                if len(desc_aasg['ScalableTargets']) > 0:
                    service_min=desc_aasg['ScalableTargets'][0]['MinCapacity']
                    service_max=desc_aasg['ScalableTargets'][0]['MaxCapacity']
                else:
                    service_min = 'NA'
                    service_max = 'NA'


                



                print(clustername + '\t' + env_tag + '\t' + str(asg_minsize) + '\t' + str(asg_maxsize) + '\t' + str(ecsinstances) + '\t' + str(service_min) + '\t' + str(service_max) + '\t' + str(RunningTasks) + '\t' + str(ActiveService) + '\t' + InstanceType + '\t' + str(servicetasks_count) + '\t' + servicename + '\t' + str(task_memory) + '\t' + str(task_cpu))
                #input('proceed..?')
                f.write(clustername + ',' + env_tag + ',' + InstanceType + ',' + str(asg_minsize) + ',' + str(asg_maxsize) + ',' + str(ecsinstances) + ',' + str(ActiveService) + ',' + str(servicename) + ',' + str(RunningTasks) + ',' + str(service_min) + ',' + str(service_max) + ',' + str(servicetasks_count) + ',' + str(task_memory) + ',' + str(task_cpu) + '\n')
                # f.write(clustername + ',' + env_tag + ',' + str(asg_minsize) + ',' + str(asg_maxsize) + ',' + str(ecsinstances) + ',' + str(service_min) + ',' + str(service_max) + ',' + str(RunningTasks) + ',' + str(ActiveService) + ',' + InstanceType + ',' + str(servicetasks_count) + ',' + servicename + ',' + str(task_memory) + ',' + str(task_cpu) + '\n')
                #filevar += clustername + ',' + InstanceId + ',' + str(RunningTasks) + ',' + InstanceType + ',' + bapp_id + ',' + environment + ',' + executiveowner +'\n'


        else:
            clustername = 'NA'
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
            env_tag = 'NA'
            service_min = 'NA'
            service_max = 'NA'


            #print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            print(clustername + '\t' + env_tag + '\t' + str(asg_minsize) + '\t' + str(asg_maxsize) + '\t' + str(ecsinstances) + '\t' + str(service_min) + '\t' + str(service_max) + '\t' + str(RunningTasks) + '\t' + str(ActiveService) + '\t' + InstanceType + '\t' + str(servicetasks_count) + '\t' + servicename + '\t' + str(task_memory) + '\t' + str(task_cpu))
            f.write(clustername + ',' + env_tag + ',' + InstanceType + ',' + str(asg_minsize) + ',' + str(asg_maxsize) + ',' + str(ecsinstances) + ',' + str(ActiveService) + ',' + str(servicename) + ',' + str(RunningTasks) + ',' + str(service_min) + ',' + str(service_max) + ',' + str(servicetasks_count) + ',' + str(task_memory) + ',' + str(task_cpu) + '\n')
            
            #input('proceed..?')
            # f.write(clustername + ',' + env_tag + ',' + str(asg_minsize) + ',' + str(asg_maxsize) + ',' + str(ecsinstances) + ',' + str(service_min) + ',' + str(service_max) + ',' + str(RunningTasks) + ',' + str(ActiveService) + ',' + InstanceType + ',' + str(servicetasks_count) + ',' + servicename + ',' + str(task_memory) + ',' + str(task_cpu) + '\n')
            #print(clustername + '\t' + env_tag + '\t' + str(ecsinstances) + '\t' + str(RunningTasks) + '\t' + str(ActiveService) + '\t' + InstanceType + '\t' + servicetasks_count + '\t' + servicename + '\t' + task_memory + '\t' + task_cpu)
            # input('proceed..?')
            #f.write(clustername + ',' + env_tag + ',' + ecsinstances + ',' + str(RunningTasks) + ',' + ActiveService + ',' + InstanceType + ',' + servicetasks_count + ',' + servicename + ',' + task_memory + ',' + task_cpu + '\n')

            #filevar += clustername + ',' + InstanceId + ',' + str(RunningTasks) + ',' + InstanceType + ',' + bapp_id + ',' + environment + ',' + executiveowner + '\n'
    except Exception as e:
        print('.....................................')
        print(clustername + '----------------')
        print(e)

    #finally:
    #   traceback.print_tb(e.__traceback__)
        #del exc_info

f.close()
print('Data exported to:\t' + file_name)

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





