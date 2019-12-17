import boto3
import collections
import datetime

source_region = 'us-west-2' 
copy_region = 'us-east-2'
ec2_client = boto3.client('ec2',region_name='us-west-2')
ec2_resource = boto3.resource('ec2')

def lambda_handler(event, context):
    # Get all volume matching the tag Backup:Yes
    volumes = ec2_client.describe_volumes(Filters = [
           { 'Name' : "tag-key", 'Values' : ["Backup"] },
           { 'Name' : "tag-value", 'Values' : ['Yes'] }
       ])
       
    # Iterate over all volumes with matching tags
    for volume in volumes['Volumes']:
        volume_id = volume['VolumeId']
        
        # Create snapshot
        snapshot = ec2_client.create_snapshot(VolumeId = volume_id, Description = "Created by lambda function ebsSnapshotManager") 
        snapshot_id = snapshot['SnapshotId']
        
        # Get snapshot tag info
        snap = ec2_resource.Snapshot(snapshot['SnapshotId'])
        if 'Tags' in volume:
            for tags in volume['Tags']:
                if tags["Key"] == 'Name':
                    volume_name = tags["Value"]
                
                try:
                    if tags["Key"] == 'Retention':
                        retention_days = int(tags["Value"])
                except ValueError:
                    retention_days = int(30)

        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%Y-%m-%d')
        today_fmt = datetime.date.today().strftime('%Y-%m-%d')
        
        #Tags snapshot
        snap.create_tags(
            Tags=[
                { 'Key': 'CreatedOn', 'Value': today_fmt },
                { 'Key': 'DeleteOn', 'Value': delete_fmt },
                { 'Key': 'Type', 'Value': 'Automated' },
                { 'Key': 'Name', 'Value': volume_name }
            ]
        )
        
        print ("SNAPSHOT %s created for %s : %s" % (snapshot_id, volume_name, volume_id)

        # Deletes snapshot based on "delete_on" date for primary region 
        delete_on = datetime.date.today().strftime('%Y-%m-%d')
            # limit snapshots to process to ones marked for deletion on this day
            # AND limit snapshots to process to ones that are automated only
            # AND exclude automated snapshots marked for permanent retention
        filters = [
            { 'Name': 'tag:DeleteOn', 'Values': [delete_on] },
            { 'Name': 'tag:Type', 'Values': ['Automated'] },
        ]
        snapshot_response = ec2_client.describe_snapshots(Filters=filters)       
        for snapshot in snapshot_response['Snapshots']:
            ec2_client.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
            print ("SNAPSHOT %s deleted due to retention policy" % (snapshot['SnapshotId'])
