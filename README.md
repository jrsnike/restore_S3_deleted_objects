This script was based on the restore-s3-deleted-objects project
https://github.com/aws-samples/restore-s3-deleted-objects

Restore accidentally deleted files from Amazon S3

When should you use this script?
The script is designed to help users restore files that have been accidentally deleted from Amazon S3.

Restore files from all buckets:

This script loops through all files in all buckets in an AWS account. If the files were deleted after a specific point in time (point_of_restore), the script restores the files to their most recent state.

Restore files from a specific bucket:

This script loops through all files in a specific bucket, or a folder within that bucket, in an AWS account. If the files were deleted after a specific point in time (point_of_restore), the script restores the files to their most recent state.

Prerequisites

Attention! For this script to work, versioning must have been enabled on the Amazon S3 bucket before files were deleted.
Edit the chosen script to set the BUCKET_NAME variable,
MAX_BATCH_SIZE and START_DATE. It should represent the date and time of the incident. Be sure to round down so you don't miss any files.
Then, during execution, you will be asked to enter the PREFIX (Folder) in the bucket to be restored. If left blank, it scrolls through the entire bucket.

How to run this script

To run this Python 3 script, you will need a user with the permissions described in this IAM policy.
There are a few options for running this script. We describe two possibilities below. Choose the one that best suits your needs:

1) If you have access to the AWS console.
   Access the AWS Cloud Shell - For more information about AWS Cloud Shell: https://aws.amazon.com/cloudshell/

   Clone this GitHub repository.
   git clone https://github.com/jrsnike/restore_S3_deleted_objects

   Run the desired script. Example:
   cd restore_s3_deleted_objects/
   python3 restore_s3_objects_us.py

2) If you have access key and secret key credentials:
   If you have the AWS CLI configured, you can ignore this. Otherwise, configure the AWS CLI in a command-line tool/terminal.

   Clone this GitHub repository.
   git clone https://github.com/jrsnike/restore_S3_deleted_objects

   Run the desired script. Example:
   cd restore_s3_deleted_objects/
   python3 restore_s3_objects_us.py

Costs:

This script executes requests made to Amazon S3 buckets and files, such as GET, LIST, and PUT. Costs will vary depending on how many objects and buckets a customer is restoring. 
For more details on Amazon S3 pricing, take a look at the Amazon S3 pricing page
