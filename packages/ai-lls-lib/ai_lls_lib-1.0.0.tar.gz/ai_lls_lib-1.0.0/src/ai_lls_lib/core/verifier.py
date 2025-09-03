"""
Phone verification logic - checks line type and DNC status
"""
import os
import re
from datetime import datetime, timezone
from typing import Optional
import httpx
import phonenumbers
from aws_lambda_powertools import Logger
from .models import PhoneVerification, LineType, VerificationSource
from .cache import DynamoDBCache

logger = Logger()


class PhoneVerifier:
    """Verifies phone numbers for line type and DNC status"""

    def __init__(self, cache: DynamoDBCache):
        self.cache = cache
        self.dnc_api_key = os.environ.get("DNC_API_KEY", "")
        self.phone_api_key = os.environ.get("PHONE_VERIFY_API_KEY", "")
        self.http_client = httpx.Client(timeout=10.0)

    def normalize_phone(self, phone: str) -> str:
        """Normalize phone to E.164 format"""
        try:
            # Parse with US as default country
            parsed = phonenumbers.parse(phone, "US")
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError(f"Invalid phone number: {phone}")

            # Format as E.164
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            logger.error(f"Phone normalization failed: {str(e)}")
            raise ValueError(f"Invalid phone format: {phone}")

    def verify_sync(self, phone: str) -> PhoneVerification:
        """Synchronous verification for Lambda handlers"""
        normalized = self.normalize_phone(phone)

        # Check cache first
        cached = self.cache.get(normalized)
        if cached:
            return cached

        # Call external APIs
        line_type = self._check_line_type_sync(normalized)
        dnc_status = self._check_dnc_sync(normalized)

        result = PhoneVerification(
            phone_number=normalized,
            line_type=line_type,
            dnc=dnc_status,
            cached=False,
            verified_at=datetime.now(timezone.utc),
            source=VerificationSource.API
        )

        # Store in cache
        self.cache.set(normalized, result)

        return result

    def _check_line_type_sync(self, phone: str) -> LineType:
        """Check if phone is mobile/landline/voip"""
        # TODO: Implement actual API call to phone verification service
        # Would use self.phone_api_key to authenticate
        logger.info(f"Checking line type for {phone[:6]}***")

        # Stub implementation based on last digit
        last_digit = phone[-1] if phone else '5'
        if last_digit in ['2', '0']:
            return LineType.LANDLINE
        else:
            return LineType.MOBILE

    def _check_dnc_sync(self, phone: str) -> bool:
        """Check if phone is on DNC list"""
        # TODO: Implement actual DNC API call
        # Would use self.dnc_api_key or os.environ.get("DNC_CHECK_API_KEY")
        logger.info(f"Checking DNC status for {phone[:6]}***")

        # Stub implementation based on last digit:
        # - Ends in 1 or 0: on DNC list
        # - Otherwise: not on DNC
        last_digit = phone[-1] if phone else '5'
        return last_digit in ['1', '0']

    def __del__(self):
        """Cleanup HTTP client"""
        if hasattr(self, 'http_client'):
            self.http_client.close()
