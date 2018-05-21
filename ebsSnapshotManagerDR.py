import boto3
import datetime

source_region = 'us-west-2' 
copy_region = 'us-east-2'
ec = boto3.client('ec2')
addl_ec = boto3.client('ec2', region_name=copy_region)

def lambda_handler(event, context):

    #Copy snapshot(s) based on snapshots created "today"
    today_fmt = datetime.date.today().strftime('%Y-%m-%d')
    filters = [
        { 'Name': 'tag:CreatedOn', 'Values': [today_fmt] },
        { 'Name': 'tag:Type', 'Values': ['Automated'] },
    ]
    snapshot_response = ec.describe_snapshots(Filters=filters)
    
    for snap in snapshot_response['Snapshots']
        
        tags=snap['Tags']
        for tag in tags:
            if tag['Key'] == 'CreatedOn':
                created_on = tag['Value']
            if tag['Key'] == 'DeleteOn':
                delete_on = tag['Value']
            if tag['Key'] == 'Name':
                volume_name = tag['Value']
        
        #Check snapshot status
        if snap['State'] == 'pending':
            print "\tWARNING: [%s] under creation and will not be copied" % snap['SnapshotId']
            continue
        
        addl_snap = addl_ec.copy_snapshot(
            SourceRegion=source_region,
            SourceSnapshotId=snap['SnapshotId'],
            Description='Original Snapshot ID: ' + snap['SnapshotId'],
            DestinationRegion=copy_region
        )

        addl_ec.create_tags(
            Resources=[addl_snap['SnapshotId']],
            Tags=[
                { 'Key': 'CreatedOn', 'Value': created_on },
                { 'Key': 'DeleteOn', 'Value': delete_on },
                { 'Key': 'Type', 'Value': 'Automated' },
                { 'Key': 'Name', 'Value': volume_name },
            ]
        )
    print "\tSNAPSHOT [%s] copied from [%s] to [%s]" % ( snap['SnapshotId'], source_region, copy_region )
    delete_on = datetime.date.today().strftime('%Y-%m-%d')
        # limit snapshots to process to ones marked for deletion on this day
        # AND limit snapshots to process to ones that are automated only
        # AND exclude automated snapshots marked for permanent retention
    filters = [
        { 'Name': 'tag:DeleteOn', 'Values': [delete_on] },
        { 'Name': 'tag:Type', 'Values': ['Automated'] },
    ]
    snapshot_response = addl_ec.describe_snapshots(Filters=filters)

    for snap in snapshot_response['Snapshots']:
        print "\tDeleting SNAPSHOT %s" % snap['SnapshotId']
        addl_ec.delete_snapshot(SnapshotId=snap['SnapshotId'])
