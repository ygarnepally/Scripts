import boto3
import json
import os
from datetime import datetime, timedelta
import time

region = 'us-west-2'

ec2 = boto3.client('ec2', region_name=region)
rds = boto3.client('rds', region_name=region)
cw = boto3.client('cloudwatch', region_name=region)

today = datetime.now()
from_date = today - timedelta(days=14)

ec2_desc = ec2.describe_instances(MaxResults=10,)
next_token = True
total_instace_desc = []

while next_token != False:
    for reservation in ec2_desc['Reservations']:
        instances = reservation['Instances']
        total_instace_desc += instances

    if 'NextToken' in ec2_desc:
        next_token = True
        ec2_desc = ec2.describe_instances(MaxResults=10, NextToken = ec2_desc['NextToken'])
    else:
        next_token = False

print('total no. of instances..')
print(len(total_instace_desc))

file = open('ec2_inventory.csv', 'w+')
file.write("InstanceId,Name,Pace_Env,bapp_id,ex-owner,PrivateIP,PublicIP,LifeCycle,AutoStop,InstanceType,State,CPU_min,CPU_max,CPU_avg" + "\n")


for instance in total_instace_desc:
    if instance['State']['Name'] != 'terminated':
        ins_id = instance['InstanceId']
        prv_ip = instance['PrivateIpAddress'] if 'PrivateIpAddress' in instance else 'NA'
        pub_ip = instance['PublicIpAddress'] if 'PublicIpAddress' in instance else 'NA'
        state  = instance['State']['Name']
        instancetype = instance['InstanceType']
        lifecyc = instance['InstanceLifecycle'] if 'InstanceLifecycle' in instance else 'NA'

        if 'Tags' not in instance:
            instance['Tags'] = []

        tag_name = [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name']
        tag_name = ''.join(tag_name) if tag_name else 'NA'

        bapp_id = [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'bapp_id']
        bapp_id = ''.join(bapp_id) if bapp_id else 'NA'

        pace_env = [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'pace_env']
        pace_env = ''.join(pace_env) if pace_env else 'NA'

        tag_autostop = [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'AutoStop']
        tag_autostop = ''.join(tag_autostop) if tag_autostop else 'NA'

        ex_owner = [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'pace_eo']
        ex_owner = ''.join(ex_owner) if ex_owner else 'NA'
        print(ins_id)
        cw_desc = cw.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            StartTime=from_date,
            EndTime=today,
            Period=86400,
            Statistics=['Average', 'Minimum', 'Maximum'],
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': ins_id
                },
            ]
        )
        print(cw_desc)
        # input('??????/')
        con_max = [str(dp['Maximum'].__round__(2)) for dp in cw_desc['Datapoints']]
        con_min = [str(dp['Minimum'].__round__(2)) for dp in cw_desc['Datapoints']]
        con_avg = [str(dp['Average'].__round__(2)) for dp in cw_desc['Datapoints']]
        con_max = ', '.join(con_max)
        con_min = ', '.join(con_min)
        con_avg = ', '.join(con_avg)
        # input('??????/')

        print(ins_id + ',' + tag_name + ',' + pace_env + ',' + bapp_id + ',' + ex_owner + ',' + prv_ip + ',' + pub_ip + ',' + lifecyc + ',' + tag_autostop + ',' + instancetype + ',' + state)

        file.write(ins_id + ',' + tag_name + ',' + pace_env + ',' + bapp_id + ',' + ex_owner + ',' + prv_ip + ',' + pub_ip + ',' + lifecyc + ',' + tag_autostop + ',' + instancetype + ',' + state + ',"' + str(con_min) + '","' + str(con_max) + '","' + str(con_avg) + '"' + '\n')

#     #except Exception as e:
#         #print(e)
#         # print(instance)
#         # input('exception????')


file.close()

input('proceed for rds ???????????????????????????????')

file = open('rds_inventory.csv', 'w+')
#file.write('\n'*10)
#file.write('RDS Database ')
file.write('RDS resources- last 14 days report with per day database connections.\n\n')
file.write('RDSIdentifier,Status,InstanceSize,MinConn/day,MaxConn/day,AvgConn/day' + '\n')
###  RDS  ##########################################
next_token = True
#total_db_instaces = []
print('describing instances ...')
rds_desc = rds.describe_db_instances(
    #MaxRecords=20,
)
total_db_instaces = rds_desc['DBInstances']

print(len(rds_desc['DBInstances']))

print('total rds instances: ' + str(len(total_db_instaces)))

for db in total_db_instaces:
    rds_name = db['DBInstanceIdentifier']
    status = db['DBInstanceStatus']
    rds_size = db['DBInstanceClass']
    print('describing cloudwatch..')
    cw_desc = cw.get_metric_statistics(
        Namespace = 'AWS/RDS',
        MetricName = 'DatabaseConnections',
        StartTime = from_date,
        EndTime = today,
        Period = 86400,
        Statistics = ['Average', 'Minimum', 'Maximum' ],
        Dimensions=[
            {
                'Name': 'DBInstanceIdentifier',
                'Value': rds_name
            },
        ]
    )

    con_max = [str(dp['Maximum']) for dp in cw_desc['Datapoints']]
    con_min = [str(dp['Minimum']) for dp in cw_desc['Datapoints']]
    con_avg = [str(dp['Average'].__round__(2)) for dp in cw_desc['Datapoints']]

    con_max = ', '.join(con_max)
    con_min = ', '.join(con_min)
    con_avg = ', '.join(con_avg)

    print(rds_name, '\t', status, '\t', rds_size + '\t' + str(con_min) + '\t' + str(con_max) + '\t' + str(con_avg))
    file.write(rds_name + ','+ status + ',' + rds_size + ',"' + str(con_min) + '","' + str(con_max) + '","' + str(con_avg) + '"' + '\n')

file.close()

# session = boto3.Session(profile_name='ttn', region_name='us-east-2')
# db = session.client('dynamodb')
#
# table = db.create_table(
#     TableName='load-shrink-snapshot1',
#     KeySchema=[
#         {
#             'AttributeName': 'servicetimestamp',
#             'KeyType': 'HASH'  #Partition key
#         },{
#             'AttributeName': 'datetime',
#             'KeyType': 'RANGE'  #Sort key
#         }
#
#     ],
#     AttributeDefinitions=[
#         {
#             'AttributeName': 'servicetimestamp',
#             'AttributeType': 'S'
#         },{
#             'AttributeName': 'datetime',
#             'AttributeType': 'N'
#         }
#
#     ],
#     ProvisionedThroughput={
#         'ReadCapacityUnits': 10,
#         'WriteCapacityUnits': 10
#     }
# )
#
# print(table)
#
# db.put_item( TableName = 'table1',
#     Item={
#         "cluster": {"S": "ljcluster2"},
#         "datetime": {"N": "20180203115449"},
#         "desiredcount": {"N": "2"},
#         "escinstances": {"N": "2"},
#         "runningcount": {"N": "2"},
#         "service": {"S": "srv4"},
#         "servicetimestamp": {"S": "srv1_20180203115449"}
#         })
#
# """
# from boto3.dynamodb.conditions import Key, Attr
# ddb = session.resource('dynamodb')
# #db.query(TableName ='table1', KeyConditionExpression = "service  srv3")
#
# tbl = ddb.Table('table1')
# """
# r = tbl.query(
# KeyConditionExpression=Key('service').eq('srv3')
# )
# r1 = tbl.scan(
# FilterExpression=Attr('datetime').eq(20180101000000),
#     AttributesToGet = ['datetime']
# )
# print(r1)
# """
# from boto3.dynamodb.conditions import Key, Attr
# z = tbl.query(
#     KeyConditionExpression= Key('service').eq('srv1') & Key('datetime').gt(2018010200001)
# )
# print(z['Items'])



