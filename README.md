# aws-ebsSnapshotManager
Simple Lambda function written in python that creates snapshots of volumes with retention policy (ebsSnapshotManager) and copies to DR (ebsSnapshotManagerDR). Also retains tag information of volume name.

## Installation
Created a new lambda function from scratch with python 2.7 runtime for each script (ebsSnapshotManager.py and ebsSnapshotManagerDR.py).  Zip each script separtely and upload. Created new role or attach existing role with the policy in this repository (ebsSnapshotManagerPolicy.json)

Edit the region variable in ebsSnapshotManagerDR.py as needed

## Usage
Add a tag "Backup" with value "Yes" to the volume that needs to be backed up.
Add another tag "Retention" with number of days to keep.  It will automatically be deleted after the number of days set.

Create a Cloudwatch schedule to trigger these events, make sure to set the schedule for ebsSnapshotManagerDR to run after the  ebsSnapshotManager function as snapshots need to be completed otherwise it will error out in the DR region.

## Credits and Thanks To:

https://github.com/neilspink/aws-ebs-snapshots-lambda  (as most of the code was based on this)

## Issues? Suggestions? Improvements?
Sorry if I left out some details, new to this.  Let me know if there are any issues, suggestions, improvements for this function.  Thanks!
