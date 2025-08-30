"""
S3 Bulk Downloader - Download files from S3 with concurrent processing and progress tracking.
"""

import concurrent.futures
import logging
import os
from pathlib import Path

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client

logger = logging.getLogger(__name__)


def download_file(s3, bucket, key, destination, preserve_structure=False):
    """Download a single file from S3 with error handling."""
    try:
        # Determine local file path
        if preserve_structure:
            # Keep S3 directory structure
            local_path = os.path.join(destination, key)
            # Create subdirectories if needed
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
        else:
            # Flatten structure - use just filename
            filename = key.split("/")[-1]
            local_path = os.path.join(destination, filename)

        # Check if file already exists
        if os.path.exists(local_path):
            file_size = os.path.getsize(local_path)
            logger.debug(f"File {local_path} already exists ({file_size} bytes). Skipping.")
            return {"status": "skipped", "key": key, "local_path": local_path, "size": file_size}

        # Download the file
        s3.download_file(bucket, key, local_path)
        file_size = os.path.getsize(local_path)
        logger.info(f"✓ Downloaded: {key} ({file_size} bytes)")

        return {"status": "downloaded", "key": key, "local_path": local_path, "size": file_size}

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "NoSuchKey":
            logger.warning(f"⚠ Key not found: {key}")
        elif error_code == "AccessDenied":
            logger.error(f"✗ Access denied: {key}")
        else:
            logger.error(f"✗ Failed to download {key}: {e}")
        return {"status": "error", "key": key, "error": str(e)}

    except Exception as e:
        logger.error(f"✗ Unexpected error downloading {key}: {e}")
        return {"status": "error", "key": key, "error": str(e)}


def get_object_list(s3, bucket, prefix):
    """Get list of objects to download with error handling."""
    try:
        objects = []
        paginator = s3.get_paginator("list_objects_v2")

        # Use prefix instead of directory for better S3 API alignment
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

        for page in page_iterator:
            if "Contents" in page:
                for obj in page["Contents"]:
                    # Skip directories (keys ending with /)
                    if not obj["Key"].endswith("/"):
                        objects.append({"key": obj["Key"], "size": obj["Size"], "modified": obj["LastModified"]})

        return objects

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "NoSuchBucket":
            logger.error(f"Bucket '{bucket}' does not exist")
        elif error_code == "AccessDenied":
            logger.error(f"Access denied to bucket '{bucket}'")
        else:
            logger.error(f"Failed to list objects in bucket '{bucket}': {e}")
        raise


@click.command()
@click.option("--bucket", required=True, help="S3 bucket name")
@click.option("--prefix", default="", help="S3 prefix/directory path (e.g., 'folder1/subfolder2/')")
@click.option("--destination", default="./downloads", help="Local destination directory")
@click.option("--threads", default=10, help="Number of concurrent download threads")
@click.option("--preserve-structure", is_flag=True, help="Preserve S3 directory structure locally")
@click.option("--dry-run", is_flag=True, help="Show what would be downloaded without actually downloading")
@click.option("--file-pattern", help="Only download files matching this pattern (e.g., '*.pdf')")
def download_files(bucket, prefix, destination, threads, preserve_structure, dry_run, file_pattern):
    """Download files from S3 with concurrent processing and progress tracking."""
    logger.info(f"S3 bulk download from {display_aws_account_info()}")

    try:
        s3 = get_client("s3")

        # Validate bucket access
        logger.info(f"Checking access to bucket: {bucket}")
        try:
            s3.head_bucket(Bucket=bucket)
            logger.info("✓ Bucket access confirmed")
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NotFound":
                logger.error(f"✗ Bucket '{bucket}' not found")
            elif error_code == "Forbidden":
                logger.error(f"✗ Access forbidden to bucket '{bucket}'")
            else:
                logger.error(f"✗ Cannot access bucket '{bucket}': {e}")
            return

        # Create destination directory
        Path(destination).mkdir(parents=True, exist_ok=True)
        logger.info(f"Destination directory: {os.path.abspath(destination)}")

        # Get list of objects to download
        logger.info(f"Listing objects with prefix: '{prefix}'")
        objects = get_object_list(s3, bucket, prefix)

        if not objects:
            logger.warning(f"No objects found with prefix '{prefix}'")
            return

        # Filter by file pattern if specified
        if file_pattern:
            import fnmatch

            original_count = len(objects)
            objects = [obj for obj in objects if fnmatch.fnmatch(obj["key"], file_pattern)]
            logger.info(f"Filtered to {len(objects)} objects matching pattern '{file_pattern}' (from {original_count})")

        if not objects:
            logger.warning("No objects to download after filtering")
            return

        # Calculate total size
        total_size = sum(obj["size"] for obj in objects)
        logger.info(f"Found {len(objects)} files to download ({total_size:,} bytes total)")

        # Show dry-run information
        if dry_run:
            logger.info("DRY-RUN MODE: Files that would be downloaded:")
            for obj in objects[:10]:  # Show first 10
                logger.info(f"  {obj['key']} ({obj['size']:,} bytes)")
            if len(objects) > 10:
                logger.info(f"  ... and {len(objects) - 10} more files")
            logger.info(f"Total: {len(objects)} files, {total_size:,} bytes")
            return

        # Download files concurrently
        logger.info(f"Starting download with {threads} concurrent threads...")

        downloaded_count = 0
        skipped_count = 0
        error_count = 0
        downloaded_size = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            # Submit all download tasks
            future_to_key = {
                executor.submit(download_file, s3, bucket, obj["key"], destination, preserve_structure): obj["key"]
                for obj in objects
            }

            # Process completed downloads
            for future in concurrent.futures.as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    result = future.result()

                    if result["status"] == "downloaded":
                        downloaded_count += 1
                        downloaded_size += result["size"]
                    elif result["status"] == "skipped":
                        skipped_count += 1
                    elif result["status"] == "error":
                        error_count += 1

                    # Progress update every 10 files
                    total_processed = downloaded_count + skipped_count + error_count
                    if total_processed % 10 == 0 or total_processed == len(objects):
                        logger.info(f"Progress: {total_processed}/{len(objects)} files processed")

                except Exception as exc:
                    logger.error(f"✗ Error processing {key}: {exc}")
                    error_count += 1

        # Final summary
        logger.info("\n=== DOWNLOAD SUMMARY ===")
        logger.info(f"Total files: {len(objects)}")
        logger.info(f"Downloaded: {downloaded_count} files ({downloaded_size:,} bytes)")
        logger.info(f"Skipped (existing): {skipped_count}")
        logger.info(f"Errors: {error_count}")

        if error_count == 0:
            logger.info("✅ All downloads completed successfully")
        elif downloaded_count > 0:
            logger.warning(f"⚠ Download completed with {error_count} errors")
        else:
            logger.error("❌ Download failed")

    except Exception as e:
        logger.error(f"Failed to download files: {e}")
        raise


if __name__ == "__main__":
    download_files()
