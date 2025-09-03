# NOTE: This tool is not used in the project and is only kept for reference

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from ..logger import logger


class SensitivityLevel(Enum):
    """Risk levels for sensitive data classification."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ComplianceType(Enum):
    """Compliance frameworks for data classification."""

    GDPR = "GDPR"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI-DSS"
    CCPA = "CCPA"
    SOX = "SOX"


@dataclass
class SensitivePattern:
    """Definition of a sensitive data pattern."""

    name: str
    regex: str
    column_name_patterns: List[str]
    risk_score: int
    sensitivity_level: SensitivityLevel
    compliance_frameworks: List[ComplianceType]
    description: str


@dataclass
class SensitiveDataFinding:
    """A finding of sensitive data in a specific column."""

    table_name: str
    column_name: str
    pattern_name: str
    sensitivity_level: SensitivityLevel
    risk_score: int
    compliance_frameworks: List[ComplianceType]
    match_count: int
    sample_matches: List[str]
    column_data_type: str
    detection_method: str  # "pattern_match", "column_name", "both"


class SensitiveDataScanner:
    """Scanner for discovering sensitive data in MySQL databases."""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.patterns = self._initialize_patterns()
        self._compiled_regexes = {}
        self._compile_patterns()

    def _initialize_patterns(self) -> List[SensitivePattern]:
        """Initialize built-in sensitive data patterns."""
        return [
            # Email Patterns
            SensitivePattern(
                name="email_address",
                regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                column_name_patterns=[
                    "email",
                    "e_mail",
                    "mail",
                    "contact",
                    "user_email",
                ],
                risk_score=70,
                sensitivity_level=SensitivityLevel.HIGH,
                compliance_frameworks=[ComplianceType.GDPR, ComplianceType.CCPA],
                description="Email addresses (personal identifiable information)",
            ),
            # Phone Number Patterns
            SensitivePattern(
                name="phone_number",
                regex=r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b|(?:\+?[1-9]\d{0,3}[-.\s]?)?\(?[0-9]{1,4}\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}",
                column_name_patterns=[
                    "phone",
                    "telephone",
                    "mobile",
                    "cell",
                    "contact_number",
                    "tel",
                ],
                risk_score=65,
                sensitivity_level=SensitivityLevel.MEDIUM,
                compliance_frameworks=[ComplianceType.GDPR, ComplianceType.CCPA],
                description="Phone numbers (personal contact information)",
            ),
            # Social Security Number
            SensitivePattern(
                name="social_security_number",
                regex=r"\b(?!000|666|9\d{2})\d{3}[-.\s]?(?!00)\d{2}[-.\s]?(?!0000)\d{4}\b",
                column_name_patterns=[
                    "ssn",
                    "social_security",
                    "social_sec",
                    "ss_number",
                ],
                risk_score=95,
                sensitivity_level=SensitivityLevel.CRITICAL,
                compliance_frameworks=[
                    ComplianceType.GDPR,
                    ComplianceType.CCPA,
                    ComplianceType.SOX,
                ],
                description="Social Security Numbers (high-risk PII)",
            ),
            # Credit Card Numbers
            SensitivePattern(
                name="credit_card_number",
                regex=r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
                column_name_patterns=[
                    "credit_card",
                    "card_number",
                    "cc_number",
                    "payment_card",
                    "card_no",
                ],
                risk_score=90,
                sensitivity_level=SensitivityLevel.CRITICAL,
                compliance_frameworks=[ComplianceType.PCI_DSS, ComplianceType.GDPR],
                description="Credit card numbers (payment card industry data)",
            ),
            # Bank Account Numbers
            SensitivePattern(
                name="bank_account_number",
                regex=r"\b[0-9]{8,17}\b",
                column_name_patterns=[
                    "account_number",
                    "bank_account",
                    "acct_num",
                    "routing_number",
                    "aba_number",
                ],
                risk_score=85,
                sensitivity_level=SensitivityLevel.HIGH,
                compliance_frameworks=[ComplianceType.GDPR, ComplianceType.SOX],
                description="Bank account numbers (financial information)",
            ),
            # Tax ID Numbers
            SensitivePattern(
                name="tax_id_number",
                regex=r"\b\d{2}-\d{7}\b",
                column_name_patterns=["tax_id", "ein", "employer_id", "federal_tax_id"],
                risk_score=80,
                sensitivity_level=SensitivityLevel.HIGH,
                compliance_frameworks=[ComplianceType.SOX, ComplianceType.GDPR],
                description="Tax identification numbers (business/individual tax data)",
            ),
            # Medical Record Numbers
            SensitivePattern(
                name="medical_record_number",
                regex=r"\b[A-Z]{2,3}[0-9]{6,10}\b",
                column_name_patterns=[
                    "mrn",
                    "medical_record",
                    "patient_id",
                    "health_id",
                    "medical_number",
                ],
                risk_score=90,
                sensitivity_level=SensitivityLevel.CRITICAL,
                compliance_frameworks=[ComplianceType.HIPAA, ComplianceType.GDPR],
                description="Medical record numbers (protected health information)",
            ),
            # Medication Names
            SensitivePattern(
                name="medication_names",
                regex=r"\b(?:acetaminophen|ibuprofen|aspirin|prednisone|metformin|lisinopril|amlodipine|atorvastatin|omeprazole|losartan|levothyroxine|albuterol|hydrochlorothiazide|furosemide|gabapentin|sertraline|escitalopram|duloxetine|trazodone|lorazepam|alprazolam|clonazepam)\b",
                column_name_patterns=[
                    "medication",
                    "drug",
                    "prescription",
                    "medicine",
                    "rx",
                ],
                risk_score=85,
                sensitivity_level=SensitivityLevel.HIGH,
                compliance_frameworks=[ComplianceType.HIPAA, ComplianceType.GDPR],
                description="Medication names (protected health information)",
            ),
            # GPS Coordinates
            SensitivePattern(
                name="gps_coordinates",
                regex=r"[-+]?(?:[1-8]?\d(?:\.\d+)?|90(?:\.0+)?),\s*[-+]?(?:180(?:\.0+)?|(?:(?:1[0-7]\d)|(?:[1-9]?\d))(?:\.\d+)?)",
                column_name_patterns=[
                    "latitude",
                    "longitude",
                    "lat",
                    "lng",
                    "coordinates",
                    "location",
                    "gps",
                ],
                risk_score=75,
                sensitivity_level=SensitivityLevel.HIGH,
                compliance_frameworks=[ComplianceType.GDPR, ComplianceType.CCPA],
                description="GPS coordinates (location tracking data)",
            ),
            # IP Addresses
            SensitivePattern(
                name="ip_address",
                regex=r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
                column_name_patterns=[
                    "ip_address",
                    "ip",
                    "client_ip",
                    "remote_ip",
                    "user_ip",
                ],
                risk_score=60,
                sensitivity_level=SensitivityLevel.MEDIUM,
                compliance_frameworks=[ComplianceType.GDPR, ComplianceType.CCPA],
                description="IP addresses (network identification data)",
            ),
            # Full Names
            SensitivePattern(
                name="full_name",
                regex=r"\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b",
                column_name_patterns=[
                    "full_name",
                    "name",
                    "first_name",
                    "last_name",
                    "customer_name",
                    "user_name",
                    "patient_name",
                ],
                risk_score=70,
                sensitivity_level=SensitivityLevel.HIGH,
                compliance_frameworks=[
                    ComplianceType.GDPR,
                    ComplianceType.CCPA,
                    ComplianceType.HIPAA,
                ],
                description="Personal names (personal identifiable information)",
            ),
            # Driver's License
            SensitivePattern(
                name="drivers_license",
                regex=r"\b[A-Z]{1,2}[0-9]{6,8}\b",
                column_name_patterns=[
                    "license",
                    "drivers_license",
                    "dl_number",
                    "driver_id",
                ],
                risk_score=80,
                sensitivity_level=SensitivityLevel.HIGH,
                compliance_frameworks=[ComplianceType.GDPR, ComplianceType.CCPA],
                description="Driver's license numbers (government-issued ID)",
            ),
            # Passport Numbers
            SensitivePattern(
                name="passport_number",
                regex=r"\b[A-Z]{1,2}[0-9]{6,9}\b",
                column_name_patterns=["passport", "passport_number", "passport_no"],
                risk_score=90,
                sensitivity_level=SensitivityLevel.CRITICAL,
                compliance_frameworks=[ComplianceType.GDPR, ComplianceType.CCPA],
                description="Passport numbers (international travel documents)",
            ),
        ]

    def _compile_patterns(self):
        """Compile regex patterns for performance."""
        for pattern in self.patterns:
            try:
                self._compiled_regexes[pattern.name] = re.compile(
                    pattern.regex, re.IGNORECASE
                )
            except re.error as e:
                logger.warning(
                    f"Failed to compile regex for pattern {pattern.name}: {e}"
                )

    def add_custom_pattern(self, pattern: SensitivePattern):
        """Add a custom sensitive data pattern."""
        self.patterns.append(pattern)
        try:
            self._compiled_regexes[pattern.name] = re.compile(
                pattern.regex, re.IGNORECASE
            )
        except re.error as e:
            logger.warning(
                f"Failed to compile custom regex for pattern {pattern.name}: {e}"
            )

    async def scan_tables(
        self,
        scan_all: bool = False,
        table_patterns: Optional[List[str]] = None,
        sample_size: int = 1000,
        risk_threshold: int = 50,
    ) -> Dict[str, Any]:
        """Scan tables for sensitive data."""
        try:
            results: Dict[str, Any] = {
                "scan_summary": {},
                "findings": [],
                "risk_assessment": {},
                "recommendations": [],
                "compliance_summary": {},
            }

            # Type hints for better type checking
            findings_list: List[SensitiveDataFinding] = results["findings"]

            # Get list of tables to scan
            tables_to_scan = await self._get_tables_to_scan(scan_all, table_patterns)

            if not tables_to_scan:
                return {
                    "scan_summary": {"message": "No tables found to scan"},
                    "findings": [],
                    "risk_assessment": {"overall_risk_score": 0.0},
                    "recommendations": ["No tables available for scanning"],
                    "compliance_summary": {},
                }

            logger.info(f"Scanning {len(tables_to_scan)} tables for sensitive data")

            total_findings = 0
            high_risk_findings = 0
            compliance_violations = {}

            # Scan each table
            for table_name in tables_to_scan:
                try:
                    table_findings = await self._scan_table(
                        table_name, sample_size, risk_threshold
                    )

                    for finding in table_findings:
                        findings_list.append(finding)
                        total_findings += 1

                        if finding.risk_score >= 80:
                            high_risk_findings += 1

                        # Track compliance violations
                        for framework in finding.compliance_frameworks:
                            if framework.value not in compliance_violations:
                                compliance_violations[framework.value] = 0
                            compliance_violations[framework.value] += 1

                except Exception as e:
                    logger.warning(f"Error scanning table {table_name}: {e}")
                    continue

            # Generate scan summary
            results["scan_summary"] = {
                "total_tables_scanned": len(tables_to_scan),
                "total_findings": total_findings,
                "high_risk_findings": high_risk_findings,
                "sample_size_per_table": sample_size,
            }

            # Calculate overall risk assessment
            if total_findings > 0:
                avg_risk_score = (
                    sum(f.risk_score for f in findings_list) / total_findings
                )
                risk_level = self._calculate_risk_level(avg_risk_score)
            else:
                avg_risk_score = 0.0
                risk_level = SensitivityLevel.LOW

            results["risk_assessment"] = {
                "overall_risk_score": round(avg_risk_score, 2),
                "risk_level": risk_level.value,
                "high_risk_tables": len(
                    set(f.table_name for f in findings_list if f.risk_score >= 80)
                ),
                "critical_findings": len(
                    [
                        f
                        for f in findings_list
                        if f.sensitivity_level == SensitivityLevel.CRITICAL
                    ]
                ),
            }

            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(findings_list)

            # Compliance summary
            results["compliance_summary"] = compliance_violations

            return results

        except Exception as e:
            logger.error(f"Error during sensitive data scan: {e}")
            raise

    async def _get_tables_to_scan(
        self, scan_all: bool, table_patterns: Optional[List[str]]
    ) -> List[str]:
        """Get list of tables to scan based on parameters."""
        try:
            # Get all tables
            query = "SHOW TABLES"
            result = await self.db_manager.execute_query(query)

            if not result.has_results:
                return []

            all_tables = [row[0] for row in result.rows]

            if scan_all:
                return all_tables

            if table_patterns:
                matching_tables = []
                for pattern in table_patterns:
                    # Simple pattern matching (can be enhanced with regex)
                    for table in all_tables:
                        if pattern.lower() in table.lower():
                            matching_tables.append(table)
                return list(set(matching_tables))

            # Default: return first 10 tables for safety
            return all_tables[:10]

        except Exception as e:
            logger.error(f"Error getting tables to scan: {e}")
            return []

    async def _scan_table(
        self, table_name: str, sample_size: int, risk_threshold: int
    ) -> List[SensitiveDataFinding]:
        """Scan a specific table for sensitive data."""
        findings = []

        try:
            # Get table structure
            describe_query = f"DESCRIBE `{table_name}`"
            describe_result = await self.db_manager.execute_query(describe_query)

            if not describe_result.has_results:
                return findings

            columns_info = {
                row[0]: {"type": row[1], "nullable": row[2], "key": row[3]}
                for row in describe_result.rows
            }

            # Get row count for sampling strategy
            count_query = f"SELECT COUNT(*) FROM `{table_name}`"
            count_result = await self.db_manager.execute_query(count_query)
            total_rows = count_result.rows[0][0] if count_result.has_results else 0

            # Sample data if table is large
            if total_rows > sample_size:
                # Use random sampling
                data_query = (
                    f"SELECT * FROM `{table_name}` ORDER BY RAND() LIMIT {sample_size}"
                )
            else:
                data_query = f"SELECT * FROM `{table_name}` LIMIT {sample_size}"

            data_result = await self.db_manager.execute_query(data_query)

            if not data_result.has_results:
                return findings

            # Scan each column
            for col_index, column_name in enumerate(data_result.columns):
                if column_name not in columns_info:
                    continue

                column_data_type = columns_info[column_name]["type"]
                column_values = [
                    str(row[col_index]) if row[col_index] is not None else ""
                    for row in data_result.rows
                ]

                # Check for patterns in this column
                column_findings = self._scan_column(
                    table_name,
                    column_name,
                    column_data_type,
                    column_values,
                    risk_threshold,
                )

                findings.extend(column_findings)

        except Exception as e:
            logger.warning(f"Error scanning table {table_name}: {e}")

        return findings

    def _scan_column(
        self,
        table_name: str,
        column_name: str,
        column_data_type: str,
        column_values: List[str],
        risk_threshold: int,
    ) -> List[SensitiveDataFinding]:
        """Scan a specific column for sensitive data patterns."""
        findings = []

        try:
            for pattern in self.patterns:
                if pattern.risk_score < risk_threshold:
                    continue

                matches = []
                detection_method = ""

                # Check column name patterns
                column_name_match = any(
                    col_pattern.lower() in column_name.lower()
                    for col_pattern in pattern.column_name_patterns
                )

                # Check data content patterns
                if pattern.name in self._compiled_regexes:
                    regex = self._compiled_regexes[pattern.name]
                    content_matches = []

                    for value in column_values:
                        if value and len(str(value).strip()) > 0:
                            found_matches = regex.findall(str(value))
                            content_matches.extend(found_matches)

                    content_match = len(content_matches) > 0
                    if content_match:
                        matches = content_matches[:5]  # Keep sample matches
                else:
                    content_match = False

                # Determine detection method
                if column_name_match and content_match:
                    detection_method = "both"
                elif column_name_match:
                    detection_method = "column_name"
                elif content_match:
                    detection_method = "pattern_match"
                else:
                    continue  # No match found

                # Only create finding if we have a match
                if column_name_match or content_match:
                    finding = SensitiveDataFinding(
                        table_name=table_name,
                        column_name=column_name,
                        pattern_name=pattern.name,
                        sensitivity_level=pattern.sensitivity_level,
                        risk_score=pattern.risk_score,
                        compliance_frameworks=pattern.compliance_frameworks,
                        match_count=len(matches) if content_match else 1,
                        sample_matches=matches[:3] if matches else [],
                        column_data_type=column_data_type,
                        detection_method=detection_method,
                    )
                    findings.append(finding)

        except Exception as e:
            logger.warning(f"Error scanning column {column_name}: {e}")

        return findings

    def _calculate_risk_level(self, risk_score: float) -> SensitivityLevel:
        """Calculate risk level based on numeric score."""
        if risk_score >= 90:
            return SensitivityLevel.CRITICAL
        elif risk_score >= 70:
            return SensitivityLevel.HIGH
        elif risk_score >= 50:
            return SensitivityLevel.MEDIUM
        else:
            return SensitivityLevel.LOW

    def _generate_recommendations(
        self, findings: List[SensitiveDataFinding]
    ) -> List[str]:
        """Generate security recommendations based on findings."""
        recommendations = []

        if not findings:
            recommendations.append(
                "✅ No sensitive data patterns detected in scanned tables"
            )
            return recommendations

        # High-level recommendations
        critical_findings = [
            f for f in findings if f.sensitivity_level == SensitivityLevel.CRITICAL
        ]
        high_findings = [
            f for f in findings if f.sensitivity_level == SensitivityLevel.HIGH
        ]

        if critical_findings:
            recommendations.append(
                f"🚨 CRITICAL: {len(critical_findings)} critical data exposures found - immediate review required"
            )

        if high_findings:
            recommendations.append(
                f"⚠️ HIGH RISK: {len(high_findings)} high-risk data exposures identified"
            )

        # Specific recommendations by compliance framework
        compliance_findings = {}
        for finding in findings:
            for framework in finding.compliance_frameworks:
                if framework.value not in compliance_findings:
                    compliance_findings[framework.value] = []
                compliance_findings[framework.value].append(finding)

        for framework, framework_findings in compliance_findings.items():
            if framework == "PCI-DSS":
                recommendations.append(
                    f"💳 PCI-DSS: {len(framework_findings)} payment card data findings - encryption/tokenization required"
                )
            elif framework == "HIPAA":
                recommendations.append(
                    f"🏥 HIPAA: {len(framework_findings)} healthcare data findings - access controls and encryption required"
                )
            elif framework == "GDPR":
                recommendations.append(
                    f"🇪🇺 GDPR: {len(framework_findings)} personal data findings - data minimization and consent management required"
                )

        # General security recommendations
        recommendations.extend(
            [
                "🔒 Implement column-level encryption for sensitive data",
                "🔐 Use database access controls and role-based permissions",
                "📝 Maintain data inventory and classification documentation",
                "🔍 Regular auditing of sensitive data access patterns",
                "🗑️ Implement data retention and secure deletion policies",
            ]
        )

        return recommendations


async def discover_sensitive_data_tool(
    scan_all: bool = False,
    table_patterns: Optional[List[str]] = None,
    custom_patterns: Optional[Dict[str, str]] = None,
    risk_threshold: int = 50,
    sample_size: int = 1000,
    db_manager=None,
    security_validator=None,
) -> str:
    """Discover sensitive data patterns in MySQL database.

    Comprehensive sensitive data discovery tool for security compliance and data protection analysis.

    Features:
    - PII Pattern Detection: Names, emails, phone numbers, addresses, SSN patterns
    - Financial Data: Credit cards, bank accounts, tax IDs
    - Medical Data: Health records, medication patterns
    - Location Data: GPS coordinates, IP addresses
    - Custom Patterns: Configurable regex patterns for domain-specific data
    - Risk Assessment: Data sensitivity scoring and exposure analysis
    - Compliance Mapping: GDPR, HIPAA, PCI-DSS, CCPA compliance checking

    Args:
        scan_all: Scan all tables in database (default: False, scans first 10 tables)
        table_patterns: List of table name patterns to scan (e.g., ["user_", "customer_"])
        custom_patterns: Dict of custom regex patterns {"pattern_name": "regex_pattern"}
        risk_threshold: Minimum risk score to report (0-100, default: 50)
        sample_size: Number of rows to sample per table (default: 1000)
        db_manager: Database manager instance
        security_validator: Security validator instance

    Returns:
        Comprehensive sensitive data discovery report with findings and recommendations
    """
    try:
        logger.info("Starting sensitive data discovery scan")

        if not db_manager or not security_validator:
            raise RuntimeError("Server not properly initialized")

        # Initialize scanner
        scanner = SensitiveDataScanner(db_manager)

        # Add custom patterns if provided
        if custom_patterns:
            for name, regex_pattern in custom_patterns.items():
                try:
                    custom_pattern = SensitivePattern(
                        name=f"custom_{name}",
                        regex=regex_pattern,
                        column_name_patterns=[name.lower()],
                        risk_score=75,  # Default high risk for custom patterns
                        sensitivity_level=SensitivityLevel.HIGH,
                        compliance_frameworks=[
                            ComplianceType.GDPR
                        ],  # Default compliance
                        description=f"Custom pattern: {name}",
                    )
                    scanner.add_custom_pattern(custom_pattern)
                except Exception as e:
                    logger.warning(f"Failed to add custom pattern {name}: {e}")

        # Perform scan
        results = await scanner.scan_tables(
            scan_all=scan_all,
            table_patterns=table_patterns,
            sample_size=sample_size,
            risk_threshold=risk_threshold,
        )

        # Format results
        return _format_scan_results(results)

    except Exception as e:
        logger.error(f"Error in sensitive data discovery: {e}")
        return f"Error: {str(e)}"


def _format_scan_results(results: Dict[str, Any]) -> str:
    """Format scan results as agent-readable output."""
    output = []
    output.append("SENSITIVE DATA DISCOVERY REPORT")

    # Scan Summary
    summary = results.get("scan_summary", {})
    if summary:
        output.append("\nSCAN SUMMARY:")
        output.append(f"Tables Scanned: {summary.get('total_tables_scanned', 0)}")
        output.append(f"Total Findings: {summary.get('total_findings', 0)}")
        output.append(f"High Risk Findings: {summary.get('high_risk_findings', 0)}")
        output.append(
            f"Sample Size per Table: {summary.get('sample_size_per_table', 0)}"
        )

    # Risk Assessment
    risk_assessment = results.get("risk_assessment", {})
    if risk_assessment:
        output.append("\nRISK ASSESSMENT:")
        output.append(
            f"Overall Risk Score: {risk_assessment.get('overall_risk_score', 0)}/100"
        )
        output.append(f"Risk Level: {risk_assessment.get('risk_level', 'Unknown')}")
        output.append(f"High Risk Tables: {risk_assessment.get('high_risk_tables', 0)}")
        output.append(
            f"Critical Findings: {risk_assessment.get('critical_findings', 0)}"
        )

    # Detailed Findings
    findings = results.get("findings", [])
    if findings:
        output.append(f"\nDETAILED FINDINGS ({len(findings)} total):")

        # Group findings by table
        findings_by_table = {}
        for finding in findings:
            if finding.table_name not in findings_by_table:
                findings_by_table[finding.table_name] = []
            findings_by_table[finding.table_name].append(finding)

        for table_name, table_findings in findings_by_table.items():
            output.append(f"\nTable: {table_name}")
            for finding in table_findings:
                risk_level = (
                    "CRITICAL"
                    if finding.risk_score >= 90
                    else "HIGH"
                    if finding.risk_score >= 70
                    else "MEDIUM"
                    if finding.risk_score >= 50
                    else "LOW"
                )
                output.append(f"  [{risk_level}] Column: {finding.column_name}")
                output.append(
                    f"    Pattern: {finding.pattern_name.replace('_', ' ').title()}"
                )
                output.append(
                    f"    Risk Score: {finding.risk_score}/100 ({finding.sensitivity_level.value})"
                )
                output.append(f"    Data Type: {finding.column_data_type}")
                output.append(
                    f"    Detection: {finding.detection_method.replace('_', ' ').title()}"
                )

                if finding.compliance_frameworks:
                    frameworks = [f.value for f in finding.compliance_frameworks]
                    output.append(f"    Compliance: {', '.join(frameworks)}")

                if finding.sample_matches:
                    output.append(
                        f"    Sample Matches: {len(finding.sample_matches)} found"
                    )
                    for i, match in enumerate(finding.sample_matches[:2], 1):
                        # Mask sensitive data in output
                        masked_match = (
                            match[:3] + "*" * (len(match) - 6) + match[-3:]
                            if len(match) > 6
                            else "*" * len(match)
                        )
                        output.append(f"      {i}. {masked_match}")

    # Compliance Summary
    compliance_summary = results.get("compliance_summary", {})
    if compliance_summary:
        output.append("\nCOMPLIANCE IMPACT:")
        for framework, count in compliance_summary.items():
            output.append(f"{framework}: {count} findings")

    # Recommendations
    recommendations = results.get("recommendations", [])
    if recommendations:
        output.append("\nSECURITY RECOMMENDATIONS:")
        for rec in recommendations:
            output.append(f"- {rec}")

    # Footer
    output.append(
        "\nThis scan identifies sensitive data for security and compliance purposes."
    )
    output.append("Review findings and implement appropriate data protection measures.")

    return "\n".join(output)
