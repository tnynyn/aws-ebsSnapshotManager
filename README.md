# aws-ebsSnapshotManager
Lambda function that creates snapshots of volumes, sets retention period, deletes snapshots based on retention period, marks them to be copied to the DR region, and copies to DR

12/17/2019: Updated print syntax for python3\
03/26/2019: Added another script for those who do not want to use a DR region (ebsSnapshotManagerNODR.py)


## Installation
- Created a new lambda function from scratch with python 2.7 runtime for each script: ebsSnapshotManager.py, ebsSnapshotManagerDR.py
- Zip each script separately and upload to lambda (set timeout to 30 seconds and memory to 128MB)
- Create new role or attach existing role with the policy in this repository (ebsSnapshotManagerPolicy.json)
- Edit the region variable (source_region and copy_region) to match your region (i.e. 'us-west-2' for Oregon).  See: https://docs.aws.amazon.com/general/latest/gr/rande.html

## Usage
Each volume needs two tags for it to be setup for automatic snapshot handling:
- Add tag "Backup" with value "Yes" (case-sensitive) to the volume(s) that needs to be snapshotted
- Add tag "Retention" with number of days to keep (default is 30 days) to volume(s)
- Create TWO Cloudwatch>Events>Rule to trigger/schedule these events, make sure run these functions in the following order:
  1. ebsSnapshotManager.py  = Run this FIRST, once per day. It will create snapshots in source_region, mark snapshots to be copied to DR, and deletes snapshots based on retention period (both regions)
  2. ebsSnapshotManagerDR.py  = Run this SECOND. It will copy marked snapshots to DR (copy_region) and unmarks those snapshots copied so it wont be copied again. Schedule another trigger if there are more than 5 snapshots to be copied to the DR region, see note below.

## Usage WITHOUT DR region
Each volume needs two tags for it to be setup for automatic snapshot handling:
- Add tag "Backup" with value "Yes" (case-sensitive) to the volume(s) that needs to be snapshotted
- Add tag "Retention" with number of days to keep (default is 30 days) to volume(s)
- Create a Cloudwatch>Events>Rule to trigger/schedule the event



## Notes
- AWS has a limitation of five concurrent CopySnapshot operations to the DR region. ebsSnapshotManagerDR.py will stop if there are five operations in progess.  You can set it to run again on a schedule until all snapshots are copied over
