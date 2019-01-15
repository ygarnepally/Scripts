import boto3
import json
import os
from datetime import datetime, timedelta
import time

region = input('RegionName:\t')

ec2 = boto3.client('ec2', region_name=region)
rds = boto3.client('rds', region_name=region)
cw = boto3.client('cloudwatch', region_name=region)

today = datetime.now()
from_date = today - timedelta(days=14)

current_time = datetime.datetime.now().isoformat()


file_name = 'RDS_HOST_Report_' + region + '_' + str(current_time) + '.csv'

f = open(file_name, 'w+')





# file = open('rds_inventory.csv', 'w+')
#file.write('\n'*10)
#file.write('RDS Database ')
file.write('RDS resources- last 14 days report with per day database connections.\n\n')
file.write('RDSIdentifier,Status,InstanceSize,MinConn/day,MaxConn/day,AvgConn/day' + '\n')
###  RDS  ##########################################
next_token = True
total_db_instaces = []
print('describing instances ...')
rds_desc = rds.describe_db_instances(
    MaxRecords=80,
)

while next_token != False:
    for ins in rds_desc['DBInstances']:
        total_db_instaces.append(ins)
    #total_db_instaces.append(rds_desc['DBInstances'])
    print(str(len(total_db_instaces)))
    if 'Marker' in rds_desc:
        print('marker exists')
        next_token = True
        rds_desc = rds.describe_db_instances(
            MaxRecords=80,
            Marker = rds_desc['Marker']
        )

    else:
        next_token = False
        print('marker doesnt exist')

#print(rds_desc)

#input('??????????????')
#total_db_instaces = rds_desc['DBInstances']

#print(len(rds_desc['DBInstances']))

print('total rds instances: ' + str(len(total_db_instaces)))
input('?????ß')

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

