"""
ACM Certificate Cleanup - Remove expired and unused SSL certificates.
"""

import logging

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client

logger = logging.getLogger(__name__)


@click.command()
@click.option("--dry-run", is_flag=True, default=True, help="Preview mode - show actions without making changes")
def clean_acm_certificates(dry_run):
    """Clean up expired and unused ACM certificates."""
    logger.info(f"Cleaning ACM certificates in {display_aws_account_info()}")

    try:
        acm_client = get_client("acm")

        # Get all certificates
        response = acm_client.list_certificates()
        certificates = response.get("CertificateSummaryList", [])

        if not certificates:
            logger.info("No ACM certificates found")
            return

        logger.info(f"Found {len(certificates)} certificates to check")

        # Track results
        expired_unused = []
        expired_in_use = []
        unused_valid = []
        certificates_deleted = []

        # Check each certificate
        for cert in certificates:
            cert_arn = cert["CertificateArn"]
            cert_status = cert.get("Status", "Unknown")
            cert_in_use = cert.get("InUse", False)

            logger.info(f"Certificate: {cert_arn[:50]}...")
            logger.info(f"  Status: {cert_status}, In Use: {cert_in_use}")

            # Categorize certificates
            if cert_status == "EXPIRED" and not cert_in_use:
                expired_unused.append(cert_arn)
                logger.info(f"  → Expired and unused - candidate for deletion")

                # Delete if not in dry-run mode
                if not dry_run:
                    try:
                        acm_client.delete_certificate(CertificateArn=cert_arn)
                        certificates_deleted.append(cert_arn)
                        logger.info(f"  ✓ Successfully deleted")
                    except ClientError as e:
                        logger.error(f"  ✗ Failed to delete: {e}")

            elif cert_status == "EXPIRED" and cert_in_use:
                expired_in_use.append(cert_arn)
                logger.info(f"  ⚠ Expired but still in use - requires manual review")

            elif not cert_in_use and cert_status in ["ISSUED", "PENDING_VALIDATION"]:
                unused_valid.append(cert_arn)
                logger.info(f"  ⚠ Valid but unused - consider for cleanup")

            else:
                logger.info(f"  ✓ Active certificate")

        # Summary
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Total certificates: {len(certificates)}")
        logger.info(f"Expired & unused: {len(expired_unused)}")
        logger.info(f"Expired but in use: {len(expired_in_use)}")
        logger.info(f"Valid but unused: {len(unused_valid)}")

        if dry_run and expired_unused:
            logger.info(f"To delete {len(expired_unused)} expired certificates, run with --no-dry-run")
        elif not dry_run:
            logger.info(f"Successfully deleted {len(certificates_deleted)} certificates")

        if expired_in_use:
            logger.warning(f"⚠ {len(expired_in_use)} expired certificates are still in use - manual review needed")

    except ClientError as e:
        logger.error(f"Failed to process ACM certificates: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    clean_acm_certificates()
