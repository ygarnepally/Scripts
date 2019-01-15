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
file.write("dbidentifier,tag:bag,tag:baap_id,tag:environment,tag:executiveowner,tag:Name")
file.write("\n")
for instance in instances:
    
    tags = rds.list_tags_for_resource(
        ResourceName=instance
    )
    print(tags)
    identifier = instance.split(':')[-1]
    #tags1 = [tag['Key'] + ':' + tag['Value'] for tag in tags['TagList']]
    #tags2 = ','.join(tags1)
    

    bapp_id = 'NA'
    bag = 'NA'
    environment = 'NA'
    executiveowner = 'NA'
    Name = 'NA'
    
    if len(tags['TagList']) > 0:
        print('Greater than zero......')
        #taglist = ['biag', 'baap_id', 'environment', 'executiveowner', 'Name' ]:
        #for t in taglist:
        for tag in tags['TagList']:
            if tag['Key'] == 'bag':
                bag = tag['Value']
                print('bag\t' + bag)


            if tag['Key'] == 'bapp_id':
                bapp_id = tag['Value']
                print('bapp_id\t' + bapp_id)

            if tag['Key'] == 'environment':
                environment = tag['Value']
                print('environment\t' + environment)


                
            if tag['Key'] == 'executiveowner':
                executiveowner = tag['Value'] 
                print('executiveowner\t' + executiveowner)


            if tag['Key'] == 'Name':
                Name = tag['Value'] 
                print('Name\t' + Name)
       
    

    #input('procced')
    file.write(identifier + ',' + bag + ',' + bapp_id + ',' + environment + ',' + executiveowner + ',' + Name + "\n")
            
           
file.close()



