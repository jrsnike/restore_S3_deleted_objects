# Initial settings
BUCKET_NAME = ""       # Enter the bucket name
START_DATE = datetime.fromisoformat("2025-01-19T00:00:00+00:00")  # Enter the date from which restoration will start
MAX_BATCH_SIZE = 1000  # Maximum number of objects per delete call

# S3 Client
s3_client = boto3.client("s3")

# Ask the user for the prefix (folder)
PREFIX = input("Enter the prefix (folder) in the bucket (leave empty to consider the entire bucket): ")  # Enter the folder to be restored or leave blank for the entire bucket

# Retrieve delete markers
try:
    print(f"Retrieving delete markers in bucket {BUCKET_NAME}...")

    params = {
        "Bucket": BUCKET_NAME
    }

    if PREFIX:
        params["Prefix"] = PREFIX

    delete_markers = []

    while True:
        response = s3_client.list_object_versions(**params)
        markers = response.get("DeleteMarkers", [])

        # Filter markers by LastModified
        for marker in markers:
            if marker["LastModified"].replace(tzinfo=timezone.utc) > START_DATE:
                delete_markers.append({
                    "Key": marker["Key"],
                    "VersionId": marker["VersionId"]
                })

        # Check if there are more pages
        if response.get("IsTruncated"):
            params["KeyMarker"] = response.get("NextKeyMarker")
            params["VersionIdMarker"] = response.get("NextVersionIdMarker")
        else:
            break

except (BotoCoreError, ClientError) as error:
    print(f"Error retrieving delete markers: {error}")
    exit(1)

if not delete_markers:
    print(f"No delete markers found after {START_DATE} for prefix '{PREFIX}'.")
    exit(0)

# Display the total number of delete markers
total_markers = len(delete_markers)
print(f"Total delete markers found: {total_markers}")

# Remove delete markers in batches
print("Removing delete markers...")
batch = []
removed_count = 0

try:
    for marker in delete_markers:
        batch.append(marker)

        if len(batch) >= MAX_BATCH_SIZE:
            delete_json = {"Objects": batch}
            s3_client.delete_objects(Bucket=BUCKET_NAME, Delete=delete_json)

            removed_count += len(batch)
            percent_complete = (removed_count / total_markers) * 100
            print(f"\rProgress: {percent_complete:.2f}% ({removed_count}/{total_markers}) completed.", end="")

            batch.clear()

    # If there are remaining objects in the batch, perform the final delete
    if batch:
        delete_json = {"Objects": batch}
        s3_client.delete_objects(Bucket=BUCKET_NAME, Delete=delete_json)

        removed_count += len(batch)
        percent_complete = (removed_count / total_markers) * 100
        print(f"Progress: {percent_complete:.2f}% ({removed_count}/{total_markers}) completed.")

    print("Restore completed!")

except (BotoCoreError, ClientError) as error:
    print(f"Error deleting objects: {error}")
    exit(1)
