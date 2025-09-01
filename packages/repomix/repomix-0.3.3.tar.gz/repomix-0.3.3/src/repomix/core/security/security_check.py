"""
Security Check Module - Responsible for Checking File and Directory Security
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Set, Dict

from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.settings import default_settings

from ...shared.logger import logger


@dataclass
class SuspiciousFileResult:
    """Suspicious File Result Class

    Attributes:
        file_path: File path as string
        messages: List of suspicious reasons
    """

    file_path: str  # Keep as string for serialization compatibility
    messages: List[str]


class SecurityChecker:
    """Security Checker Class"""

    # Suspicious file name patterns
    SUSPICIOUS_FILE_PATTERNS = [
        r"\.env($|\..*$)",  # Environment variable files
        r".*_rsa$",  # RSA keys
        r".*\.pem$",  # PEM certificates
        r".*\.key$",  # Key files
        r".*\.pfx$",  # PFX certificates
        r".*\.p12$",  # P12 certificates
        r".*\.pkcs12$",  # PKCS12 certificates
        r".*\.keystore$",  # Keystore
        r".*\.jks$",  # Java keystore
        r".*\.kdbx$",  # KeePass database
        r".*\.psafe3$",  # Password Safe database
    ]

    # Suspicious file content patterns
    SUSPICIOUS_CONTENT_PATTERNS = [
        # API keys - more flexible patterns
        r"api[_-]?key.*['\"][^'\"]{10,}['\"]",
        r"api[_-]?secret.*['\"][^'\"]{10,}['\"]",
        # Access tokens
        r"access[_-]?token.*['\"][^'\"]{10,}['\"]",
        r"auth[_-]?token.*['\"][^'\"]{10,}['\"]",
        # Common API key patterns - more flexible
        r"['\"]sk[-_][0-9a-zA-Z_-]*[0-9a-zA-Z]['\"]",  # Stripe-like keys (sk- or sk_)
        r"['\"]pk[-_][0-9a-zA-Z_-]*[0-9a-zA-Z]['\"]",  # Public keys
        r"['\"]ghp_[0-9a-zA-Z]{30,}['\"]",  # GitHub personal access tokens (more flexible length)
        # AWS related
        r"AKIA[0-9A-Z]{16}",  # AWS access key ID
        r"aws[_-]?secret.*['\"][0-9a-zA-Z/+=]{32,}['\"]",
        # Database connection strings
        r"jdbc:.*:@.*:\d+:.*",  # JDBC connection string
        r"mongodb(\+srv)?://[^/\s]+:[^/\s]+@[^/\s]+",  # MongoDB connection URI
        r"postgres://[^/\s]+:[^/\s]+@[^/\s]+",  # PostgreSQL connection URI
        # Private keys
        r"-----BEGIN (?:RSA )?PRIVATE KEY-----",
        # Passwords - case insensitive
        r"password.*['\"][^'\"\s]{6,}['\"]",
        r"passwd.*['\"][^'\"\s]{6,}['\"]",
        r"pwd.*['\"][^'\"\s]{6,}['\"]",
        # Generic secret/token patterns - more flexible
        r"secret.*['\"][^'\"]{8,}['\"]",
        r"token.*['\"][^'\"]{15,}['\"]",
    ]

    def __init__(self):
        """Initialize security checker"""
        self.suspicious_file_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SUSPICIOUS_FILE_PATTERNS]
        self.suspicious_content_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SUSPICIOUS_CONTENT_PATTERNS]
        self.checked_paths: Set[str] = set()

    def check_file(self, file_path: Path, content: str) -> List[str]:
        """Check security of a single file

        Args:
            file_path: Path object representing the file path
            content: File content

        Returns:
            List of suspicious reasons
        """
        str_path = str(file_path)
        if str_path in self.checked_paths:
            return []

        self.checked_paths.add(str_path)
        messages: List[str] = []

        # Check file name
        for pattern in self.suspicious_file_patterns:
            if pattern.match(file_path.name):
                messages.append(f"Suspicious file name pattern: {file_path.name}")
                break

        # Check file content
        for pattern in self.suspicious_content_patterns:
            matches = pattern.finditer(content)
            for match in matches:
                matched_text = match.group()
                # Truncate matched text to avoid displaying sensitive information
                truncated_text = matched_text[:20] + "..." if len(matched_text) > 20 else matched_text
                messages.append(f"Suspicious content pattern: {truncated_text}")

        return messages

    def check_file_size(self, file_path: Path, max_size_mb: float = 10.0) -> List[str]:
        """Check file size

        Args:
            file_path: Path object representing the file path
            max_size_mb: Maximum allowed size in megabytes

        Returns:
            List of warning messages
        """
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > max_size_mb:
                return [f"File size exceeds {max_size_mb}MB (current size: {size_mb:.2f}MB)"]
        except Exception as e:
            logger.warn(f"Error checking file size: {e}")

        return []

    def check_files_with_secretlint(self, file_path: Path) -> List[str]:
        secrets = SecretsCollection()
        with default_settings():
            secrets.scan_file(filename=str(file_path.absolute()))

            results = []
            for secret in secrets:
                results.append(f"Secret detected: {secret[1].type}")
            return results


def check_files(root_dir: str | Path, file_paths: List[str], file_contents: Dict[str, str]) -> List[SuspiciousFileResult]:
    """Check security of multiple files

    Args:
        root_dir: Root directory path
        file_paths: List of file paths to check
        file_contents: Dictionary mapping file paths to their contents

    Returns:
        List of suspicious file results
    """
    checker = SecurityChecker()
    results: List[SuspiciousFileResult] = []
    root_path = Path(root_dir)

    for file_path in file_paths:
        # Convert to Path object for path operations
        full_path = root_path / file_path
        content = file_contents.get(file_path, "")

        messages = []
        if full_path.exists():
            messages.extend(checker.check_file(full_path, content))
            messages.extend(checker.check_file_size(full_path))
            messages.extend(checker.check_files_with_secretlint(full_path))
        if messages:
            # Keep using relative path string in results
            results.append(SuspiciousFileResult(file_path=file_path, messages=messages))

    return results
