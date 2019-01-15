import json
import os
import boto3
import sys



ec2 = boto3.client('ec2')
ecs = boto3.client('ecs')
asg = boto3.client('autoscaling')
cf = boto3.client('cloudformation')

json_file_path = input("Enter the path of your json file: ")
#json_file = '/home/ttn/Downloads/convertcsv.json'


json_records = json.load(open(json_file_path))

for record in json_records:
    print(record)
    try:
        cluster = clustername = record['clustername']
        cluster_instances = ecs.list_container_instances(
            cluster=cluster
        )
        if len(cluster_instances['containerInstanceArns']) == 0:
            #print('no container instances are available in this cluster:\t' + clustername)
            stack_name = 'EC2ContainerService-' + clustername
            cfn_resp = cf.describe_stack_resource(
                StackName=stack_name,
                ResourceType='AWS::AutoScaling::AutoScalingGroup'
            )
            print(cfn_resp)
            asg_name = cfn_resp['StackResourceDetail']['PhysicalResourceId']

        else:
            ecs_instance = ecs.describe_container_instances(
                cluster=clustername,
                containerInstances=[cluster_instances['containerInstanceArns'][0]]
            )

            ec2_tags = ec2.describe_tags(
                Filters=[
                    {
                        'Name': 'resource-id',
                        'Values': [ecs_instance['containerInstances'][0]['ec2InstanceId']]
                    }
                ])
            #print(ec2_tags)
            asg_tag = [tag for tag in ec2_tags['Tags'] if tag['Key'] == 'aws:autoscaling:groupName']

            asg_name = asg_tag[0]['Value']
        

        print(asg_name)

        print('adding tag to asg:\t' + asg_name)
        add_asg_tag_resp = asg.create_or_update_tags(
            Tags=[
                {
                    'ResourceId': asg_name,
                    'ResourceType': 'auto-scaling-group',
                    'Key': record['Key'],
                    'Value': record['Value'],
                    'PropagateAtLaunch': True
                },
            ]
        )
        #print(add_asg_tag_resp)

        print('adding tags to all cluster instances')
        #print(cluster_instances['containerInstanceArns'])
        for instance in cluster_instances['containerInstanceArns']:
            ecs_instance = ecs.describe_container_instances(
                cluster = clustername,
                containerInstances = [ instance ]
            )
            
            instance_id = ecs_instance['containerInstances'][0]['ec2InstanceId']

            create_tag_resp = ec2.create_tags(
                Resources=[ instance_id ],
                Tags=[
                    {
                        'Key': record['Key'],
                        'Value': record['Value']
                    },
                ]
            )
            #print(create_tag_resp)
        else:
            print('no more iteration available in list')
    except Exception as e:
        print('-------------------------------------------------------------')
        print(e)    

