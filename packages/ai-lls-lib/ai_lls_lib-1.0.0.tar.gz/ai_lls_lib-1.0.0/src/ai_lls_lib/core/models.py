"""
Data models for phone verification
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class LineType(str, Enum):
    """Phone line type enumeration"""
    MOBILE = "mobile"
    LANDLINE = "landline"
    VOIP = "voip"
    UNKNOWN = "unknown"


class VerificationSource(str, Enum):
    """Source of verification data"""
    API = "api"
    CACHE = "cache"
    BULK_IMPORT = "bulk_import"


class JobStatus(str, Enum):
    """Bulk job status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PhoneVerification(BaseModel):
    """Result of phone number verification"""
    phone_number: str = Field(..., description="E.164 formatted phone number")
    line_type: LineType = Field(
        ..., description="Type of phone line"
    )
    dnc: bool = Field(..., description="Whether number is on DNC list")
    cached: bool = Field(..., description="Whether result came from cache")
    verified_at: datetime = Field(..., description="When verification occurred")
    source: VerificationSource = Field(
        ..., description="Source of verification data"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BulkJob(BaseModel):
    """Bulk processing job metadata"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(
        ..., description="Current job status"
    )


class BulkJobStatus(BulkJob):
    """Extended bulk job status with progress info"""
    total_rows: Optional[int] = Field(None, description="Total rows to process")
    processed_rows: Optional[int] = Field(None, description="Rows processed so far")
    result_url: Optional[str] = Field(None, description="S3 URL of results")
    created_at: datetime = Field(..., description="Job creation time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
    error: Optional[str] = Field(None, description="Error message if failed")


class CacheEntry(BaseModel):
    """DynamoDB cache entry"""
    phone_number: str
    line_type: str  # Stored as string in DynamoDB
    dnc: bool
    verified_at: str  # ISO format string
    source: str  # Stored as string in DynamoDB
    ttl: int  # Unix timestamp for DynamoDB TTL
