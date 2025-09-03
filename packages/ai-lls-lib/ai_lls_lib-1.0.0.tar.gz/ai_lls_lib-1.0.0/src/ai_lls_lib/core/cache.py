"""
DynamoDB cache implementation for phone verifications
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import boto3
from aws_lambda_powertools import Logger
from .models import PhoneVerification, CacheEntry

logger = Logger()


class DynamoDBCache:
    """Cache for phone verification results using DynamoDB with TTL"""

    def __init__(self, table_name: str, ttl_days: int = 30):
        self.table_name = table_name
        self.ttl_days = ttl_days
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def get(self, phone_number: str) -> Optional[PhoneVerification]:
        """Get cached verification result"""
        try:
            response = self.table.get_item(Key={"phone_number": phone_number})

            if "Item" not in response:
                logger.info(f"Cache miss for {phone_number[:6]}***")
                return None

            item = response["Item"]
            logger.info(f"Cache hit for {phone_number[:6]}***")

            return PhoneVerification(
                phone_number=item["phone_number"],
                line_type=item["line_type"],
                dnc=item["dnc"],
                cached=True,
                verified_at=datetime.fromisoformat(item["verified_at"]),
                source="cache"
            )

        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    def set(self, phone_number: str, verification: PhoneVerification) -> None:
        """Store verification result in cache"""
        try:
            ttl = int((datetime.now(timezone.utc) + timedelta(days=self.ttl_days)).timestamp())

            self.table.put_item(
                Item={
                    "phone_number": phone_number,
                    "line_type": verification.line_type,
                    "dnc": verification.dnc,
                    "verified_at": verification.verified_at.isoformat(),
                    "source": verification.source,
                    "ttl": ttl
                }
            )

            logger.info(f"Cached result for {phone_number[:6]}***")

        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            # Don't fail the request if cache write fails

    def batch_get(self, phone_numbers: list[str]) -> dict[str, Optional[PhoneVerification]]:
        """Get multiple cached results"""
        results = {}

        # DynamoDB batch get (max 100 items per request)
        for i in range(0, len(phone_numbers), 100):
            batch = phone_numbers[i:i+100]

            try:
                response = self.dynamodb.batch_get_item(
                    RequestItems={
                        self.table_name: {
                            "Keys": [{"phone_number": phone} for phone in batch]
                        }
                    }
                )

                for item in response.get("Responses", {}).get(self.table_name, []):
                    phone = item["phone_number"]
                    results[phone] = PhoneVerification(
                        phone_number=phone,
                        line_type=item["line_type"],
                        dnc=item["dnc"],
                        cached=True,
                        verified_at=datetime.fromisoformat(item["verified_at"]),
                        source="cache"
                    )

            except Exception as e:
                logger.error(f"Batch cache get error: {str(e)}")

        # Fill in None for misses
        for phone in phone_numbers:
            if phone not in results:
                results[phone] = None

        return results
