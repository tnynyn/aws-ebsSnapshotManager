import boto3
import collections
import datetime

source_region = 'us-west-2' 
copy_region = 'us-east-2'
ec2_client = boto3.client('ec2',region_name='us-west-2')
retention_days = 30

def lambda_handler(event, context):
    # Get all volume matching the tag Backup:Yes
    volumes = ec2_client.describe_volumes(Filters = [
           {
               'Name' : "tag-key",
               'Values' : ["Backup"]
           },
           {
               'Name' : "tag-value",
               'Values' : ['Yes']
           }
       ])
       
    to_tag = collections.defaultdict(list)
     
    # Iterate over all volumes with matching tags and create snapshot for the specific volume using volume_id
    for volume in volumes.get('Volumes',[]):
        volume_id = volume.get('VolumeId')
        try:
            retention_days = [
                int(t.get('Value')) for t in volume['Tags']
                if t['Key'] == 'Retention'][0]                                              
        except IndexError:
            retention_days = 30
        
        try:
            volume_name = [
                str(t.get('Value')) for t in volume['Tags']
                if t['Key'] == 'Name'][0] 
        except IndexError:
                volume_name = 'None'
        
        snapshot = ec2_client.create_snapshot(VolumeId = volume_id, Description = "Created by lambda function ebsSnapshotManager")  
        
        if snapshot:
            print "\tSNAPSHOT [%s] created from [%s] [%s]" % ( snapshot['SnapshotId'], volume_name, volume_id )
            to_tag[retention_days].append(snapshot['SnapshotId'])
            #print "\tRetaining SNAPSHOT [%s] for [%d] days" % ( snapshot['SnapshotId'], retention_days )            

        # Tags snapshot to delete on date   
        for retention_days in to_tag.keys():
            delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
            delete_fmt = delete_date.strftime('%Y-%m-%d')
            today_fmt = datetime.date.today().strftime('%Y-%m-%d')

        #print "\tDeleting [%d] SNAPSHOT(S) on [%s]" % (len(to_tag[retention_days]), delete_fmt)
        ec2_client.create_tags(
            Resources=to_tag[retention_days],
            Tags=[
                { 'Key': 'CreatedOn', 'Value': today_fmt },
                { 'Key': 'DeleteOn', 'Value': delete_fmt },
                { 'Key': 'Type', 'Value': 'Automated' },
                { 'Key': 'Name', 'Value': volume_name },
            ]
        )                     
                          
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
        print "\tDeleting SNAPSHOT [%s]" % snapshot['SnapshotId']
        ec2_client.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                
    
