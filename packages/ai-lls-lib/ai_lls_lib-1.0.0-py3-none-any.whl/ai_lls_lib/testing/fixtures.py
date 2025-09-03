"""
Test fixtures and utilities for ai-lls-lib
"""
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from ai_lls_lib.core.models import PhoneVerification, LineType, VerificationSource

# Sample phone numbers for testing
# Using 201-555-01XX format which is designated for testing
TEST_PHONES = {
    "valid_mobile": "+12015550153",  # Ends in 3 - mobile, not on DNC
    "valid_landline": "+12015550152",  # Ends in 2 - landline, not on DNC
    "dnc_mobile": "+12015550151",  # Ends in 1 - mobile, on DNC
    "dnc_landline": "+12015550150",  # Ends in 0 - landline, on DNC
    "invalid": "not-a-phone",
    "missing_country": "2015550123",
    "international": "+442071234567",
}

def create_test_verification(
    phone: str = TEST_PHONES["valid_mobile"],
    line_type: LineType = LineType.MOBILE,
    dnc: bool = False,
    cached: bool = False,
    source: VerificationSource = VerificationSource.API
) -> PhoneVerification:
    """Create a test PhoneVerification object"""
    return PhoneVerification(
        phone_number=phone,
        line_type=line_type,
        dnc=dnc,
        cached=cached,
        verified_at=datetime.now(timezone.utc),
        source=source
    )

def create_test_csv_content(phones: List[str] = None) -> str:
    """Create CSV content for testing bulk processing"""
    if phones is None:
        phones = [
            TEST_PHONES["valid_mobile"],
            TEST_PHONES["valid_landline"],
            TEST_PHONES["dnc_mobile"],
        ]

    lines = ["name,phone,email"]
    for i, phone in enumerate(phones):
        lines.append(f"Test User {i},{phone},test{i}@example.com")

    return "\n".join(lines)

def create_dynamodb_item(phone: str, line_type: LineType = LineType.MOBILE, dnc: bool = False) -> Dict[str, Any]:
    """Create a DynamoDB item for testing"""
    ttl = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp())

    return {
        "phone_number": phone,
        "line_type": line_type.value,  # Store as string in DynamoDB
        "dnc": dnc,
        "cached": True,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "source": VerificationSource.CACHE.value,  # Store as string in DynamoDB
        "ttl": ttl
    }

def create_sqs_message(file_id: str, bucket: str, key: str, user_id: str) -> Dict[str, Any]:
    """Create an SQS message for bulk processing"""
    return {
        "file_id": file_id,
        "bucket": bucket,
        "key": key,
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

def create_api_gateway_event(
    phone: str = None,
    user_id: str = "test-user",
    method: str = "GET",
    path: str = "/verify"
) -> Dict[str, Any]:
    """Create an API Gateway event for Lambda testing"""
    event = {
        "httpMethod": method,
        "path": path,
        "headers": {
            "Authorization": "Bearer test-token"
        },
        "requestContext": {
            "authorizer": {
                "lambda": {
                    "principal_id": user_id,
                    "claims": {
                        "email": f"{user_id}@example.com"
                    }
                }
            }
        }
    }

    if phone:
        event["queryStringParameters"] = {"p": phone}

    return event
