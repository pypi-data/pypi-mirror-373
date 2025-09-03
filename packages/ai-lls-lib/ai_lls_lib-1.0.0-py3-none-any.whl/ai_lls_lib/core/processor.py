"""
Bulk CSV processing for phone verification
"""
import csv
from typing import List, Optional
from aws_lambda_powertools import Logger
from .models import PhoneVerification
from .verifier import PhoneVerifier

logger = Logger()


class BulkProcessor:
    """Process CSV files for bulk phone verification"""

    def __init__(self, verifier: PhoneVerifier):
        self.verifier = verifier

    def process_csv_sync(self, file_path: str, phone_column: str = "phone") -> List[PhoneVerification]:
        """
        Process CSV file synchronously.
        Returns list of verification results.
        """
        results = []

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)

                # Find phone column (case-insensitive)
                headers = reader.fieldnames or []
                phone_col = self._find_phone_column(headers, phone_column)

                if not phone_col:
                    raise ValueError(f"Phone column '{phone_column}' not found in CSV")

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                    try:
                        phone = row.get(phone_col, "").strip()
                        if not phone:
                            logger.warning(f"Empty phone at row {row_num}")
                            continue

                        # Verify phone
                        result = self.verifier.verify_sync(phone)
                        results.append(result)

                        # Log progress every 100 rows
                        if len(results) % 100 == 0:
                            logger.info(f"Processed {len(results)} phones")

                    except ValueError as e:
                        logger.warning(f"Invalid phone at row {row_num}: {str(e)}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing row {row_num}: {str(e)}")
                        continue

                logger.info(f"Completed processing {len(results)} valid phones")

        except Exception as e:
            logger.error(f"CSV processing failed: {str(e)}")
            raise

        return results

    def _find_phone_column(self, headers: List[str], preferred: str) -> Optional[str]:
        """Find phone column in headers (case-insensitive)"""
        # First try exact match
        for header in headers:
            if header.lower() == preferred.lower():
                return header

        # Common phone column names
        phone_patterns = [
            "phone", "phone_number", "phonenumber", "mobile",
            "cell", "telephone", "tel", "number", "contact"
        ]

        for header in headers:
            header_lower = header.lower()
            for pattern in phone_patterns:
                if pattern in header_lower:
                    logger.info(f"Using column '{header}' as phone column")
                    return header

        return None

    def generate_results_csv(
        self,
        original_path: str,
        results: List[PhoneVerification],
        output_path: str
    ) -> None:
        """
        Generate CSV with original data plus verification results.
        Adds columns: line_type, dnc, cached
        """
        # Create lookup dict
        results_map = {r.phone_number: r for r in results}

        with open(original_path, 'r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            headers = reader.fieldnames or []

            # Add new columns
            output_headers = headers + ["line_type", "dnc", "cached"]

            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_headers)
                writer.writeheader()

                phone_col = self._find_phone_column(headers, "phone")

                for row in reader:
                    phone = row.get(phone_col, "").strip()

                    # Try to normalize for lookup
                    try:
                        normalized = self.verifier.normalize_phone(phone)
                        if normalized in results_map:
                            result = results_map[normalized]
                            row["line_type"] = result.line_type
                            row["dnc"] = "true" if result.dnc else "false"
                            row["cached"] = "true" if result.cached else "false"
                        else:
                            row["line_type"] = "unknown"
                            row["dnc"] = ""
                            row["cached"] = ""
                    except:
                        row["line_type"] = "invalid"
                        row["dnc"] = ""
                        row["cached"] = ""

                    writer.writerow(row)
