
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
f.write("clustername,bapp_id_tag,env_tag,region,asg_minsize,asg_maxsize,InstanceType,scale_up_policy,scale_up_adj,scale_up_thrs,scale_up_evelp,scale_up_period,scale_down_policy,scale_down_adj,scale_down_thrs,scale_down_evelp,scale_down_period")
#f.write("clustername,policy_name,policy_type,InstanceType,alarmname,metricname,threshold,evelp,period")
f.write('\n')


for cluster in clusters:
    #try:
    if 0 == 0:
        # input('??????????????????????????????????????????????')
        clustername = cluster.split('/')[-1]

        desc_cluster = ecs.describe_clusters(
            clusters=[ clustername ],
        )
        desc_cluster = desc_cluster['clusters'][0]
        ecsinstances = desc_cluster['registeredContainerInstancesCount']
        cluster_status = desc_cluster['status']
        RunningTasks = desc_cluster['runningTasksCount']
        ActiveService = desc_cluster['activeServicesCount']

        scale_down_policy = 'NA'
        scale_up_policy = 'NA'
        scale_up_alarm = 'NA'
        scale_down_alarm = 'NA'
        scale_up_policytype = 'NA'
        scale_down_policytype = 'NA'
        scale_up_metricname = 'NA'
        scale_down_metricname = 'NA'
        scale_up_thrs = 'NA'
        scale_down_thrs = 'NA'
        scale_up_evelp = 'NA'
        scale_down_evelp = 'NA'
        scale_up_period = 'NA'
        scale_down_period = 'NA'
        scale_up_adj = 'NA'
        scale_down_adj = 'NA'
        InstanceType = 'NA'


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

            desc_asg = asg.describe_auto_scaling_groups(
                AutoScalingGroupNames=[asg_name]
                )
            asg_minsize = desc_asg['AutoScalingGroups'][0]['MinSize']
            asg_maxsize = desc_asg['AutoScalingGroups'][0]['MaxSize']
            #print(desc_asg)
            env_tag = [tag['Value'] for tag in desc_asg['AutoScalingGroups'][0]['Tags'] if tag['Key'] == 'environment']
            env_tag = ''.join(env_tag)
            bapp_id_tag = [tag['Value'] for tag in desc_asg['AutoScalingGroups'][0]['Tags'] if tag['Key'] == 'bapp_id']
            bapp_id_tag = ''.join(bapp_id_tag)


            asg_policies = asg.describe_policies(
                AutoScalingGroupName=asg_name
               )
            
            # scale_down_policy = 'NA'
            # scale_up_policy = 'NA'
            # scale_up_alarm = 'NA'
            # scale_down_alarm = 'NA'
            # scale_up_policytype = 'NA'
            # scale_down_policytype = 'NA'
            # scale_up_metricname = 'NA'
            # scale_down_metricname = 'NA'
            # scale_up_thrs = 'NA'
            # scale_down_thrs = 'NA'
            # scale_up_evelp = 'NA'
            # scale_down_evelp = 'NA'
            # scale_up_period = 'NA'
            # scale_down_period = 'NA'
            # scale_up_adj = 'NA'
            # scale_down_adj = 'NA'




            for policy in asg_policies['ScalingPolicies']:
                if 'scale-up' in policy['PolicyName']:

                    scale_up_policy = policy['PolicyName']
                    scale_up_policytype = policy['PolicyType']
                    scale_up_adj = policy['ScalingAdjustment']

                    for alarm in policy['Alarms']:
                        scale_up_alarm = alarm['AlarmName']
                        desc_alarm = cw.describe_alarms(
                            AlarmNames=[ alarm['AlarmName'] ] 
                            )
                        
                        desc_alarm = desc_alarm['MetricAlarms'][0]
                        scale_up_metric = desc_alarm['MetricName']
                        scale_up_thrs = desc_alarm['Threshold']
                        scale_up_evelp = desc_alarm['EvaluationPeriods']
                        scale_up_period = desc_alarm['Period']

                elif 'scale-down' in policy['PolicyName']:
                    scale_down_policy = policy['PolicyName']
                    scale_down_policytype = policy['PolicyType']
                    scale_down_adj = policy['ScalingAdjustment']

                    for alarm in policy['Alarms']:
                        scale_down_alarm = alarm['AlarmName']
                        desc_alarm = cw.describe_alarms(
                            AlarmNames=[ alarm['AlarmName'] ]
                            )
                        
                        desc_alarm = desc_alarm['MetricAlarms'][0]
                        scale_down_metric = desc_alarm['MetricName']
                        scale_down_thrs = desc_alarm['Threshold']
                        scale_down_evelp = desc_alarm['EvaluationPeriods']
                        scale_down_period = desc_alarm['Period']



            print('print after policy')
            print(clustername + '\t' + bapp_id_tag + '\t' + env_tag + '\t' + region + '\t' + str(asg_minsize) + '\t' + str(asg_maxsize) + '\t' + InstanceType + '\t' + scale_up_policy + '\t' + str(scale_up_adj) + '\t' + str(scale_up_thrs) + '\t' + str(scale_up_evelp) + '\t' + str(scale_up_period)  + '\t' + scale_down_policy + '\t' + str(scale_down_adj) + '\t' + str(scale_down_thrs) + '\t' + str(scale_down_evelp) + '\t' + str(scale_down_period))
                    
            f.write(clustername + ',' + bapp_id_tag + ',' + env_tag + ',' + region + ',' + str(asg_minsize) + ',' + str(asg_maxsize) + ',' + InstanceType + ',' + scale_up_policy + ',' + str(scale_up_adj) + ',' + str(scale_up_thrs) + ',' + str(scale_up_evelp) + ',' + str(scale_up_period) + ',' + scale_down_policy + ',' + str(scale_down_adj) + ',' + str(scale_down_thrs) + ',' + str(scale_down_evelp) + ',' + str(scale_down_period) + '\n')
                    




            

        else:
            #InstanceType = 'NA'
            
            #print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            print(clustername + '\t' + bapp_id_tag + '\t' + env_tag + '\t' + region + '\t' + str(asg_minsize) + '\t' + str(asg_maxsize) + '\t' + InstanceType + '\t' + scale_up_policy + '\t' + str(scale_up_adj) + '\t' + str(scale_up_thrs) + '\t' + str(scale_up_evelp) + '\t' + str(scale_up_period)  + '\t' + scale_down_policy + '\t' + str(scale_down_adj) + '\t' + str(scale_down_thrs) + '\t' + str(scale_down_evelp) + '\t' + str(scale_down_period))
                    
            f.write(clustername + ',' + bapp_id_tag + ',' + env_tag + ',' + region + ',' + str(asg_minsize) + ',' + str(asg_maxsize) + ',' + InstanceType + ',' + scale_up_policy + ',' + str(scale_up_adj) + ',' + str(scale_up_thrs) + ',' + str(scale_up_evelp) + ',' + str(scale_up_period) + ',' + scale_down_policy + ',' + str(scale_down_adj) + ',' + str(scale_down_thrs) + ',' + str(scale_down_evelp) + ',' + str(scale_down_period) + '\n')
            #filevar += clustername + ',' + InstanceId + ',' + str(RunningTasks) + ',' + InstanceType + ',' + bapp_id + ',' + environment + ',' + executiveowner + '\n'
    # except Exception as e:
    #     print('-------------------------------------------------------------')
    #     print(clustername + '----------------')
    #     print(e)

f.close()







