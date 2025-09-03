import unittest

from src.aws.lambda_list import update_policy_document


class TestUpdatePolicyDocument(unittest.TestCase):
    def test_update_policy_document_simple(self):
        # Define a policy document for testing
        policy_document = {
            "policy1": {
                "Statement": [
                    {"Action": "*", "Resource": "arn:aws:cloudformation:*:*:*"},
                    {"Action": "codepipeline:PutJobSuccessResult", "Resource": "*"},
                ]
            }
        }

        # Call the function with the test policy document
        changes, new_policy_document = update_policy_document(policy_document)

        # Define the expected results
        expected_changes = {"policy1": ["cloudformation:*", "arn:aws:codepipeline:*:*:*"]}
        expected_new_policy_document = {
            "policy1": {
                "Statement": [
                    {"Action": "cloudformation:*", "Resource": "arn:aws:cloudformation:*:*:*"},
                    {"Action": "codepipeline:PutJobSuccessResult", "Resource": "arn:aws:codepipeline:*:*:*"},
                ]
            }
        }

        # Assert that the function returns the expected results
        self.assertEqual(changes, expected_changes)
        self.assertEqual(new_policy_document, expected_new_policy_document)

    def test_update_policy_document_no_change(self):
        policy_document = {
            "MeterWriteService-prod-lambda": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": ["cloudformation:Describe*"],
                        "Resource": ["arn:aws:cloudformation:*:*:*"],
                        "Effect": "Allow",
                    },
                    {
                        "Action": [
                            "codepipeline:PutJobSuccessResult",
                            "codepipeline:PutJobFailureResult",
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:Describe*",
                            "logs:PutLogEvents",
                            "s3:List*",
                        ],
                        "Resource": ["arn:aws:codepipeline:*:*:*", "arn:aws:logs:*:*:*", "arn:aws:s3:::*"],
                        "Effect": "Allow",
                    },
                    {
                        "Action": ["s3:Get*", "s3:Put*"],
                        "Resource": [
                            "arn:aws:s3:::prod-meterwriteservice-cd-codepipelineartifactbuck-ueiwuorier",
                            "arn:aws:s3:::prod-meterwriteservice-cd-codepipelineartifactbuck-ueiwuorier/*",
                        ],
                        "Effect": "Allow",
                    },
                ],
            }
        }

        changes, new_policy_document = update_policy_document(policy_document)

        expected_changes = {}
        self.assertEqual(changes, expected_changes)
