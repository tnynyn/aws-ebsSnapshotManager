import boto3
import collections
import datetime
source_region = 'us-west-2' 
copy_region = 'us-east-2'
ec2_client = boto3.client('ec2',region_name=source_region)
ec2_resource = boto3.resource('ec2')
addl_ec = boto3.client('ec2', region_name=copy_region)

def lambda_handler(event, context):
    # Get all volume matching the tag Backup:Yes
    volumes = ec2_client.describe_volumes(Filters = [
           { 'Name' : "tag-key", 'Values' : ["Backup"] },
           { 'Name' : "tag-value", 'Values' : ['Yes'] }
       ])
    for volume in volumes['Volumes']:
        volume_id = volume['VolumeId']        
        # Create snapshot
        snapshot = ec2_client.create_snapshot(VolumeId = volume_id, Description = "Created by lambda function ebsSnapshotManager") 
        snapshot_id = snapshot['SnapshotId']       
        # Get snapshot tag info
        snap = ec2_resource.Snapshot(snapshot['SnapshotId'])
        volume_name = ''
        retention_days = int(30)
        for tags in volume['Tags']:
            if tags["Key"] == 'Name':
                volume_name = tags["Value"]               
            if tags["Key"] == 'Retention':
                retention_days = int(tags["Value"])
        #Tags snapshot            
        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%Y-%m-%d')
        today_fmt = datetime.date.today().strftime('%Y-%m-%d')        
        snap.create_tags(
            Tags=[
                { 'Key': 'CreatedOn', 'Value': today_fmt },
                { 'Key': 'DeleteOn', 'Value': delete_fmt },
                { 'Key': 'Type', 'Value': 'Automated' },
                { 'Key': 'Name', 'Value': volume_name },
                { 'Key': 'DR', 'Value': 'No' }
            ]
        )        
        print "\tSNAPSHOT [%s] created for [%s]:[%s]" % (snapshot_id, volume_name, volume_id)             
    # Deletes snapshot based on "delete_on" date for PR and DR regions 
    delete_on = datetime.date.today().strftime('%Y-%m-%d')
    filters = [
        { 'Name': 'tag:DeleteOn', 'Values': [delete_on] },
        { 'Name': 'tag:Type', 'Values': ['Automated'] },
    ]
    snapshot_response = ec2_client.describe_snapshots(Filters=filters)       
    for snapshot in snapshot_response['Snapshots']:
        ec2_client.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
        print "\tSNAPSHOT [%s] deleted due to retention policy" % (snapshot['SnapshotId'])           
    snapshot_responseDR = addl_ec.describe_snapshots(Filters=filters)
    for snapshotDR in snapshot_responseDR['Snapshots']:
        addl_ec.delete_snapshot(SnapshotId=snapshotDR['SnapshotId'])
        print "\tSNAPSHOT_DR [%s] deleted due to retention policy" % (snapshotDR['SnapshotId'])
