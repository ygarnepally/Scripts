import boto3
import json
import os
from boto3.dynamodb.conditions import Key, Attr


# region = input('RegionName:\t')

# accounts = ['wdpr-apps','wdpr-apps-pilot','dcl-apps-dev','dcl-apps-test','dcl-apps-prod','nvo-apps-dev','nvo-apps-test','nvo-apps-prod','shdr-apps-dev','wdpr-ee-dev','wdpr-ee-test','wdpr-ee-prod','wdpr-packaging-dev','wdpr-packaging-test', 'wdpr-packaging-prod','wdpr-fastpass-dev','wdpr-fastpass-test','wdpr-fastpass-prod','wdpr-ecommerce-dev','wdpr-ecommerce-test','wdpr-ecommerce-prod','wdpr-revmgmt-dev','wdpr-revmgmt-test','wdpr-revmgmt-prod', 'wdpr-cast-dev','wdpr-cast-test','wdpr-cast-prod','wdpr-ticketing-dev','wdpr-ticketing-test','wdpr-ticketing-prod','wdpr-lodging-dev','wdpr-lodging-test','wdpr-lodging-prod','wdpr-gam-dev','wdpr-gam-test', 'wdpr-gam-prod','wdpr-dpi-dev','wdpr-dpi-test','wdpr-dpi-prod','hkdl-apps-dev','hkdl-apps-test','hkdl-apps-prod']
# accounts = ['wdpr-apps-pilot','dcl-apps-dev','dcl-apps-test','dcl-apps-prod','nvo-apps-dev','nvo-apps-test','nvo-apps-prod','shdr-apps-dev','wdpr-ee-dev','wdpr-ee-test','wdpr-ee-prod','wdpr-packaging-dev','wdpr-packaging-test', 'wdpr-packaging-prod','wdpr-fastpass-dev','wdpr-fastpass-test','wdpr-fastpass-prod','wdpr-ecommerce-dev','wdpr-ecommerce-test','wdpr-ecommerce-prod','wdpr-revmgmt-dev','wdpr-revmgmt-test','wdpr-revmgmt-prod', 'wdpr-cast-dev','wdpr-cast-test','wdpr-cast-prod','wdpr-ticketing-dev','wdpr-ticketing-test','wdpr-ticketing-prod','wdpr-lodging-dev','wdpr-lodging-test','wdpr-lodging-prod','wdpr-gam-dev','wdpr-gam-test', 'wdpr-gam-prod','wdpr-dpi-dev','wdpr-dpi-test','wdpr-dpi-prod','hkdl-apps-dev','hkdl-apps-test','hkdl-apps-prod']
accounts = ['wdpr-sandbox', 'ra-sandbox']


regions = ['us-east-1', 'us-west-2', 'ap-northeast-1', 'eu-west-1']


# file = open('rds-instances-tags.csv', 'w+')
# file.write("dbidentifier,bag,pace_env,bappp-id,instance_type,engine,storage,storage_type,multi_az,public,iops,StorageEncrypted,Region,Account")
# file.write("\n")

db = boto3.client('dynamodb')


for account in accounts:

  session = boto3.Session(profile_name=account)

  regions = ['us-east-1', 'us-west-2', 'ap-northeast-1', 'eu-west-1']
  
  try:
    for region in regions:
      try:

        rds = session.client('rds', region_name=region)
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
        
        for instance in instances:
          try:
            arn = instance['DBInstanceArn']
            identifier = instance['DBInstanceIdentifier'].split(':  ')[-1]
            instance_type = instance['DBInstanceClass']
            engine = instance['Engine']
            storage = instance['AllocatedStorage']
            storage_type = instance['StorageType']
            multi_az = instance['MultiAZ']
            public = instance['PubliclyAccessible']
            StorageEncrypted = instance['StorageEncrypted']
            iops = instance['Iops'] if 'Iops' in instance else 'NA'


            tags = rds.list_tags_for_resource(
                ResourceName=arn
            )
            if tags['TagList']:
                bag = [tag['Value'] for tag in tags['TagList'] if tag['Key'] == 'bag']
                bag = ''.join(bag) if bag else 'NA'
                bapp_id = [tag['Value'] for tag in tags['TagList'] if tag['Key'] == 'bapp_id']
                bapp_id = ''.join(bapp_id) if bapp_id else 'NA'
                pace_bapp_id = [tag['Value'] for tag in tags['TagList'] if tag['Key'] == 'pace_bapp_id']
                pace_bapp_id = ''.join(pace_bapp_id) if pace_bapp_id else 'NA'
                pace_name_node_id = [tag['Value'] for tag in tags['TagList'] if tag['Key'] == 'pace_name_node_id']
                pace_name_node_id = ''.join(pace_name_node_id) if pace_name_node_id else 'NA'
                pace_env = [tag['Value'] for tag in tags['TagList'] if tag['Key'] == 'pace_env']
                pace_env = ''.join(pace_env) if pace_env else 'NA'
                pace_eo = [tag['Value'] for tag in tags['TagList'] if tag['Key'] == 'pace_eo']
                pace_eo = ''.join(pace_eo) if pace_eo else 'NA'

            # else:
            #     bag = 'NA'
            #     bapp_id = 'NA'
            #     pace_env = 'NA'


            print('updating dynamodb for records..')
            item_dict = {
                'RDS_Name': { "S": identifier},
                'pace_env': { "S": pace_env },
                'bapp_id': {"S": bapp_id },
                'pace_bapp_id': { "S": pace_bapp_id},
                'pace_eo' : { "S": pace_eo},
                'pace_name_node_id' : { "S": pace_name_node_id},
                'Account' : { "S": account},
                'Region' : { "S": region},
                }
            response = db.put_item(
                TableName = 'PaCE-RDS-pace-tags',
                Item=item_dict
                )
            
            # input('????????????')
            
            print(identifier + '\t' + region  + '\t' + account)
            print(StorageEncrypted)
            
            # file.write(identifier + ',' + bag + ',' + pace_env + ',' + bapp_id + ',' + instance_type + ',' + engine + ',' + str(storage) + ',' + str(storage_type) + ',' + str(multi_az) + ',' + str(public) + ',' + str(iops) + ',' + str(StorageEncrypted) + ',' + str(region)  + ',' + str(account)  + "\n")

          except Exception as e:
            print('-------------------------------------------------------------')
            print(e) 
            print('-------------------------------------------------------------')

        # file.close()
      except Exception as e:
          print('-------------------------------------------------------------')
          print(e) 
          print('-------------------------------------------------------------')
  except Exception as e:
    print('-------------------------------------------------------------')
    print(e) 
    print('-------------------------------------------------------------')

# file.close()
