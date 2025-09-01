"""
S3 Bucket Inventory - List and analyze S3 bucket configurations.
"""

import logging

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_bucket_policy, get_client, write_to_csv

logger = logging.getLogger(__name__)


@click.command()
@click.option("--output-file", default="s3_buckets.csv", help="Output CSV file path")
@click.option("--include-versioning", is_flag=True, help="Include versioning status in analysis")
@click.option("--include-encryption", is_flag=True, help="Include encryption status in analysis")
def list_buckets(output_file, include_versioning, include_encryption):
    """List all S3 buckets with policy and configuration analysis."""
    logger.info(f"Listing S3 buckets in {display_aws_account_info()}")

    try:
        s3 = get_client("s3")
        response = s3.list_buckets()
        buckets = response.get("Buckets", [])

        if not buckets:
            logger.info("No S3 buckets found")
            return

        logger.info(f"Found {len(buckets)} S3 buckets to analyze")

        data = []
        for i, bucket in enumerate(buckets, 1):
            bucket_name = bucket["Name"]
            creation_date = bucket.get("CreationDate", "Unknown")

            logger.info(f"Analyzing bucket {i}/{len(buckets)}: {bucket_name}")

            try:
                # Get bucket region
                location_response = s3.get_bucket_location(Bucket=bucket_name)
                bucket_region = location_response.get("LocationConstraint") or "us-east-1"

                # Get bucket policy and public access block
                policy, public_access_block = get_bucket_policy(bucket_name)

                bucket_data = {
                    "BucketName": bucket_name,
                    "Region": bucket_region,
                    "CreationDate": creation_date.strftime("%Y-%m-%d")
                    if hasattr(creation_date, "strftime")
                    else str(creation_date),
                    "HasPolicy": "Yes" if policy else "No",
                    "PublicAccessBlock": public_access_block,
                }

                # Add versioning status if requested
                if include_versioning:
                    try:
                        versioning_response = s3.get_bucket_versioning(Bucket=bucket_name)
                        versioning_status = versioning_response.get("Status", "Disabled")
                        bucket_data["VersioningStatus"] = versioning_status
                        logger.debug(f"  Versioning: {versioning_status}")
                    except ClientError as e:
                        bucket_data["VersioningStatus"] = "Error"
                        logger.debug(f"  Could not get versioning status: {e}")

                # Add encryption status if requested
                if include_encryption:
                    try:
                        encryption_response = s3.get_bucket_encryption(Bucket=bucket_name)
                        encryption_rules = encryption_response.get("ServerSideEncryptionConfiguration", {}).get(
                            "Rules", []
                        )
                        if encryption_rules:
                            # Get the first encryption rule
                            sse_algorithm = (
                                encryption_rules[0]
                                .get("ApplyServerSideEncryptionByDefault", {})
                                .get("SSEAlgorithm", "Unknown")
                            )
                            bucket_data["EncryptionStatus"] = f"Enabled ({sse_algorithm})"
                        else:
                            bucket_data["EncryptionStatus"] = "Enabled (Unknown algorithm)"
                        logger.debug(f"  Encryption: {bucket_data['EncryptionStatus']}")
                    except ClientError as e:
                        error_code = e.response.get("Error", {}).get("Code", "Unknown")
                        if error_code == "ServerSideEncryptionConfigurationNotFoundError":
                            bucket_data["EncryptionStatus"] = "Disabled"
                            logger.debug(f"  Encryption: Disabled")
                        else:
                            bucket_data["EncryptionStatus"] = "Error"
                            logger.debug(f"  Could not get encryption status: {e}")

                # Log summary for this bucket
                policy_status = "with policy" if policy else "no policy"
                pab_status = public_access_block if public_access_block else "no PAB"
                logger.info(f"  → {bucket_region}, {policy_status}, {pab_status}")

                data.append(bucket_data)

            except ClientError as e:
                logger.error(f"  ✗ Failed to analyze bucket {bucket_name}: {e}")
                # Add minimal data for failed analysis
                data.append({"BucketName": bucket_name, "Region": "Error", "Error": str(e)})

        # Export results
        write_to_csv(data, output_file)
        logger.info(f"S3 bucket inventory exported to: {output_file}")

        # Summary
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Total buckets: {len(buckets)}")

        if data:
            buckets_with_policy = sum(1 for b in data if b.get("HasPolicy") == "Yes")
            logger.info(f"Buckets with policies: {buckets_with_policy}")

            # Region distribution
            regions = {}
            for bucket in data:
                region = bucket.get("Region", "Unknown")
                regions[region] = regions.get(region, 0) + 1

            logger.info("Region distribution:")
            for region, count in sorted(regions.items()):
                logger.info(f"  {region}: {count} buckets")

            if include_encryption:
                encrypted_buckets = sum(1 for b in data if b.get("EncryptionStatus", "").startswith("Enabled"))
                logger.info(f"Encrypted buckets: {encrypted_buckets}")

            if include_versioning:
                versioned_buckets = sum(1 for b in data if b.get("VersioningStatus") == "Enabled")
                logger.info(f"Versioned buckets: {versioned_buckets}")

    except Exception as e:
        logger.error(f"Failed to list S3 buckets: {e}")
        raise
