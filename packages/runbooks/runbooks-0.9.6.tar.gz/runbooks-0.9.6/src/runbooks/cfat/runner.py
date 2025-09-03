"""
Cloud Foundations Assessment Tool - Backward Compatibility Module.

This module maintains backward compatibility for existing code
while providing access to the enhanced assessment engine.

For new implementations, consider using the enhanced assessment
module directly:

    from runbooks.cfat.assessment import CloudFoundationsAssessment

This module will be deprecated in a future version.
"""

from typing import Optional

from loguru import logger

from runbooks.cfat.assessment.runner import CloudFoundationsAssessment
from runbooks.config import RunbooksConfig


class AssessmentRunner(CloudFoundationsAssessment):
    """
    Backward Compatibility Wrapper for Cloud Foundations Assessment.

    This class provides backward compatibility for existing code that
    uses the original AssessmentRunner class. All functionality is
    delegated to the enhanced CloudFoundationsAssessment engine.

    **Deprecation Notice**: This class is deprecated and will be removed
    in a future version. Please migrate to using CloudFoundationsAssessment
    directly:

    ```python
    # Old way (deprecated)
    from runbooks.cfat.runner import AssessmentRunner
    runner = AssessmentRunner()

    # New way (recommended)
    from runbooks.cfat.assessment import CloudFoundationsAssessment
    assessment = CloudFoundationsAssessment()
    ```

    Args:
        profile: AWS CLI profile for authentication
        region: AWS region for assessment
        config: RunbooksConfig instance for configuration
    """

    def __init__(
        self, profile: Optional[str] = None, region: Optional[str] = None, config: Optional[RunbooksConfig] = None
    ):
        """
        Initialize backward compatibility wrapper.

        Args:
            profile: AWS CLI profile to use
            region: AWS region for assessment
            config: Configuration object
        """
        # Log deprecation warning
        logger.warning(
            "AssessmentRunner is deprecated. Please use CloudFoundationsAssessment "
            "from runbooks.cfat.assessment instead."
        )

        # Initialize the enhanced assessment engine
        super().__init__(profile=profile, region=region, config=config)
