"""
Enterprise-Grade S3 Operations Module.

Comprehensive S3 resource management with Lambda support, environment configuration,
validation utilities, and full compatibility with original AWS Cloud Foundations scripts.

Migrated and enhanced from:
- aws/s3_create_bucket.py (with bucket validation and region-specific creation)
- aws/s3_object_operations.py (with Lambda handlers and ACL support)
- aws/s3_list_objects.py (with pagination and filtering)
- aws/s3_list_buckets.py (with comprehensive listing)

Author: CloudOps DevOps Engineer
Date: 2025-01-21
Version: 2.0.0 - Enterprise Enhancement
"""

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from loguru import logger
from rich.console import Console

from runbooks.operate.base import BaseOperation, OperationContext, OperationResult, OperationStatus

# Initialize Rich console for enhanced CLI output
console = Console()


class S3Operations(BaseOperation):
    """
    Enterprise-grade S3 resource operations and lifecycle management.

    Handles all S3-related operational tasks including bucket management,
    object operations, storage lifecycle management, and comprehensive validation.
    Supports environment variable configuration and AWS Lambda execution.
    """

    service_name = "s3"
    supported_operations = {
        "create_bucket",
        "delete_bucket",
        "put_object",
        "delete_object",
        "copy_object",
        "list_objects",
        "list_buckets",
        "set_bucket_policy",
        "set_bucket_versioning",
        "set_bucket_encryption",
        "set_lifecycle_configuration",
        "empty_bucket",
        "delete_bucket_and_objects",
        "set_public_access_block",
        "get_public_access_block",
        "sync_objects",
        "find_buckets_without_lifecycle",
        "add_lifecycle_policy_bulk",
        "get_bucket_lifecycle",
        "analyze_lifecycle_compliance",
    }
    requires_confirmation = True

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None, dry_run: bool = False):
        """
        Initialize S3 operations with enhanced configuration support.

        Args:
            profile: AWS profile name (can be overridden by AWS_PROFILE env var)
            region: AWS region (can be overridden by AWS_REGION env var)
            dry_run: Dry run mode (can be overridden by DRY_RUN env var)
        """
        # Environment variable support for Lambda/Container deployment
        self.profile = profile or os.getenv("AWS_PROFILE")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.dry_run = dry_run or os.getenv("DRY_RUN", "false").lower() == "true"

        super().__init__(self.profile, self.region, self.dry_run)

    def validate_bucket_name(self, bucket_name: str) -> None:
        """
        Validates an S3 bucket name based on AWS naming rules.

        Based on original aws/s3_create_bucket.py validation.

        Args:
            bucket_name: The bucket name to validate

        Raises:
            ValueError: If the bucket name is invalid
        """
        # AWS Bucket Naming Rules
        if len(bucket_name) < 3 or len(bucket_name) > 63:
            raise ValueError("Bucket name must be between 3 and 63 characters long.")

        if not re.match(r"^[a-z0-9.-]+$", bucket_name):
            raise ValueError("Bucket name can only contain lowercase letters, numbers, hyphens (-), and periods (.).")

        if bucket_name.startswith(".") or bucket_name.endswith("."):
            raise ValueError("Bucket name cannot start or end with a period (.)")

        if ".." in bucket_name:
            raise ValueError("Bucket name cannot contain consecutive periods (..).")

        logger.info(f"✅ Bucket name '{bucket_name}' is valid.")

    def format_object_list(self, objects: List[Dict]) -> List[Dict[str, str]]:
        """
        Format object list for display with size conversion and date formatting.

        Based on original aws/s3_list_objects.py formatting.

        Args:
            objects: List of S3 objects from API response

        Returns:
            Formatted list with human-readable data
        """
        formatted_objects = []
        for obj in objects:
            formatted_objects.append(
                {
                    "Key": obj["Key"],
                    "Size (KB)": f"{obj['Size'] / 1024:.2f}",  # Convert bytes to KB
                    "LastModified": obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        return formatted_objects

    def execute_operation(self, context: OperationContext, operation_type: str, **kwargs) -> List[OperationResult]:
        """
        Execute S3 operation.

        Args:
            context: Operation context
            operation_type: Type of operation to execute
            **kwargs: Operation-specific arguments

        Returns:
            List of operation results
        """
        self.validate_context(context)

        if operation_type == "create_bucket":
            return self.create_bucket(context, **kwargs)
        elif operation_type == "delete_bucket":
            return self.delete_bucket(context, kwargs.get("bucket_name"))
        elif operation_type == "put_object":
            return self.put_object(context, **kwargs)
        elif operation_type == "delete_object":
            return self.delete_object(context, **kwargs)
        elif operation_type == "copy_object":
            return self.copy_object(context, **kwargs)
        elif operation_type == "list_objects":
            return self.list_objects(context, **kwargs)
        elif operation_type == "list_buckets":
            return self.list_buckets(context)
        elif operation_type == "set_bucket_policy":
            return self.set_bucket_policy(context, **kwargs)
        elif operation_type == "set_bucket_versioning":
            return self.set_bucket_versioning(context, **kwargs)
        elif operation_type == "set_bucket_encryption":
            return self.set_bucket_encryption(context, **kwargs)
        elif operation_type == "set_lifecycle_configuration":
            return self.set_lifecycle_configuration(context, **kwargs)
        elif operation_type == "empty_bucket":
            return self.empty_bucket(context, kwargs.get("bucket_name"))
        elif operation_type == "delete_bucket_and_objects":
            return self.delete_bucket_and_objects(context, kwargs.get("bucket_name"))
        elif operation_type == "set_public_access_block":
            return self.set_public_access_block(context, **kwargs)
        elif operation_type == "get_public_access_block":
            return self.get_public_access_block(context, kwargs.get("account_id"))
        elif operation_type == "sync_objects":
            return self.sync_objects(context, **kwargs)
        elif operation_type == "find_buckets_without_lifecycle":
            return self.find_buckets_without_lifecycle(context, **kwargs)
        elif operation_type == "add_lifecycle_policy_bulk":
            return self.add_lifecycle_policy_bulk(context, **kwargs)
        elif operation_type == "get_bucket_lifecycle":
            return self.get_bucket_lifecycle(context, **kwargs)
        elif operation_type == "analyze_lifecycle_compliance":
            return self.analyze_lifecycle_compliance(context, **kwargs)
        else:
            raise ValueError(f"Unsupported operation: {operation_type}")

    def validate_bucket_name(self, bucket_name: str) -> bool:
        """
        Validate S3 bucket name according to AWS naming rules.

        Args:
            bucket_name: Bucket name to validate

        Returns:
            True if valid

        Raises:
            ValueError: If bucket name is invalid
        """
        import re

        if len(bucket_name) < 3 or len(bucket_name) > 63:
            raise ValueError("Bucket name must be between 3 and 63 characters long")

        if not re.match(r"^[a-z0-9.-]+$", bucket_name):
            raise ValueError("Bucket name can only contain lowercase letters, numbers, hyphens (-), and periods (.)")

        if bucket_name.startswith("-") or bucket_name.endswith("-"):
            raise ValueError("Bucket name cannot start or end with hyphens")

        if ".." in bucket_name:
            raise ValueError("Bucket name cannot contain consecutive periods")

        return True

    def create_bucket(
        self,
        context: OperationContext,
        bucket_name: str,
        region: Optional[str] = None,
        acl: str = "private",
        encryption: bool = True,
        versioning: bool = False,
        public_access_block: bool = True,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[OperationResult]:
        """
        Create S3 bucket with security best practices.

        Args:
            context: Operation context
            bucket_name: Name of bucket to create
            region: AWS region for bucket (defaults to context region)
            acl: Bucket ACL (private, public-read, etc.)
            encryption: Enable server-side encryption
            versioning: Enable versioning
            public_access_block: Enable public access block
            tags: Bucket tags

        Returns:
            List of operation results
        """
        self.validate_bucket_name(bucket_name)

        bucket_region = region or context.region
        s3_client = self.get_client("s3", bucket_region)

        result = self.create_operation_result(context, "create_bucket", "s3:bucket", bucket_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would create bucket {bucket_name} in {bucket_region}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            # Create bucket
            create_params = {"Bucket": bucket_name, "ACL": acl}

            # Add location constraint for regions other than us-east-1
            if bucket_region != "us-east-1":
                create_params["CreateBucketConfiguration"] = {"LocationConstraint": bucket_region}

            response = self.execute_aws_call(s3_client, "create_bucket", **create_params)
            logger.info(f"Created bucket {bucket_name}")

            # Configure encryption
            if encryption:
                self.execute_aws_call(
                    s3_client,
                    "put_bucket_encryption",
                    Bucket=bucket_name,
                    ServerSideEncryptionConfiguration={
                        "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
                    },
                )
                logger.info(f"Enabled encryption for bucket {bucket_name}")

            # Configure versioning
            if versioning:
                self.execute_aws_call(
                    s3_client,
                    "put_bucket_versioning",
                    Bucket=bucket_name,
                    VersioningConfiguration={"Status": "Enabled"},
                )
                logger.info(f"Enabled versioning for bucket {bucket_name}")

            # Configure public access block
            if public_access_block:
                self.execute_aws_call(
                    s3_client,
                    "put_public_access_block",
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        "BlockPublicAcls": True,
                        "IgnorePublicAcls": True,
                        "BlockPublicPolicy": True,
                        "RestrictPublicBuckets": True,
                    },
                )
                logger.info(f"Enabled public access block for bucket {bucket_name}")

            # Apply tags
            if tags:
                tag_set = [{"Key": k, "Value": v} for k, v in tags.items()]
                self.execute_aws_call(s3_client, "put_bucket_tagging", Bucket=bucket_name, Tagging={"TagSet": tag_set})
                logger.info(f"Applied tags to bucket {bucket_name}")

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)

        except ClientError as e:
            error_msg = f"Failed to create bucket {bucket_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_bucket(self, context: OperationContext, bucket_name: str) -> List[OperationResult]:
        """
        Delete S3 bucket.

        Args:
            context: Operation context
            bucket_name: Name of bucket to delete

        Returns:
            List of operation results
        """
        s3_client = self.get_client("s3")

        result = self.create_operation_result(context, "delete_bucket", "s3:bucket", bucket_name)

        try:
            if not self.confirm_operation(context, bucket_name, "delete bucket"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete bucket {bucket_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                # Check if bucket is empty
                try:
                    objects = self.execute_aws_call(s3_client, "list_objects_v2", Bucket=bucket_name, MaxKeys=1)
                    if objects.get("Contents"):
                        raise ValueError(f"Bucket {bucket_name} is not empty. Use empty_bucket operation first.")
                except ClientError as e:
                    if e.response["Error"]["Code"] != "NoSuchBucket":
                        raise

                response = self.execute_aws_call(s3_client, "delete_bucket", Bucket=bucket_name)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully deleted bucket {bucket_name}")

        except ClientError as e:
            error_msg = f"Failed to delete bucket {bucket_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def put_object(
        self,
        context: OperationContext,
        bucket_name: str,
        key: str,
        body: Union[str, bytes] = None,
        file_path: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[OperationResult]:
        """
        Upload object to S3 bucket.

        Args:
            context: Operation context
            bucket_name: Target bucket name
            key: Object key (path)
            body: Object content as string or bytes
            file_path: Path to local file to upload
            content_type: MIME type of object
            metadata: Object metadata
            tags: Object tags

        Returns:
            List of operation results
        """
        s3_client = self.get_client("s3")

        result = self.create_operation_result(context, "put_object", "s3:object", f"{bucket_name}/{key}")

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would upload object to s3://{bucket_name}/{key}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            put_params = {"Bucket": bucket_name, "Key": key}

            if body is not None:
                put_params["Body"] = body
            elif file_path:
                with open(file_path, "rb") as f:
                    put_params["Body"] = f.read()
            else:
                raise ValueError("Either body or file_path must be provided")

            if content_type:
                put_params["ContentType"] = content_type
            if metadata:
                put_params["Metadata"] = metadata

            response = self.execute_aws_call(s3_client, "put_object", **put_params)

            # Apply tags if provided
            if tags:
                tag_set = "&".join([f"{k}={v}" for k, v in tags.items()])
                self.execute_aws_call(s3_client, "put_object_tagging", Bucket=bucket_name, Key=key, Tagging=tag_set)

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully uploaded object to s3://{bucket_name}/{key}")

        except ClientError as e:
            error_msg = f"Failed to upload object to s3://{bucket_name}/{key}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except Exception as e:
            error_msg = f"Failed to read file {file_path}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_object(
        self, context: OperationContext, bucket_name: str, key: str, version_id: Optional[str] = None
    ) -> List[OperationResult]:
        """
        Delete object from S3 bucket.

        Args:
            context: Operation context
            bucket_name: Source bucket name
            key: Object key to delete
            version_id: Specific version to delete (for versioned buckets)

        Returns:
            List of operation results
        """
        s3_client = self.get_client("s3")

        result = self.create_operation_result(context, "delete_object", "s3:object", f"{bucket_name}/{key}")

        try:
            if not self.confirm_operation(context, f"s3://{bucket_name}/{key}", "delete object"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete object s3://{bucket_name}/{key}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                delete_params = {"Bucket": bucket_name, "Key": key}
                if version_id:
                    delete_params["VersionId"] = version_id

                response = self.execute_aws_call(s3_client, "delete_object", **delete_params)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully deleted object s3://{bucket_name}/{key}")

        except ClientError as e:
            error_msg = f"Failed to delete object s3://{bucket_name}/{key}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def copy_object(
        self,
        context: OperationContext,
        source_bucket: str,
        source_key: str,
        destination_bucket: str,
        destination_key: str,
        metadata_directive: str = "COPY",
    ) -> List[OperationResult]:
        """
        Copy object between S3 locations.

        Args:
            context: Operation context
            source_bucket: Source bucket name
            source_key: Source object key
            destination_bucket: Destination bucket name
            destination_key: Destination object key
            metadata_directive: COPY or REPLACE metadata

        Returns:
            List of operation results
        """
        s3_client = self.get_client("s3")

        result = self.create_operation_result(context, "copy_object", "s3:object", f"{source_bucket}/{source_key}")

        try:
            if context.dry_run:
                logger.info(
                    f"[DRY-RUN] Would copy s3://{source_bucket}/{source_key} to s3://{destination_bucket}/{destination_key}"
                )
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                copy_source = {"Bucket": source_bucket, "Key": source_key}

                response = self.execute_aws_call(
                    s3_client,
                    "copy_object",
                    CopySource=copy_source,
                    Bucket=destination_bucket,
                    Key=destination_key,
                    MetadataDirective=metadata_directive,
                )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully copied object to s3://{destination_bucket}/{destination_key}")

        except ClientError as e:
            error_msg = f"Failed to copy object: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def empty_bucket(self, context: OperationContext, bucket_name: str) -> List[OperationResult]:
        """
        Delete all objects in S3 bucket.

        Args:
            context: Operation context
            bucket_name: Bucket to empty

        Returns:
            List of operation results
        """
        s3_client = self.get_client("s3")

        result = self.create_operation_result(context, "empty_bucket", "s3:bucket", bucket_name)

        try:
            if not self.confirm_operation(context, bucket_name, "empty bucket"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would empty bucket {bucket_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            # List and delete all objects
            deleted_count = 0
            paginator = s3_client.get_paginator("list_objects_v2")

            for page in paginator.paginate(Bucket=bucket_name):
                objects = page.get("Contents", [])

                if objects:
                    delete_keys = [{"Key": obj["Key"]} for obj in objects]

                    self.execute_aws_call(
                        s3_client, "delete_objects", Bucket=bucket_name, Delete={"Objects": delete_keys}
                    )

                    deleted_count += len(delete_keys)

            # Handle versioned objects
            version_paginator = s3_client.get_paginator("list_object_versions")
            for page in version_paginator.paginate(Bucket=bucket_name):
                versions = page.get("Versions", []) + page.get("DeleteMarkers", [])

                if versions:
                    delete_keys = [{"Key": obj["Key"], "VersionId": obj["VersionId"]} for obj in versions]

                    self.execute_aws_call(
                        s3_client, "delete_objects", Bucket=bucket_name, Delete={"Objects": delete_keys}
                    )

                    deleted_count += len(delete_keys)

            result.response_data = {"deleted_objects": deleted_count}
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully emptied bucket {bucket_name}, deleted {deleted_count} objects")

        except ClientError as e:
            error_msg = f"Failed to empty bucket {bucket_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def set_bucket_policy(
        self, context: OperationContext, bucket_name: str, policy: Union[str, Dict[str, Any]]
    ) -> List[OperationResult]:
        """
        Set S3 bucket policy.

        Args:
            context: Operation context
            bucket_name: Target bucket name
            policy: Bucket policy as JSON string or dict

        Returns:
            List of operation results
        """
        s3_client = self.get_client("s3")

        result = self.create_operation_result(context, "set_bucket_policy", "s3:bucket", bucket_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would set policy on bucket {bucket_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                policy_json = policy if isinstance(policy, str) else json.dumps(policy)

                response = self.execute_aws_call(s3_client, "put_bucket_policy", Bucket=bucket_name, Policy=policy_json)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully set policy on bucket {bucket_name}")

        except ClientError as e:
            error_msg = f"Failed to set bucket policy on {bucket_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def set_bucket_versioning(
        self, context: OperationContext, bucket_name: str, status: str = "Enabled"
    ) -> List[OperationResult]:
        """
        Configure S3 bucket versioning.

        Args:
            context: Operation context
            bucket_name: Target bucket name
            status: Versioning status (Enabled, Suspended)

        Returns:
            List of operation results
        """
        s3_client = self.get_client("s3")

        result = self.create_operation_result(context, "set_bucket_versioning", "s3:bucket", bucket_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would set versioning to {status} on bucket {bucket_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(
                    s3_client, "put_bucket_versioning", Bucket=bucket_name, VersioningConfiguration={"Status": status}
                )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully set versioning to {status} on bucket {bucket_name}")

        except ClientError as e:
            error_msg = f"Failed to set versioning on bucket {bucket_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def set_bucket_encryption(
        self,
        context: OperationContext,
        bucket_name: str,
        sse_algorithm: str = "AES256",
        kms_master_key_id: Optional[str] = None,
    ) -> List[OperationResult]:
        """
        Configure S3 bucket encryption.

        Args:
            context: Operation context
            bucket_name: Target bucket name
            sse_algorithm: Encryption algorithm (AES256, aws:kms)
            kms_master_key_id: KMS key ID for aws:kms encryption

        Returns:
            List of operation results
        """
        s3_client = self.get_client("s3")

        result = self.create_operation_result(context, "set_bucket_encryption", "s3:bucket", bucket_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would set encryption on bucket {bucket_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                encryption_rule = {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": sse_algorithm}}

                if sse_algorithm == "aws:kms" and kms_master_key_id:
                    encryption_rule["ApplyServerSideEncryptionByDefault"]["KMSMasterKeyID"] = kms_master_key_id

                response = self.execute_aws_call(
                    s3_client,
                    "put_bucket_encryption",
                    Bucket=bucket_name,
                    ServerSideEncryptionConfiguration={"Rules": [encryption_rule]},
                )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully set encryption on bucket {bucket_name}")

        except ClientError as e:
            error_msg = f"Failed to set encryption on bucket {bucket_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def find_buckets_without_lifecycle(
        self, 
        context: OperationContext, 
        region: Optional[str] = None, 
        bucket_names: Optional[List[str]] = None
    ) -> List[OperationResult]:
        """
        Find S3 buckets without lifecycle policies.
        
        Enhanced from unSkript notebook: AWS_Add_Lifecycle_Policy_To_S3_Buckets.ipynb
        Identifies buckets that do not have any configured lifecycle rules for 
        managing object lifecycle, valuable for optimizing storage costs.

        Args:
            context: Operation context
            region: AWS region to search (if None, searches all regions)
            bucket_names: Specific bucket names to check (if None, checks all buckets)

        Returns:
            List of operation results with buckets without lifecycle policies
        """
        result = self.create_operation_result(
            context, "find_buckets_without_lifecycle", "s3:bucket", "lifecycle-audit"
        )

        try:
            console.print(f"[bold blue]🔍 Scanning for S3 buckets without lifecycle policies...[/bold blue]")
            
            buckets_without_policy = []
            
            # Get list of regions to search
            search_regions = []
            if region:
                search_regions = [region]
            elif bucket_names and region:
                search_regions = [region]
            else:
                # Get all regions if not specified - use boto3 to get all regions
                try:
                    ec2_client = self.get_client("ec2", "us-east-1")  # Use us-east-1 to get all regions
                    regions_response = self.execute_aws_call(ec2_client, "describe_regions")
                    search_regions = [r["RegionName"] for r in regions_response.get("Regions", [])]
                except Exception:
                    # Fallback to common regions
                    search_regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]

            # Process each region
            for reg in search_regions:
                try:
                    s3_client = self.get_client("s3", reg)
                    
                    # Get buckets to check
                    if bucket_names:
                        # Check specific buckets
                        buckets_to_check = bucket_names
                    else:
                        # Get all buckets in region
                        response = self.execute_aws_call(s3_client, "list_buckets")
                        buckets_to_check = [bucket["Name"] for bucket in response.get("Buckets", [])]

                    # Check each bucket for lifecycle policies
                    for bucket_name in buckets_to_check:
                        try:
                            # Get bucket location to ensure it's in the current region
                            try:
                                bucket_location = self.execute_aws_call(s3_client, "get_bucket_location", Bucket=bucket_name)
                                bucket_region = bucket_location.get("LocationConstraint")
                                
                                # us-east-1 returns None for LocationConstraint
                                if bucket_region is None:
                                    bucket_region = "us-east-1"
                                
                                # Skip if bucket is not in current region (when checking all regions)
                                if not bucket_names and bucket_region != reg:
                                    continue
                                    
                            except ClientError as e:
                                if e.response["Error"]["Code"] in ["NoSuchBucket", "AccessDenied"]:
                                    continue
                                raise

                            # Check for lifecycle configuration
                            try:
                                lifecycle_response = self.execute_aws_call(
                                    s3_client, "get_bucket_lifecycle_configuration", Bucket=bucket_name
                                )
                                
                                # If we get here, bucket has lifecycle rules
                                rules = lifecycle_response.get("Rules", [])
                                if not rules:
                                    # Empty rules list means no active lifecycle
                                    buckets_without_policy.append({
                                        "bucket_name": bucket_name,
                                        "region": bucket_region,
                                        "issue": "Empty lifecycle configuration"
                                    })
                                    
                            except ClientError as e:
                                if e.response["Error"]["Code"] == "NoSuchLifecycleConfiguration":
                                    # No lifecycle configuration found
                                    buckets_without_policy.append({
                                        "bucket_name": bucket_name,
                                        "region": bucket_region,
                                        "issue": "No lifecycle configuration"
                                    })
                                else:
                                    logger.warning(f"Could not check lifecycle for bucket {bucket_name}: {e}")

                        except Exception as bucket_error:
                            logger.warning(f"Error checking bucket {bucket_name}: {bucket_error}")
                            continue

                except Exception as region_error:
                    logger.warning(f"Error processing region {reg}: {region_error}")
                    continue

            # Format results with Rich console output
            if buckets_without_policy:
                console.print(f"[bold yellow]⚠️  Found {len(buckets_without_policy)} bucket(s) without lifecycle policies:[/bold yellow]")
                
                from rich.table import Table
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Bucket Name", style="cyan")
                table.add_column("Region", style="green")
                table.add_column("Issue", style="yellow")
                
                for bucket_info in buckets_without_policy:
                    table.add_row(
                        bucket_info["bucket_name"],
                        bucket_info["region"], 
                        bucket_info["issue"]
                    )
                
                console.print(table)
                
                result.response_data = {
                    "buckets_without_lifecycle": buckets_without_policy,
                    "total_count": len(buckets_without_policy),
                    "regions_scanned": search_regions
                }
                result.mark_completed(OperationStatus.SUCCESS)
            else:
                console.print("[bold green]✅ All buckets have lifecycle policies configured![/bold green]")
                result.response_data = {
                    "buckets_without_lifecycle": [],
                    "total_count": 0,
                    "regions_scanned": search_regions,
                    "message": "All buckets have lifecycle policies"
                }
                result.mark_completed(OperationStatus.SUCCESS)

        except Exception as e:
            error_msg = f"Failed to scan for buckets without lifecycle policies: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def add_lifecycle_policy_bulk(
        self,
        context: OperationContext,
        bucket_list: List[Dict[str, str]],
        expiration_days: int = 30,
        prefix: str = "",
        noncurrent_days: int = 30,
        transition_ia_days: Optional[int] = None,
        transition_glacier_days: Optional[int] = None,
    ) -> List[OperationResult]:
        """
        Add lifecycle policies to multiple S3 buckets in bulk.
        
        Enhanced from unSkript notebook: AWS_Add_Lifecycle_Policy_To_S3_Buckets.ipynb
        Applies optimized lifecycle configuration for cost management.

        Args:
            context: Operation context
            bucket_list: List of dictionaries with 'bucket_name' and 'region' keys
            expiration_days: Days after which objects expire
            prefix: Object prefix filter for lifecycle rule
            noncurrent_days: Days before noncurrent versions are deleted
            transition_ia_days: Days before transition to IA storage class
            transition_glacier_days: Days before transition to Glacier

        Returns:
            List of operation results for each bucket processed
        """
        results = []
        
        console.print(f"[bold blue]📋 Adding lifecycle policies to {len(bucket_list)} bucket(s)...[/bold blue]")
        
        if context.dry_run:
            console.print("[yellow]🧪 DRY-RUN MODE: No actual changes will be made[/yellow]")

        for i, bucket_info in enumerate(bucket_list, 1):
            bucket_name = bucket_info.get("bucket_name")
            bucket_region = bucket_info.get("region")
            
            if not bucket_name or not bucket_region:
                logger.error(f"Invalid bucket info: {bucket_info}")
                continue
                
            console.print(f"[cyan]({i}/{len(bucket_list)}) Processing bucket: {bucket_name}[/cyan]")

            result = self.create_operation_result(
                context, "add_lifecycle_policy", "s3:bucket", bucket_name
            )

            try:
                s3_client = self.get_client("s3", bucket_region)

                # Build lifecycle configuration
                lifecycle_rules = []
                
                # Main lifecycle rule
                rule = {
                    "ID": f"lifecycle-rule-{int(datetime.now().timestamp())}",
                    "Status": "Enabled",
                    "Filter": {"Prefix": prefix} if prefix else {},
                    "Expiration": {"Days": expiration_days},
                }

                # Add noncurrent version expiration
                if noncurrent_days:
                    rule["NoncurrentVersionExpiration"] = {"NoncurrentDays": noncurrent_days}

                # Add storage class transitions
                transitions = []
                if transition_ia_days and transition_ia_days < expiration_days:
                    transitions.append({
                        "Days": transition_ia_days,
                        "StorageClass": "STANDARD_IA"
                    })
                
                if transition_glacier_days and transition_glacier_days < expiration_days:
                    transitions.append({
                        "Days": transition_glacier_days,
                        "StorageClass": "GLACIER"
                    })
                
                if transitions:
                    rule["Transitions"] = transitions

                lifecycle_rules.append(rule)

                lifecycle_config = {"Rules": lifecycle_rules}

                if context.dry_run:
                    console.print(f"[yellow]  [DRY-RUN] Would apply lifecycle policy to {bucket_name}[/yellow]")
                    result.response_data = {
                        "bucket_name": bucket_name,
                        "region": bucket_region,
                        "lifecycle_config": lifecycle_config,
                        "dry_run": True
                    }
                    result.mark_completed(OperationStatus.DRY_RUN)
                else:
                    # Apply lifecycle configuration
                    response = self.execute_aws_call(
                        s3_client,
                        "put_bucket_lifecycle_configuration",
                        Bucket=bucket_name,
                        LifecycleConfiguration=lifecycle_config
                    )

                    console.print(f"[green]  ✅ Successfully applied lifecycle policy to {bucket_name}[/green]")
                    
                    result.response_data = {
                        "bucket_name": bucket_name,
                        "region": bucket_region,
                        "lifecycle_config": lifecycle_config,
                        "aws_response": response
                    }
                    result.mark_completed(OperationStatus.SUCCESS)

            except ClientError as e:
                error_msg = f"Failed to set lifecycle policy on {bucket_name}: {e}"
                console.print(f"[red]  ❌ {error_msg}[/red]")
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)
            except Exception as e:
                error_msg = f"Unexpected error for bucket {bucket_name}: {e}"
                console.print(f"[red]  ❌ {error_msg}[/red]")
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)

            results.append(result)

        # Summary report
        successful = len([r for r in results if r.success])
        failed = len(results) - successful
        
        if context.dry_run:
            console.print(f"[yellow]🧪 DRY-RUN SUMMARY: Would process {len(results)} bucket(s)[/yellow]")
        else:
            console.print(f"[bold blue]📊 BULK OPERATION SUMMARY:[/bold blue]")
            console.print(f"[green]  ✅ Successful: {successful}[/green]")
            if failed > 0:
                console.print(f"[red]  ❌ Failed: {failed}[/red]")

        return results

    def get_bucket_lifecycle(
        self, context: OperationContext, bucket_name: str
    ) -> List[OperationResult]:
        """
        Get current lifecycle configuration for an S3 bucket.

        Args:
            context: Operation context
            bucket_name: Name of bucket to check

        Returns:
            List of operation results with current lifecycle configuration
        """
        s3_client = self.get_client("s3")
        
        result = self.create_operation_result(
            context, "get_bucket_lifecycle", "s3:bucket", bucket_name
        )

        try:
            console.print(f"[blue]🔍 Checking lifecycle configuration for bucket: {bucket_name}[/blue]")
            
            try:
                response = self.execute_aws_call(
                    s3_client, "get_bucket_lifecycle_configuration", Bucket=bucket_name
                )
                
                rules = response.get("Rules", [])
                console.print(f"[green]✅ Found {len(rules)} lifecycle rule(s) for bucket {bucket_name}[/green]")
                
                # Display rules in a formatted table
                if rules:
                    from rich.table import Table
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("Rule ID", style="cyan")
                    table.add_column("Status", style="green")
                    table.add_column("Prefix", style="yellow")
                    table.add_column("Expiration", style="red")
                    
                    for rule in rules:
                        rule_id = rule.get("ID", "N/A")
                        status = rule.get("Status", "N/A")
                        
                        # Handle different filter formats
                        filter_info = rule.get("Filter", {})
                        if isinstance(filter_info, dict):
                            prefix = filter_info.get("Prefix", "")
                        else:
                            prefix = ""
                            
                        expiration = rule.get("Expiration", {})
                        exp_days = expiration.get("Days", "N/A")
                        
                        table.add_row(rule_id, status, prefix or "All objects", str(exp_days))
                    
                    console.print(table)
                
                result.response_data = {
                    "bucket_name": bucket_name,
                    "lifecycle_rules": rules,
                    "rules_count": len(rules)
                }
                result.mark_completed(OperationStatus.SUCCESS)
                
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchLifecycleConfiguration":
                    console.print(f"[yellow]⚠️  No lifecycle configuration found for bucket {bucket_name}[/yellow]")
                    result.response_data = {
                        "bucket_name": bucket_name,
                        "lifecycle_rules": [],
                        "rules_count": 0,
                        "message": "No lifecycle configuration"
                    }
                    result.mark_completed(OperationStatus.SUCCESS)
                else:
                    raise e

        except ClientError as e:
            error_msg = f"Failed to get lifecycle configuration for {bucket_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def analyze_lifecycle_compliance(
        self, context: OperationContext, region: Optional[str] = None
    ) -> List[OperationResult]:
        """
        Analyze lifecycle compliance across S3 buckets and provide cost optimization recommendations.
        
        Args:
            context: Operation context  
            region: AWS region to analyze (if None, analyzes all regions)

        Returns:
            List of operation results with compliance analysis and recommendations
        """
        result = self.create_operation_result(
            context, "analyze_lifecycle_compliance", "s3:account", "compliance-analysis"
        )

        try:
            console.print("[bold blue]📊 Analyzing S3 lifecycle compliance and cost optimization opportunities...[/bold blue]")
            
            # Find buckets without lifecycle policies
            find_results = self.find_buckets_without_lifecycle(context, region=region)
            
            if not find_results or not find_results[0].success:
                result.mark_completed(OperationStatus.FAILED, "Failed to analyze buckets")
                return [result]
                
            buckets_data = find_results[0].response_data
            non_compliant_buckets = buckets_data.get("buckets_without_lifecycle", [])
            total_buckets_scanned = buckets_data.get("total_count", 0)
            
            # Calculate compliance metrics
            s3_client = self.get_client("s3")
            
            # Get total bucket count for compliance percentage
            list_response = self.execute_aws_call(s3_client, "list_buckets")
            total_buckets = len(list_response.get("Buckets", []))
            
            compliance_percentage = ((total_buckets - len(non_compliant_buckets)) / total_buckets * 100) if total_buckets > 0 else 100
            
            # Generate recommendations
            recommendations = []
            potential_savings = 0
            
            if non_compliant_buckets:
                recommendations.extend([
                    "🎯 Implement lifecycle policies to automatically transition objects to cheaper storage classes",
                    "💰 Configure automatic deletion of old object versions to reduce storage costs",
                    "📈 Set up transitions: Standard → IA (30 days) → Glacier (90 days) → Deep Archive (365 days)",
                    "🔧 Use prefixes to apply different policies to different object types",
                    "📊 Monitor lifecycle rule effectiveness with CloudWatch metrics"
                ])
                
                # Estimate potential savings (rough calculation)
                estimated_savings_per_bucket = 25  # Estimated 25% savings per bucket
                potential_savings = len(non_compliant_buckets) * estimated_savings_per_bucket

            # Create summary report
            from rich.panel import Panel
            from rich.table import Table
            
            # Compliance summary table
            summary_table = Table(show_header=True, header_style="bold magenta")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="green")
            
            summary_table.add_row("Total Buckets", str(total_buckets))
            summary_table.add_row("Compliant Buckets", str(total_buckets - len(non_compliant_buckets)))
            summary_table.add_row("Non-Compliant Buckets", str(len(non_compliant_buckets)))
            summary_table.add_row("Compliance Percentage", f"{compliance_percentage:.1f}%")
            summary_table.add_row("Potential Cost Savings", f"~{potential_savings}%")
            
            console.print(Panel(summary_table, title="S3 Lifecycle Compliance Report", border_style="blue"))
            
            # Display recommendations if any
            if recommendations:
                console.print("\n[bold yellow]💡 Cost Optimization Recommendations:[/bold yellow]")
                for i, rec in enumerate(recommendations, 1):
                    console.print(f"  {i}. {rec}")
            
            # Compliance status color coding
            if compliance_percentage >= 90:
                compliance_status = "[bold green]EXCELLENT[/bold green]"
            elif compliance_percentage >= 75:
                compliance_status = "[bold yellow]GOOD[/bold yellow]"
            elif compliance_percentage >= 50:
                compliance_status = "[bold orange]NEEDS IMPROVEMENT[/bold orange]"
            else:
                compliance_status = "[bold red]POOR[/bold red]"
                
            console.print(f"\n[bold blue]Overall Compliance Status: {compliance_status}[/bold blue]")
            
            result.response_data = {
                "compliance_percentage": compliance_percentage,
                "total_buckets": total_buckets,
                "compliant_buckets": total_buckets - len(non_compliant_buckets),
                "non_compliant_buckets": len(non_compliant_buckets),
                "non_compliant_details": non_compliant_buckets,
                "recommendations": recommendations,
                "potential_savings_percentage": potential_savings,
                "compliance_status": compliance_status.replace("[bold ", "").replace("[/bold ", "").replace("]", "")
            }
            result.mark_completed(OperationStatus.SUCCESS)

        except Exception as e:
            error_msg = f"Failed to analyze lifecycle compliance: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_bucket_and_objects(self, context: OperationContext, bucket_name: str) -> List[OperationResult]:
        """
        Delete S3 bucket and all its objects/versions (complete cleanup).

        Migrated from inventory/delete_s3_buckets_objects.py

        Args:
            context: Operation context
            bucket_name: Bucket to delete completely

        Returns:
            List of operation results
        """
        s3_client = self.get_client("s3")

        result = self.create_operation_result(context, "delete_bucket_and_objects", "s3:bucket", bucket_name)

        try:
            if not self.confirm_operation(context, bucket_name, "delete bucket and all objects"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete bucket {bucket_name} and all objects")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            # First empty the bucket
            empty_results = self.empty_bucket(context, bucket_name)
            if not empty_results or not empty_results[0].success:
                result.mark_completed(OperationStatus.FAILED, "Failed to empty bucket before deletion")
                return [result]

            # Then delete the bucket
            response = self.execute_aws_call(s3_client, "delete_bucket", Bucket=bucket_name)

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully deleted bucket {bucket_name} and all objects")

        except ClientError as e:
            error_msg = f"Failed to delete bucket and objects {bucket_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def set_public_access_block(
        self,
        context: OperationContext,
        account_id: Optional[str] = None,
        bucket_name: Optional[str] = None,
        block_public_acls: bool = True,
        ignore_public_acls: bool = True,
        block_public_policy: bool = True,
        restrict_public_buckets: bool = True,
    ) -> List[OperationResult]:
        """
        Configure S3 public access block settings.

        Migrated from inventory/update_s3_public_access_block.py

        Args:
            context: Operation context
            account_id: Account ID for account-level settings
            bucket_name: Bucket name for bucket-level settings
            block_public_acls: Block public ACLs
            ignore_public_acls: Ignore public ACLs
            block_public_policy: Block public bucket policies
            restrict_public_buckets: Restrict public bucket access

        Returns:
            List of operation results
        """
        if account_id:
            # Account-level public access block
            s3control_client = self.get_client("s3control")
            resource_id = f"account:{account_id}"
        elif bucket_name:
            # Bucket-level public access block
            s3_client = self.get_client("s3")
            resource_id = f"bucket:{bucket_name}"
        else:
            raise ValueError("Either account_id or bucket_name must be provided")

        result = self.create_operation_result(context, "set_public_access_block", "s3:public_access_block", resource_id)

        try:
            public_access_block_config = {
                "BlockPublicAcls": block_public_acls,
                "IgnorePublicAcls": ignore_public_acls,
                "BlockPublicPolicy": block_public_policy,
                "RestrictPublicBuckets": restrict_public_buckets,
            }

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would set public access block on {resource_id}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                if account_id:
                    response = self.execute_aws_call(
                        s3control_client,
                        "put_public_access_block",
                        AccountId=account_id,
                        PublicAccessBlockConfiguration=public_access_block_config,
                    )
                else:
                    response = self.execute_aws_call(
                        s3_client,
                        "put_public_access_block",
                        Bucket=bucket_name,
                        PublicAccessBlockConfiguration=public_access_block_config,
                    )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully set public access block on {resource_id}")

        except ClientError as e:
            error_msg = f"Failed to set public access block on {resource_id}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def sync_objects(
        self,
        context: OperationContext,
        source_bucket: str,
        destination_bucket: str,
        source_prefix: Optional[str] = None,
        destination_prefix: Optional[str] = None,
        delete_removed: bool = False,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[OperationResult]:
        """
        Synchronize objects between S3 buckets or prefixes.

        Args:
            context: Operation context
            source_bucket: Source bucket name
            destination_bucket: Destination bucket name
            source_prefix: Source prefix to sync from
            destination_prefix: Destination prefix to sync to
            delete_removed: Delete objects in destination that don't exist in source
            exclude_patterns: Patterns to exclude from sync

        Returns:
            List of operation results
        """
        s3_client = self.get_client("s3", context.region)

        result = self.create_operation_result(
            context, "sync_objects", "s3:bucket", f"{source_bucket}->{destination_bucket}"
        )

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would sync objects from {source_bucket} to {destination_bucket}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            # List objects in source bucket
            list_params = {"Bucket": source_bucket}
            if source_prefix:
                list_params["Prefix"] = source_prefix

            paginator = s3_client.get_paginator("list_objects_v2")
            source_objects = []

            for page in paginator.paginate(**list_params):
                if "Contents" in page:
                    source_objects.extend(page["Contents"])

            # List objects in destination bucket for comparison
            dest_list_params = {"Bucket": destination_bucket}
            if destination_prefix:
                dest_list_params["Prefix"] = destination_prefix

            dest_paginator = s3_client.get_paginator("list_objects_v2")
            dest_objects = {}

            for page in dest_paginator.paginate(**dest_list_params):
                if "Contents" in page:
                    for obj in page["Contents"]:
                        dest_objects[obj["Key"]] = obj

            synced_count = 0
            deleted_count = 0

            # Sync objects from source to destination
            for obj in source_objects:
                source_key = obj["Key"]

                # Apply prefix transformation if needed
                if source_prefix and destination_prefix:
                    if source_key.startswith(source_prefix):
                        dest_key = destination_prefix + source_key[len(source_prefix) :]
                    else:
                        dest_key = source_key
                else:
                    dest_key = source_key

                # Check exclude patterns
                if exclude_patterns:
                    excluded = any(pattern in source_key for pattern in exclude_patterns)
                    if excluded:
                        continue

                # Check if object needs to be copied/updated
                needs_copy = True
                if dest_key in dest_objects:
                    dest_obj = dest_objects[dest_key]
                    if obj["ETag"] == dest_obj["ETag"] and obj["Size"] == dest_obj["Size"]:
                        needs_copy = False

                if needs_copy:
                    copy_source = {"Bucket": source_bucket, "Key": source_key}
                    self.execute_aws_call(
                        s3_client, "copy_object", CopySource=copy_source, Bucket=destination_bucket, Key=dest_key
                    )
                    synced_count += 1
                    logger.info(f"Synced object: {source_key} -> {dest_key}")

            # Delete objects in destination that don't exist in source
            if delete_removed:
                source_keys = {obj["Key"] for obj in source_objects}
                for dest_key in dest_objects:
                    # Transform back to source key for comparison
                    if destination_prefix and source_prefix:
                        if dest_key.startswith(destination_prefix):
                            source_equiv = source_prefix + dest_key[len(destination_prefix) :]
                        else:
                            source_equiv = dest_key
                    else:
                        source_equiv = dest_key

                    if source_equiv not in source_keys:
                        self.execute_aws_call(s3_client, "delete_object", Bucket=destination_bucket, Key=dest_key)
                        deleted_count += 1
                        logger.info(f"Deleted object: {dest_key}")

            result.response_data = {
                "synced_objects": synced_count,
                "deleted_objects": deleted_count,
                "total_source_objects": len(source_objects),
            }
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully synced {synced_count} objects, deleted {deleted_count} objects")

        except ClientError as e:
            error_msg = f"Failed to sync objects from {source_bucket} to {destination_bucket}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def list_objects(
        self,
        context: OperationContext,
        bucket_name: Optional[str] = None,
        prefix: Optional[str] = None,
        max_keys: int = 1000,
    ) -> List[OperationResult]:
        """
        List objects in S3 bucket with pagination support.

        Enhanced from original aws/s3_list_objects.py with pagination and formatting.

        Args:
            context: Operation context
            bucket_name: Name of bucket to list (can use S3_BUCKET env var)
            prefix: Filter objects by prefix
            max_keys: Maximum number of keys per request

        Returns:
            List of operation results with formatted object data
        """
        # Environment variable support from original file
        bucket_name = bucket_name or os.getenv("S3_BUCKET", "my-default-bucket")

        s3_client = self.get_client("s3", context.region)

        result = self.create_operation_result(context, "list_objects", "s3:bucket", bucket_name)

        try:
            logger.info(f"Listing objects in bucket: {bucket_name}")

            # Prepare parameters (from original file)
            params = {"Bucket": bucket_name, "MaxKeys": max_keys}
            if prefix:
                params["Prefix"] = prefix

            # Fetch objects with pagination support (from original file)
            paginator = s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(**params)

            object_list = []
            for page in page_iterator:
                if "Contents" in page:  # Check if there are objects
                    for obj in page["Contents"]:
                        object_list.append(obj)

            # Format objects for display (from original file)
            formatted_objects = self.format_object_list(object_list)

            result.response_data = {
                "objects": formatted_objects,
                "count": len(object_list),
                "bucket": bucket_name,
                "prefix": prefix,
            }
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Found {len(object_list)} object(s) in bucket '{bucket_name}'.")

        except ClientError as e:
            error_msg = f"❌ AWS Client Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except BotoCoreError as e:
            error_msg = f"❌ BotoCore Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except Exception as e:
            error_msg = f"❌ Unexpected error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def list_buckets(self, context: OperationContext) -> List[OperationResult]:
        """
        List all S3 buckets in the account.

        Enhanced from original aws/s3_list_buckets.py functionality.
        """
        s3_client = self.get_client("s3", context.region)

        result = self.create_operation_result(context, "list_buckets", "s3:account", "all-buckets")

        try:
            logger.info("Listing all S3 buckets...")

            response = self.execute_aws_call(s3_client, "list_buckets")
            buckets = response.get("Buckets", [])

            # Format bucket data
            formatted_buckets = []
            for bucket in buckets:
                formatted_buckets.append(
                    {"Name": bucket["Name"], "CreationDate": bucket["CreationDate"].strftime("%Y-%m-%d %H:%M:%S")}
                )

            result.response_data = {"buckets": formatted_buckets, "count": len(buckets)}
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Found {len(buckets)} bucket(s)")

        except ClientError as e:
            error_msg = f"❌ AWS Client Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except BotoCoreError as e:
            error_msg = f"❌ BotoCore Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except Exception as e:
            error_msg = f"❌ Unexpected error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]


# ==============================
# AWS LAMBDA HANDLERS
# ==============================


def lambda_handler_s3_object_operations(event, context):
    """
    AWS Lambda handler for S3 object operations.

    Based on original aws/s3_object_operations.py Lambda handler.
    """
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate.base import OperationContext

        action = event.get("action")  # 'upload' or 'delete'
        bucket = event.get("bucket", os.getenv("S3_BUCKET", "my-default-bucket"))
        key = event.get("key", os.getenv("S3_KEY", "default-key.txt"))
        file_path = event.get("file_path", os.getenv("LOCAL_FILE_PATH", "default.txt"))
        acl = event.get("acl", os.getenv("ACL", "private"))
        region = event.get("region", os.getenv("AWS_REGION", "us-east-1"))

        s3_ops = S3Operations()
        account = AWSAccount(account_id="current", account_name="lambda-execution")
        operation_context = OperationContext(
            account=account, region=region, operation_type=action, resource_types=["s3:object"], dry_run=False
        )

        if action == "upload":
            results = s3_ops.put_object(operation_context, bucket=bucket, key=key, file_path=file_path, acl=acl)
            return {"statusCode": 200, "body": f"File '{key}' uploaded to '{bucket}'."}
        elif action == "delete":
            results = s3_ops.delete_object(operation_context, bucket=bucket, key=key)
            return {"statusCode": 200, "body": f"File '{key}' deleted from '{bucket}'."}
        else:
            raise ValueError("Invalid action. Supported actions: 'upload', 'delete'.")

    except Exception as e:
        logger.error(f"❌ Lambda Error: {e}")
        return {"statusCode": 500, "body": str(e)}


# ==============================
# SCRIPT ENTRY POINT (CLI Support)
# ==============================


def main():
    """
    Main entry point for standalone execution (CLI or Docker).

    Provides compatibility with original AWS script execution patterns.
    """
    import sys

    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python s3_operations.py <operation> [args...][/yellow]")
        console.print("[blue]Operations: create-bucket, list-objects, list-buckets, put-object, delete-object[/blue]")
        sys.exit(1)

    operation = sys.argv[1]

    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate.base import OperationContext

        s3_ops = S3Operations()
        account = AWSAccount(account_id="current", account_name="cli-execution")
        operation_context = OperationContext(
            account=account,
            region=os.getenv("AWS_REGION", "us-east-1"),
            operation_type=operation.replace("-", "_"),
            resource_types=["s3"],
            dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
        )

        if operation == "create-bucket":
            bucket_name = sys.argv[2] if len(sys.argv) > 2 else os.getenv("S3_BUCKET_NAME", "1cloudops")
            results = s3_ops.create_bucket(operation_context, bucket_name=bucket_name)

        elif operation == "list-objects":
            bucket_name = sys.argv[2] if len(sys.argv) > 2 else os.getenv("S3_BUCKET", "my-default-bucket")
            results = s3_ops.list_objects(operation_context, bucket_name=bucket_name)

        elif operation == "list-buckets":
            results = s3_ops.list_buckets(operation_context)

        elif operation == "put-object":
            bucket = os.getenv("S3_BUCKET", "my-default-bucket")
            key = os.getenv("S3_KEY", "default-key.txt")
            file_path = os.getenv("LOCAL_FILE_PATH", "default.txt")
            results = s3_ops.put_object(operation_context, bucket=bucket, key=key, file_path=file_path)

        elif operation == "delete-object":
            bucket = os.getenv("S3_BUCKET", "my-default-bucket")
            key = os.getenv("S3_KEY", "default-key.txt")
            results = s3_ops.delete_object(operation_context, bucket=bucket, key=key)

        else:
            raise ValueError(f"Unknown operation: {operation}")

        # Print results with Rich formatting
        for result in results:
            if result.success:
                console.print(f"[green]✅ {result.operation_type} completed successfully[/green]")
                if result.response_data:
                    console.print(f"[blue]   Data: {json.dumps(result.response_data, default=str, indent=2)}[/blue]")
            else:
                console.print(f"[red]❌ {result.operation_type} failed: {result.error_message}[/red]")

    except Exception as e:
        logger.error(f"Error during operation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
