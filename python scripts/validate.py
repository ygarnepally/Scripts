import boto3
from botocore.exceptions import ClientError
regions = ['us-west-2']

f = open("west.csv", 'w+')
f.write('\n')

def calculate_ratio (cpu, memory, instance_type):
	if "c5" in instance_type and cpu/memory == 1/2:
		return True
	elif "m" in instance_type and cpu/memory == 1/4:
		return True
	elif "c4" in instance_type and cpu/memory == 1/1.875:
		return True
	elif "r5" in instance_type and cpu/memory == 1/8:
		return True
	elif "r4" in instance_type and cpu/memory == 1/7.625:
		return True
	else:
		return False 

def threshold(scaleup_threshold, scaledown_threshold):
	if scaledown_threshold in ['6000', '600'] and scaleup_threshold in ['10000', '1000']:
		return ''
	else:
		return '1'
		
def scalingmetric(metricname):
	if metricname == 'RequestCountPerTarget':
		return ''
	else:
		return '2'
		
def alarmstatevalue(Statevalue_scaleup, Statevalue_scaledown):
	if Statevalue_scaleup in ['OK', 'ALARM'] and Statevalue_scaleup in ['OK', 'ALARM']:
		return ''
	else:
		return '3'
		
def datapoints_validate(scaleup_datapoints, Scaledown_datapoints):
	if scaleup_datapoints == 300 and Scaledown_datapoints == 900:
		return ''
	else:
		return '4'


#getting evaluationperiods and periods for scale up and scale down alarm
def datapoints(evalperiods, periods):
	alarm_datapoints = int(evalperiods)*periods
	return alarm_datapoints

for region in regions:

	accounts = ['wdpr-apps','wdpr-apps-pilot','dcl-apps-dev','dcl-apps-test','dcl-apps-prod','nvo-apps-dev','nvo-apps-test','nvo-apps-prod','shdr-apps-dev','wdpr-ee-dev','wdpr-ee-test','wdpr-ee-prod','wdpr-packaging-dev','wdpr-packaging-test', 'wdpr-packaging-prod','wdpr-fastpass-dev','wdpr-fastpass-test','wdpr-fastpass-prod','wdpr-ecommerce-dev','wdpr-ecommerce-test','wdpr-ecommerce-prod','wdpr-revmgmt-dev','wdpr-revmgmt-test','wdpr-revmgmt-prod', 'wdpr-cast-dev','wdpr-cast-test','wdpr-cast-prod','wdpr-ticketing-dev','wdpr-ticketing-test','wdpr-ticketing-prod','wdpr-lodging-dev','wdpr-lodging-test','wdpr-lodging-prod','wdpr-gam-dev','wdpr-gam-test', 'wdpr-gam-prod','wdpr-dpi-dev','wdpr-dpi-test','wdpr-dpi-prod','hkdl-apps-dev','hkdl-apps-test','hkdl-apps-prod']
	
	for account in accounts:
		session = boto3.Session(profile_name= account)
		ecsclient = session.client('ecs', region_name=region)
		ec2client = session.client('ec2', region_name=region)
		asgclient = session.client('application-autoscaling', region_name=region)
		cloudwatchclient = session.client('cloudwatch', region_name=region)
		db = boto3.client('dynamodb')
		print("--account--",account,"--region--",region)
		next_token = True

		while next_token:
			if next_token and next_token != True:
				response = ecsclient.list_clusters(maxResults=100, nextToken=next_token)
			else:
				response = ecsclient.list_clusters(maxResults=100)
			next_token = response.get('nextToken')
	
			clusterarn = response['clusterArns'] # clusterarn has list of arns
			for arn in clusterarn:
				clustername = arn.split('/')[-1]
				print("----------clusterarn---------",arn)
				service_token = True

				while service_token:
					if service_token and service_token != True:
						listservice_response = ecsclient.list_services(cluster=arn, maxResults=50, nextToken=service_token, launchType='EC2')
					else:
						listservice_response = ecsclient.list_services(cluster=arn, maxResults=50, launchType='EC2')
					service_token = listservice_response.get('nextToken')
					services= listservice_response['serviceArns']
					
					#list container instances
					instance_response = ecsclient.list_container_instances(cluster=arn)
					if instance_response['containerInstanceArns']:
						ci_descriptions_response = ecsclient.describe_container_instances(cluster=arn, containerInstances=instance_response['containerInstanceArns'])
						instance_id = ci_descriptions_response['containerInstances'][0]['ec2InstanceId']
						ec2_response = ec2client.describe_instances(InstanceIds=[instance_id])
						instance_type = ec2_response['Reservations'][0]['Instances'][0]['InstanceType']
						instance_type_firstletter = instance_type[0]
						
						for service in services:
							servicename = service.split('/')[-1]
							resourceid = 'service/' + clustername + '/' + servicename
							# get desired and running count
							service_response = ecsclient.describe_services(cluster = arn, services=[servicename])
							taskdef_response = ecsclient.describe_task_definition(taskDefinition=service_response['services'][0]['taskDefinition'])
							cpu = taskdef_response['taskDefinition']['containerDefinitions'][0]['cpu']
							if "memory" in taskdef_response['taskDefinition']['containerDefinitions'][0]:
								memory = taskdef_response['taskDefinition']['containerDefinitions'][0]['memory']
							elif 'memoryReservation' in taskdef_response['taskDefinition']['containerDefinitions'][0]:
								memory = taskdef_response['taskDefinition']['containerDefinitions'][0]['memoryReservation']
								
							check_ratio = calculate_ratio(cpu, memory, instance_type) #function calling to get ratio of cpu and memory

							desired_count = service_response['services'][0]['desiredCount']
							running_count = service_response['services'][0]['runningCount']
							desc_asg = asgclient.describe_scaling_policies(ServiceNamespace='ecs', ResourceId=resourceid)
							if desc_asg['ScalingPolicies'] != []:
								alarm_names = []  #pass both alarm names into alarm_names
								alarm_1 = desc_asg['ScalingPolicies'][0].get('Alarms')
								if alarm_1:
									alarm_names.append(alarm_1[0].get('AlarmName'))
								try:
									alarm_2 = desc_asg['ScalingPolicies'][1].get('Alarms')
									if alarm_2:
										alarm_names.append(alarm_2[0].get('AlarmName'))

								except IndexError:
									pass
								alarm_response = cloudwatchclient.describe_alarms(AlarmNames=alarm_names)
								
								scaledown_threshold = 'NA'
								scaleup_threshold = 'NA'
								metricname = 'NA'
								scaledown_evalperiods = 'NA'
								statevalue_scaledown = 'NA'
								scaleup_evalperiods = 'NA'
								statevalue_scaleup = 'NA'
								periods = 'NA'
								
								alarm_desc_1 = alarm_response['MetricAlarms'][0]['AlarmArn']
								if 'ScaleDown' in alarm_desc_1:
									scaledown_threshold = alarm_response['MetricAlarms'][0]['Threshold']
									metricname = alarm_response['MetricAlarms'][0]['MetricName']
									evalperiods = alarm_response['MetricAlarms'][0]['EvaluationPeriods']
									print("--alarm1 if--",evalperiods)
									periods = alarm_response['MetricAlarms'][0]['Period']
									statevalue_scaledown = alarm_response['MetricAlarms'][0]['StateValue']
									scaledown_datapoints = str(datapoints(evalperiods, periods))

								elif 'ScaleUp' in alarm_desc_1:
									scaleup_threshold = alarm_response['MetricAlarms'][0]['Threshold']
									metricname = alarm_response['MetricAlarms'][0]['MetricName']
									evalperiods = alarm_response['MetricAlarms'][0]['EvaluationPeriods']
									print("--alarm1 elif--",evalperiods)
									periods = alarm_response['MetricAlarms'][0]['Period']
									statevalue_scaleup = alarm_response['MetricAlarms'][0]['StateValue']
									scaleup_datapoints = str(datapoints(evalperiods, periods))
								#if there is no second alarm_arn
								if len(alarm_response['MetricAlarms']) > 1:
									alarm_desc_2 = alarm_response['MetricAlarms'][1]['AlarmArn']
									if 'ScaleDown' in alarm_desc_2:
										scaledown_threshold = alarm_response['MetricAlarms'][1]['Threshold']
										evalperiods = alarm_response['MetricAlarms'][1]['EvaluationPeriods']
										print("--alarm2 if--",evalperiods)
										periods = alarm_response['MetricAlarms'][1]['Period']
										statevalue_scaledown = alarm_response['MetricAlarms'][1]['StateValue']
										scaledown_datapoints = str(datapoints(evalperiods, periods))

									elif 'ScaleUp' in alarm_desc_2:
										scaleup_threshold = alarm_response['MetricAlarms'][1]['Threshold']
										evalperiods = alarm_response['MetricAlarms'][1]['EvaluationPeriods']
										print("--alarm2 elif--",evalperiods)
										periods = alarm_response['MetricAlarms'][1]['Period']
										statevalue_scaleup = alarm_response['MetricAlarms'][1]['StateValue']
										scaleup_datapoints = str(datapoints(evalperiods, periods))
								
								Account = str(account)
								Clustername = str(clustername)
								Servicename = str(servicename)
								Region = str(region)
								Scaleup_threshold = str(scaleup_threshold)
								Scaledown_threshold = str(scaledown_threshold)
								Metricname = str(metricname)
								Scaleup_datapoints = str(scaleup_datapoints)
								Scaledown_datapoints = str(scaledown_datapoints)
								Statevalue_scaleup = str(statevalue_scaleup)
								Statevalue_scaledown = str(statevalue_scaledown)
								Cpu = str(cpu)
								Memory = str(memory)
								
								#pace_validate
								pace_validate = ''
								if threshold(scaleup_threshold, scaleup_threshold) != '' :
									pace_validate += threshold(scaleup_threshold, scaleup_threshold)+":"
	
								if scalingmetric(metricname) != '' :
									pace_validate += scalingmetric(metricname)+":"
	
								if alarmstatevalue(Statevalue_scaleup, Statevalue_scaledown) != '' :
									pace_validate += alarmstatevalue(Statevalue_scaleup, Statevalue_scaledown)+":"
	
								if datapoints_validate(scaleup_datapoints, Scaledown_datapoints) != '' :
									pace_validate += datapoints_validate(scaleup_datapoints, Scaledown_datapoints)+":"
	
								if not calculate_ratio(cpu, memory, instance_type):
									pace_validate += '5'


								if Metricname == 'RequestCountPerTarget'and Statevalue_scaleup in ['OK', 'ALARM'] and Statevalue_scaledown in ['OK', 'ALARM'] and Scaleup_datapoints == '300' and Scaledown_datapoints == '900' and check_ratio == True and scaledown_threshold in ['6000', '600'] and scaleup_threshold in ['10000', '1000']:
										#statevalue_scaledown == 'OK' or statevalue_scaledown == 'ALARM'
										#statevalue_scaleup in ['OK','ALARM']
									print("standard")
								else:
									print("pace_validate",pace_validate, Clustername)
									f.write(Account + ',' + Clustername + ',' + Servicename + ',' + Region + ',' + Scaleup_threshold + ',' + Scaledown_threshold + ',' + Metricname + ',' + Scaleup_datapoints + ',' + Scaledown_datapoints + ',' +  Statevalue_scaleup + ',' + Statevalue_scaledown + ',' + Cpu + ',' + Memory +',' +pace_validate+'\n')
