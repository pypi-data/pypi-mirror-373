"""
S3 Public Access Analyzer - External HTTP testing for bucket accessibility.
"""

import logging

import click
import requests
from botocore.exceptions import ClientError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .commons import display_aws_account_info, get_client, write_to_csv

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

logger = logging.getLogger(__name__)


def check_bucket_public_http_access(bucket_name: str):
    """Check if S3 bucket is accessible via HTTP without credentials."""
    try:
        url = f"https://{bucket_name}.s3.amazonaws.com"
        logger.debug(f"Testing HTTP access to: {url}")

        # Test GET request
        response = requests.get(url, verify=False, timeout=10)

        # Check if bucket responds (200=accessible, 403=exists but protected)
        if response.status_code in [200, 403]:
            logger.info(f"  → Bucket responds: {response.status_code}")

            # Test OPTIONS for additional info
            try:
                options_response = requests.options(url, verify=False, timeout=5)
                cors_info = options_response.headers.get("Access-Control-Allow-Origin", "Not configured")
            except Exception:
                cors_info = "Failed to check"

            return {
                "accessible": True,
                "status_code": response.status_code,
                "content_length": len(response.text),
                "server": response.headers.get("Server", "Unknown"),
                "cors": cors_info,
                "last_modified": response.headers.get("Last-Modified", "Unknown"),
            }
        else:
            logger.debug(f"  → Bucket not accessible: {response.status_code}")
            return {"accessible": False, "status_code": response.status_code}

    except requests.exceptions.RequestException as e:
        logger.debug(f"  → HTTP test failed for {bucket_name}: {e}")
        return {"accessible": False, "error": str(e)}


def get_bucket_list_from_aws():
    """Get list of S3 buckets from AWS API."""
    try:
        s3 = get_client("s3")
        response = s3.list_buckets()
        return [bucket["Name"] for bucket in response.get("Buckets", [])]
    except ClientError as e:
        logger.error(f"Failed to list S3 buckets: {e}")
        return []


@click.command()
@click.option("--bucket-names", help="Comma-separated list of bucket names to test (uses AWS list if not provided)")
@click.option("--output-file", default="s3_public_access_test.csv", help="Output CSV file path")
@click.option("--timeout", default=10, help="HTTP request timeout in seconds")
def analyze_s3_public_access(bucket_names, output_file, timeout):
    """Analyze S3 buckets for public HTTP accessibility."""
    logger.info(f"S3 public access analysis in {display_aws_account_info()}")

    try:
        # Get bucket list
        if bucket_names:
            bucket_list = [name.strip() for name in bucket_names.split(",")]
            logger.info(f"Testing provided buckets: {bucket_list}")
        else:
            logger.info("Getting bucket list from AWS...")
            bucket_list = get_bucket_list_from_aws()

        if not bucket_list:
            logger.warning("No buckets to test")
            return

        logger.info(f"Testing {len(bucket_list)} buckets for public HTTP access")

        # Test each bucket
        results = []
        public_buckets = []

        for i, bucket_name in enumerate(bucket_list, 1):
            logger.info(f"Testing bucket {i}/{len(bucket_list)}: {bucket_name}")

            access_info = check_bucket_public_http_access(bucket_name)

            result = {
                "Bucket Name": bucket_name,
                "HTTP Accessible": access_info.get("accessible", False),
                "Status Code": access_info.get("status_code", "N/A"),
                "Content Length": access_info.get("content_length", 0),
                "Server": access_info.get("server", "Unknown"),
                "CORS Configuration": access_info.get("cors", "Not checked"),
                "Last Modified": access_info.get("last_modified", "Unknown"),
                "Error": access_info.get("error", "None"),
            }

            results.append(result)

            if access_info.get("accessible"):
                public_buckets.append(bucket_name)
                status = access_info.get("status_code")
                if status == 200:
                    logger.warning(f"  ⚠ PUBLICLY READABLE: {bucket_name}")
                elif status == 403:
                    logger.info(f"  ℹ Exists but protected: {bucket_name}")

        # Export results
        write_to_csv(results, output_file)
        logger.info(f"Results exported to: {output_file}")

        # Summary
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Total buckets tested: {len(bucket_list)}")
        logger.info(f"Buckets responding to HTTP: {len(public_buckets)}")

        if public_buckets:
            logger.warning(f"⚠ {len(public_buckets)} buckets are accessible via HTTP:")
            for bucket in public_buckets:
                logger.warning(f"  - {bucket}")
            logger.warning("Review these buckets for unintended public access")
        else:
            logger.info("✓ No buckets found with public HTTP access")

    except Exception as e:
        logger.error(f"Failed to analyze S3 public access: {e}")
        raise


if __name__ == "__main__":
    analyze_s3_public_access()
