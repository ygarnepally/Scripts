import json
import boto3
import csv


# session = boto3.Session(profile_name='sts-prod', region_name='us-east-1')
# ec2 = session.client('ec2')
regions = ['us-east-1']


s3r = boto3.resource('s3')
s3 = boto3.client('s3')

bucket = 'pace-event-mon'



get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))
objs = s3.list_objects_v2(Bucket=bucket)['Contents']

# print(objs)

last_added = [obj['Key'] for obj in sorted(objs, key=get_last_modified)][-1]


print(last_added)

s3r.Bucket(bucket).download_file(last_added, last_added)


# with open(last_added, newline='') as csvfile:
# 	csv_data = csv.reader(csvfile, delimiter=' ', quotechar='|')
# 	# for row in spamreader:
# 	# 	print(', '.join(row))
csv_rows = []
with open(last_added) as csvfile1:
	reader = csv.DictReader(csvfile1)
	fields = reader.fieldnames
	title = fields

	for row in reader:
		csv_rows.extend([{title[i]:row[title[i]] for i in range(len(title))}])

# z = [x for x in csv_rows if x['Current bapp_id'] == 'BAPP0004919']

# print(z)

## looping into all regions
for region in regions:
	ec2 = boto3.client('ec2', region_name = region)
	asg = boto3.client('autoscaling', region_name = region)


	## Get all ASGs
	all_asgs = []

	desc_asg = asg.describe_auto_scaling_groups(MaxRecords=5)
	next_token = True
	while next_token != False:

		all_asgs.extend(desc_asg['AutoScalingGroups'])
	    # for group in desc_asg['AutoScalingGroups']:
	    #     all_asg.append(group)

		if 'NextToken' in desc_asg:
			next_token = True
			desc_asg = asg.describe_auto_scaling_groups(
				NextToken = desc_asg['NextToken'],
				MaxRecords=5
		    )
		else:
			next_token = False



	##
	print(len(all_asgs))
	# input('?????????asg')
	for group in all_asgs:
		tags = group['Tags']

		bapp_id_tag = [ tag['Value'] for tag in tags if tag['Key'] == 'bapp_id']

		if bapp_id_tag:
			bapp_id = ''.join(bapp_id_tag)

			node_id = [ id['name_node_id'] for id in csv_rows if id['Current bapp_id'] == bapp_id ]
			# print(node_id)
			if node_id:
				node_id = ''.join(node_id)

				###Update Autoscaling group ...
				print('updating node_id tag on ASG: ' + group['AutoScalingGroupName'])
				update_tag = asg.create_or_update_tags(
				    Tags=[
				        {
				            'ResourceId': group['AutoScalingGroupName'],
				            'ResourceType': 'auto-scaling-group',
				            'Key': 'node_id',
				            'Value': str(node_id),
				            'PropagateAtLaunch': True
				        },
				    ]
				)


				# input('Proceed   ???????????')
			else:
				print('#' * 20 + '\nNo node_id found for bapp_id: ' + str(bapp_id) + '#' * 20 + '\n')
		else:
			print('#' * 20 + '\nNo bapp_id found on asg: ' + group['AutoScalingGroupName'] + '#' * 20 + '\n')
