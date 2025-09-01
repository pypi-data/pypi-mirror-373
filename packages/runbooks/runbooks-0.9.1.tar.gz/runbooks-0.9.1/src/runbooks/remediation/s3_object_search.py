"""
S3 Object Search - Find objects across all S3 buckets with advanced search capabilities.
"""

import logging

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client, write_to_csv

logger = logging.getLogger(__name__)


def search_objects_in_bucket(s3_client, bucket_name, search_term, case_sensitive=False, exact_match=False):
    """Search for objects in a specific bucket with various matching options."""
    try:
        found_objects = []
        paginator = s3_client.get_paginator("list_objects_v2")

        logger.debug(f"Searching in bucket: {bucket_name}")

        for page in paginator.paginate(Bucket=bucket_name):
            objects = page.get("Contents", [])

            for obj in objects:
                key = obj["Key"]

                # Apply search logic based on options
                if exact_match:
                    # Exact filename match (not the full key path)
                    filename = key.split("/")[-1]
                    match = (search_term == filename) if case_sensitive else (search_term.lower() == filename.lower())
                else:
                    # Substring search
                    match = (search_term in key) if case_sensitive else (search_term.lower() in key.lower())

                if match:
                    found_objects.append(
                        {
                            "bucket": bucket_name,
                            "key": key,
                            "size": obj.get("Size", 0),
                            "last_modified": obj.get("LastModified"),
                            "storage_class": obj.get("StorageClass", "STANDARD"),
                        }
                    )

        if found_objects:
            logger.info(f"  → Found {len(found_objects)} matching objects")
        else:
            logger.debug(f"  → No matching objects found")

        return found_objects

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "AccessDenied":
            logger.warning(f"  ⚠ Access denied to bucket: {bucket_name}")
        elif error_code == "NoSuchBucket":
            logger.warning(f"  ⚠ Bucket does not exist: {bucket_name}")
        else:
            logger.error(f"  ✗ Error accessing bucket {bucket_name}: {e}")
        return []

    except Exception as e:
        logger.error(f"  ✗ Unexpected error with bucket {bucket_name}: {e}")
        return []


def get_bucket_list(s3_client, bucket_filter=None):
    """Get list of S3 buckets with optional filtering."""
    try:
        response = s3_client.list_buckets()
        buckets = response.get("Buckets", [])

        if bucket_filter:
            original_count = len(buckets)
            buckets = [b for b in buckets if bucket_filter.lower() in b["Name"].lower()]
            logger.info(f"Filtered to {len(buckets)} buckets matching '{bucket_filter}' (from {original_count})")

        return [bucket["Name"] for bucket in buckets]

    except ClientError as e:
        logger.error(f"Failed to list buckets: {e}")
        raise


@click.command()
@click.option("--search-term", required=True, help="Object name or prefix to search for")
@click.option("--bucket-filter", help="Only search buckets containing this string in their name")
@click.option("--case-sensitive", is_flag=True, help="Perform case-sensitive search")
@click.option("--exact-match", is_flag=True, help="Match exact filename (not substring)")
@click.option("--output-file", default="s3_search_results.csv", help="Output CSV file path")
@click.option("--max-buckets", type=int, help="Limit search to first N buckets (for testing)")
def s3_object_search(search_term, bucket_filter, case_sensitive, exact_match, output_file, max_buckets):
    """Search for objects across all S3 buckets with advanced filtering options."""
    logger.info(f"S3 object search in {display_aws_account_info()}")

    try:
        s3_client = get_client("s3")

        # Get list of buckets to search
        logger.info("Getting list of S3 buckets...")
        bucket_names = get_bucket_list(s3_client, bucket_filter)

        if not bucket_names:
            logger.warning("No buckets found to search")
            return

        # Apply bucket limit if specified
        if max_buckets and max_buckets < len(bucket_names):
            bucket_names = bucket_names[:max_buckets]
            logger.info(f"Limited search to first {max_buckets} buckets")

        logger.info(f"Searching {len(bucket_names)} buckets for: '{search_term}'")
        if case_sensitive:
            logger.info("Search mode: Case-sensitive")
        if exact_match:
            logger.info("Search mode: Exact filename match")

        # Search all buckets
        all_found_objects = []
        successful_searches = 0
        failed_searches = 0

        for i, bucket_name in enumerate(bucket_names, 1):
            logger.info(f"Searching bucket {i}/{len(bucket_names)}: {bucket_name}")

            found_objects = search_objects_in_bucket(s3_client, bucket_name, search_term, case_sensitive, exact_match)

            if found_objects is not None:  # None indicates error, empty list is valid
                all_found_objects.extend(found_objects)
                successful_searches += 1
            else:
                failed_searches += 1

        # Process results
        if all_found_objects:
            logger.info(f"\n🎯 SEARCH RESULTS: Found {len(all_found_objects)} matching objects")

            # Group by bucket for summary
            bucket_counts = {}
            total_size = 0

            for obj in all_found_objects:
                bucket = obj["bucket"]
                bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
                total_size += obj.get("size", 0)

            logger.info("Objects found per bucket:")
            for bucket, count in sorted(bucket_counts.items()):
                logger.info(f"  {bucket}: {count} objects")

            logger.info(f"Total size: {total_size:,} bytes")

            # Prepare data for CSV export
            csv_data = []
            for obj in all_found_objects:
                csv_data.append(
                    {
                        "Bucket": obj["bucket"],
                        "ObjectKey": obj["key"],
                        "Filename": obj["key"].split("/")[-1],
                        "Size": obj["size"],
                        "LastModified": obj["last_modified"].strftime("%Y-%m-%d %H:%M:%S")
                        if obj["last_modified"]
                        else "Unknown",
                        "StorageClass": obj["storage_class"],
                        "Directory": "/".join(obj["key"].split("/")[:-1]) if "/" in obj["key"] else "",
                    }
                )

            # Export results
            write_to_csv(csv_data, output_file)
            logger.info(f"Search results exported to: {output_file}")

            # Show sample results
            logger.info("\nSample results (first 5):")
            for i, obj in enumerate(all_found_objects[:5]):
                logger.info(f"  {i + 1}. s3://{obj['bucket']}/{obj['key']} ({obj['size']:,} bytes)")

        else:
            logger.info(f"❌ No objects found matching '{search_term}'")

        # Summary
        logger.info("\n=== SEARCH SUMMARY ===")
        logger.info(f"Buckets searched: {successful_searches}")
        logger.info(f"Search failures: {failed_searches}")
        logger.info(f"Total objects found: {len(all_found_objects)}")

        if failed_searches > 0:
            logger.warning(f"⚠ {failed_searches} buckets could not be searched (access denied or errors)")

    except Exception as e:
        logger.error(f"Failed to search S3 objects: {e}")
        raise


if __name__ == "__main__":
    s3_object_search()
