# aws-ebsSnapshotManager
Simple Lambda function written in python that creates snapshots of volumes with retention policy (ebsSnapshotManager) and copies to DR (ebsSnapshotManagerDR). Also retains tag information of volume name.

## Installation
- Created a new lambda function from scratch with python 2.7 runtime for each script (ebsSnapshotManager.py and ebsSnapshotManagerDR.py)  - Zip each script separately and upload to lambda
- Created new role or attach existing role with the policy in this repository (ebsSnapshotManagerPolicy.json)

Edit the region variable in ebsSnapshotManagerDR.py as needed

## Usage
Add a tag "Backup" with value "Yes" (case-sensitive) to the volume that needs to be backed up.
Add another tag "Retention" with number of days to keep (default is 30 days).  It will automatically be deleted after the number of days set. 

Create a Cloudwatch schedule to trigger these events, make sure to set the schedule for ebsSnapshotManagerDR to run after the  ebsSnapshotManager function as snapshots need to be completed otherwise it will error out in the DR region.

For notifications, you can set up a SNS topic and create a CloudWatch rule to trigger on EC2 snapshot creation and copy events with result "failed".

## Credits and Thanks To:
https://github.com/neilspink/aws-ebs-snapshots-lambda  (as most of the code was based on this)

## Issues? Suggestions? Improvements?
Sorry if I left out some details, new to this.  Let me know if there are any issues, suggestions, improvements for this function.  Thanks!
