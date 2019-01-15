import boto3
import json
import os

region = input('RegionName:\t')

rds = boto3.client('rds', region_name=region)
next_token = True
instances = []
rds_instances = rds.describe_db_instances(
    MaxRecords = 20
)

while next_token == True:
    for instance in rds_instances['DBInstances']:
        instances.append(instance)

    if 'Marker' in rds_instances:
        next_token = True
        rds_instances = rds.describe_db_instances(
            MaxRecords=20,
            Marker = rds_instances['Marker']
        )
    else:
        next_token = False

file = open('rds-instances-tags.csv', 'w+')
file.write("dbidentifier,bag,pace_env,bappp-id,instance_type,engine,storage,storage_type,multi_az,public,iops")
file.write("\n")
for instance in instances:
    arn = instance['DBInstanceArn']
    identifier = instance['DBInstanceIdentifier'].split(':	')[-1]
    instance_type = instance['DBInstanceClass']
    engine = instance['Engine']
    storage = instance['AllocatedStorage']
    storage_type = instance['StorageType']
    multi_az = instance['MultiAZ']
    public = instance['PubliclyAccessible']
    iops = instance['Iops'] if 'Iops' in instance else 'NA'


    tags = rds.list_tags_for_resource(
        ResourceName=arn
    )
    if tags['TagList']:
        bag = [tag['Value'] for tag in tags['TagList'] if tag['Key'] == 'bag']
        bag = ''.join(bag) if bag else 'NA'
        bapp_id = [tag['Value'] for tag in tags['TagList'] if tag['Key'] == 'bapp_id']
        bapp_id = ''.join(bapp_id) if bapp_id else 'NA'
        pace_env = [tag['Value'] for tag in tags['TagList'] if tag['Key'] == 'pace_env']
        pace_env = ''.join(pace_env) if pace_env else 'NA'
    else:
        bag = 'NA'
        bapp_id = 'NA'
        pace_env = 'NA'

    # print(tags)
    # print(bag)
    # print(bapp_id)
    # # input('??????????????????')
    # # tags1 = [tag['Key'] + ':' + tag['Value'] for tag in tags['TagList']]
    print(identifier)
    # print(instance_type)
    # print(engine)
    # print(storage)
    # print(storage_type)
    # print(multi_az)
    # print(public)
    # print(iops)
    # # tags2 = ','.join(tags1)
    file.write(identifier + ',' + bag + ',' + pace_env + ',' + bapp_id + ',' + instance_type + ',' + engine + ',' + str(storage) + ',' + storage_type + ',' + str(multi_az) + ',' + str(public) + ',' + str(iops) + "\n")

file.close()



