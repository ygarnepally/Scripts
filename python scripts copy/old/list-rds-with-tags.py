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
        instances.append(instance['DBInstanceArn'])

    if 'Marker' in rds_instances:
        next_token = True
        rds_instances = rds.describe_db_instances(
            MaxRecords=20,
            Marker = rds_instances['Marker']
        )
    else:
        next_token = False

file = open('rds-instances-tags.csv', 'w+')
file.write("dbidentifier,tags")
file.write("\n")
for instance in instances:
    tags = rds.list_tags_for_resource(
        ResourceName=instance
    )
    print(tags)
    identifier = instance.split(':')[-1]
    tags1 = [tag['Key'] + ':' + tag['Value'] for tag in tags['TagList']]
    tags2 = ','.join(tags1)
    file.write(identifier + ',' + tags2 + "\n")

file.close()



