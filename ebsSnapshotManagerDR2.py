import boto3
import datetime

source_region = 'us-west-2' 
copy_region = 'us-east-2'
ec = boto3.client('ec2')
addl_ec = boto3.client('ec2', region_name=copy_region)

def lambda_handler(event, context):

    #Get count of concurrent CopySnapshot operation in copy_region
    i = 0
    filters = [
        { 'Name': 'status', 'Values': ['pending'] },
    ]
    snapshot_response = addl_ec.describe_snapshots(Filters=filters)
    for snap in snapshot_response['Snapshots']:
        if i == 5:
            print "\tWARNING Five concurrent CopySnapshot operation in progess, exiting..."
            raise SystemExit
        i = i + 1
 
    filters = [
        { 'Name': 'tag:Type', 'Values': ['Automated'] },
        { 'Name': 'tag:DR', 'Values': ['No'] },
    ]
    snapshot_response = ec.describe_snapshots(Filters=filters)
    for snap in snapshot_response['Snapshots']:
        tags=snap['Tags']
        for tag in tags:
            if tag['Key'] == 'CreatedOn':
                created_on = tag['Value']
            if tag['Key'] == 'DeleteOn':
                delete_on = tag['Value']
            if tag['Key'] == 'Name':
                volume_name = tag['Value']
        if i < 5:
            #Check snapshot status         
            if snap['State'] == 'pending':
                print "\tWARNING: [%s] under creation and will not be copied" % snap['SnapshotId']
                #Mark Snapshot not copied
                ec.create_tags(
                    Resources=[snap['SnapshotId']],
                    Tags=[
                        { 'Key': 'DR', 'Value': 'No' },
                    ]
                )
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
            
            ec.create_tags(
                Resources=[snap['SnapshotId']],
                Tags=[
                    { 'Key': 'DR', 'Value': '' },
                ]
            )
    
            i = i + 1
            print "\tSNAPSHOT [%s] copied from [%s] to [%s]" % ( snap['SnapshotId'], source_region, copy_region )
        else: 
            print "\tWARNING: Five concurrent CopySnapshot operation limit reached, [%s] of [%s] will not be copied" % ( snap['SnapshotId'], volume_name )
            #Mark Snapshot not copied
            ec.create_tags(
                Resources=[snap['SnapshotId']],
                Tags=[
                    { 'Key': 'DR', 'Value': 'No' },
               ]
            )
            continue
    