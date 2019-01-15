
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
aasg = boto3.client('application-autoscaling', region_name=region)
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
f.write("ClusterName,Service,PolicyName,PolicyType,AlarmName,MetricName,Threshold,EvaluationPeriod,Period")
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

        cluster_services = ecs.list_services(
            cluster=clustername

        )
        for service in cluster_services['serviceArns']:
            servicename = service.split('/')[-1]
            resourceid = 'service/' + clustername + '/' + servicename
            desc_aasg = aasg.describe_scaling_policies(
               ServiceNamespace='ecs',
               ResourceId=resourceid

            )
            for policy in desc_aasg['ScalingPolicies']:
                policy_name = policy['PolicyName']
                policy_type = policy['PolicyType']

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
                    #print(desc_alarm)
                    #input('procceed??????????????????????????????')



               
                    print(clustername + '\t' + servicename + '\t' + policy_name + '\t' + policy_type + '\t' + alarmname + '\t' + metricname + '\t' + str(threshold) + '\t' + str(evelp) + '\t' + str(period))
                    #input('proceed..?')
                    f.write(clustername + ',' + servicename + ',' + policy_name + ',' + policy_type + ',' + alarmname + ',' + metricname + ',' + str(threshold) + ',' + str(evelp) + ',' + str(period) + '\n')
                    #filevar += clustername + ',' + Insx`tanceId + ',' + str(RunningTasks) + ',' + InstanceType + ',' + bapp_id + ',' + environment + ',' + executiveowner +'\n'


                    #filevar += clustername + ',' + InstanceId + ',' + str(RunningTasks) + ',' + InstanceType + ',' + bapp_id + ',' + environment + ',' + executiveowner + '\n'
    except Exception as e:
        print('-------------------------------------------------------------')
        print(clustername + '----------------')
        print(e)

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





