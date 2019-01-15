
import boto3
import json
import os
import datetime
import gspread

#from oauth2client.service_account import ServiceAccountCredentials

region = input('RegionName:\t')

ecs = boto3.client('ecs', region_name=region)
ec2 = boto3.client('ec2', region_name=region)
asg = boto3.client('autoscaling', region_name=region)
cw = boto3.client('cloudwatch', region_name=region)

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
f.write("clustername,policy_name,policy_type,InstanceType,alarmname,metricname,threshold,evelp,period")
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

            asg_name = [tag['Value'] for tag in desc_instance['Reservations'][0]['Instances'][0]['Tags'] if tag['Key'] == 'aws:autoscaling:groupName']
            

            asg_name = ''.join(asg_name)

            asg_policies = asg.describe_policies(
                AutoScalingGroupName=asg_name
               )
            for policy in asg_policies['ScalingPolicies']:
                policy_name = policy['PolicyName']
                policy_type = policy['PolicyType']
                scale_adj = policy['ScalingAdjustment']


                for alarm in policy['Alarms']:
                    alarmname = alarm['AlarmName']
                    desc_alarm = cw.describe_alarms(
                        AlarmNames=[ alarmname ]
                        )
                    
                    desc_alarm = desc_alarm['MetricAlarms'][0]
                    metricname = desc_alarm['MetricName']
                    threshold = desc_alarm['Threshold']
                    evelp = desc_alarm['EvaluationPeriods']
                    period = desc_alarm['Period']



                    print(clustername + '\t' + policy_name + '\t' + policy_type + '\t' + InstanceType + '\t' + alarmname + '\t' + metricname + '\t' + str(threshold) + '\t' + str(evelp) + '\t' + str(period))
                    
                    f.write(clustername + ',' + policy_name + ',' + policy_type + ',' + InstanceType + ',' + alarmname + ',' + metricname + ',' + str(threshold) + ',' + str(evelp) + ',' + str(period) + '\n')
                    #print(desc_alarm)
                    #print(desc_alarm)
                    #input('gsdgsg')




            

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
            policy_type = 'NA'
            policy_name = 'NA'
            alarmname = 'NA'
            threshold = 'NA'
            metricname = 'NA'
            evelp = 'NA'
            period = 'NA'


            #print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            print(clustername + '\t' + policy_name + '\t' + policy_type + '\t' + InstanceType + '\t' + alarmname + '\t' + metricname + '\t' + str(threshold) + '\t' + str(evelp) + '\t' + str(period))
                    
            f.write(clustername + ',' + policy_name + ',' + policy_type + ',' + InstanceType + ',' + alarmname + ',' + metricname + ',' + str(threshold) + ',' + str(evelp) + ',' + str(period) + '\n')
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





