# aws-ebsSnapshotManager
Simple Lambda function written in python that creates snapshots of volumes with retention policy (ebsManager) and copies to DR (ebsManager). Also retains tag information of volume name.

## Installation
Created a new lambda function from scratch with python 2.7 runtime for each script (ebsSnapshotManager.py and ebsSnapshotManagerDR.py).  Zip each script separtely and upload. Created new role or attach existing role with the policy in this repository (ebsSnapshotManagerPolicy.json)

Edit the region variable in ebsSnapshotManagerDR.py as needed

## Usage
Add a tag "Backup" with value "Yes" to the volume that needs to be backed up. Add another tag "Retention" with number of days to keep.  It will automatically be deleted after the number of days set.

Create a Cloudwatch schedule to trigger these events.

Most of the code was based on:
https://github.com/neilspink/aws-ebs-snapshots-lambda
