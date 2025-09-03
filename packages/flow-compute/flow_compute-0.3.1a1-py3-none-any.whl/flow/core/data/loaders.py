"""Data loaders for different URL schemes."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from flow.core.data.resolver import DataError
from flow.sdk.models import MountSpec

if TYPE_CHECKING:  # avoid runtime circular imports
    from flow.protocols.provider import ProviderProtocol as IProvider  # pragma: no cover
else:
    IProvider = object  # type: ignore


class VolumeLoader:
    """Loads volume:// URLs.

    Handles both names and IDs:
    - volume://training-data -> Look up by name
    - volume://vol_abc123 -> Direct ID

    Performance: Name lookups are cached after first resolution.
    Auto-creation: Missing volumes are created with 100GB default size.

    Examples:
        >>> loader = VolumeLoader()
        >>> spec = loader.resolve("volume://my-data", provider)
        >>> spec.options["volume_id"]
        'vol_abc123'
    """

    def __init__(self):
        # Simple in-memory cache for name->ID mapping
        # Avoids repeated API calls for same volume names
        self._name_cache: dict[str, str] = {}

    def resolve(self, url: str, provider: IProvider) -> MountSpec:
        """Resolve volume URL to mount spec."""
        parsed = urlparse(url)
        volume_ref = parsed.netloc or parsed.path.lstrip("/")

        if not volume_ref:
            raise DataError(
                "Invalid volume URL: missing volume name/ID",
                suggestions=["Use volume://name or volume://vol_id"],
            )

        # Determine if it's an ID or name
        if provider.is_volume_id(volume_ref):
            volume_id = volume_ref
        else:
            volume_id = self._resolve_name(volume_ref, provider)

        return MountSpec(
            source=f"volume://{volume_id}",
            target="",  # Will be set by resolver
            mount_type="volume",
            options={"volume_id": volume_id},
        )

    def _resolve_name(self, name: str, provider: IProvider) -> str:
        """Resolve volume name to ID."""
        # Check cache first (fast path)
        cache_key = f"{provider.__class__.__name__}:{name}"
        if cache_key in self._name_cache:
            return self._name_cache[cache_key]

        # List volumes and find by name
        volumes = provider.list_volumes(limit=1000)
        for vol in volumes:
            # Handle both dict and Volume objects
            vol_name = vol.get("name") if isinstance(vol, dict) else vol.name
            vol_id = vol.get("id") if isinstance(vol, dict) else vol.volume_id

            if vol_name == name:
                self._name_cache[cache_key] = vol_id
                return vol_id

        # Not found - create it
        new_volume = provider.create_volume(size_gb=100, name=name)  # Default size
        volume_id = new_volume.volume_id if hasattr(new_volume, "volume_id") else new_volume["id"]
        self._name_cache[cache_key] = volume_id
        return volume_id


class LocalLoader:
    """Loads local file paths."""

    def resolve(self, url: str, provider: IProvider) -> MountSpec:
        """Resolve local path to mount spec.

        This is primarily used when the URLResolver delegates to us,
        so the path validation has already been done.
        """
        return MountSpec(
            source=url,
            target="",  # Will be set by resolver
            mount_type="bind",
            options={"readonly": True},
        )


class S3Loader:
    """Loads s3:// URLs using s3fs mounting.

    Features:
    - Standard AWS credential resolution (env, file, IAM role)
    - Pre-flight validation of bucket access
    - Read-only mounting by default

    Performance: Bucket validation adds ~100-500ms latency.
    Security: Credentials passed via environment, not command line.

    Examples:
        >>> loader = S3Loader()
        >>> spec = loader.resolve("s3://ml-data/datasets", provider)
        >>> spec.mount_type
        's3fs'
        >>> spec.options["bucket"]
        'ml-data'
    """

    def __init__(self):
        self._credential_resolver = AWSCredentialResolver()

    def resolve(self, url: str, provider: IProvider) -> MountSpec:
        """Resolve S3 URL to mount specification."""
        parsed = urlparse(url)
        bucket = parsed.netloc
        path = parsed.path.lstrip("/")

        if not bucket:
            raise DataError(
                "Invalid S3 URL: missing bucket name", suggestions=["Use format: s3://bucket/path"]
            )

        # Validate bucket exists and we have access
        if not self._validate_access(bucket):
            raise DataError(
                f"Cannot access S3 bucket: {bucket}",
                suggestions=[
                    "Check AWS credentials are configured",
                    "Verify bucket exists and you have access",
                    "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY",
                ],
            )

        return MountSpec(
            source=f"s3://{bucket}/{path}" if path else f"s3://{bucket}",
            target="",  # Set by resolver
            mount_type="s3fs",
            options={"bucket": bucket, "path": path, "readonly": True},
        )

    def _validate_access(self, bucket: str) -> bool:
        """Validate we have access to the S3 bucket."""
        # First check if we have credentials. If none are available locally,
        # skip strict preflight and allow runtime auth (e.g., IAM role on instance).
        creds = self._credential_resolver.get_credentials()
        if not creds:
            # No local credentials; assume runtime will provide access (IAM role or injected env)
            return True

        # Try to access the bucket using boto3
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError

            # Create S3 client with resolved credentials
            if creds.get("session_token"):
                session = boto3.Session(
                    aws_access_key_id=creds["access_key"],
                    aws_secret_access_key=creds["secret_key"],
                    aws_session_token=creds["session_token"],
                )
            else:
                session = boto3.Session(
                    aws_access_key_id=creds["access_key"], aws_secret_access_key=creds["secret_key"]
                )

            s3 = session.client("s3")

            # Try to list the bucket (just 1 object to test access)
            s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
            return True

        except ImportError:
            raise DataError(
                "boto3 is required for S3 support", suggestions=["Install with: pip install boto3"]
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                raise DataError(
                    f"S3 bucket not found: {bucket}",
                    suggestions=[
                        "Check bucket name is correct",
                        "Verify bucket exists in your AWS account",
                        f"Try: aws s3 ls s3://{bucket}",
                    ],
                )
            elif error_code in ("AccessDenied", "Forbidden"):
                raise DataError(
                    f"Access denied to S3 bucket: {bucket}",
                    suggestions=[
                        "Check IAM permissions for your AWS user",
                        "Verify bucket policy allows your access",
                        f"Try: aws s3 ls s3://{bucket}",
                    ],
                )
            return False
        except Exception:
            return False


class AWSCredentialResolver:
    """Resolves AWS credentials from multiple sources."""

    def get_credentials(self) -> dict[str, str] | None:
        """Get AWS credentials following standard resolution order."""
        # 1. Environment variables
        if os.environ.get("AWS_ACCESS_KEY_ID"):
            return {
                "access_key": os.environ["AWS_ACCESS_KEY_ID"],
                "secret_key": os.environ["AWS_SECRET_ACCESS_KEY"],
                "session_token": os.environ.get("AWS_SESSION_TOKEN"),
            }

        # 2. Credentials file
        creds = self._read_credentials_file()
        if creds:
            return creds

        # 3. Instance metadata (IAM role)
        if self._is_ec2_instance():
            return self._get_instance_credentials()

        return None

    def _read_credentials_file(self) -> dict[str, str] | None:
        """Read AWS credentials from ~/.aws/credentials."""
        creds_path = Path.home() / ".aws" / "credentials"
        if not creds_path.exists():
            return None

        try:
            import configparser

            config = configparser.ConfigParser()
            config.read(creds_path)

            # Use default profile
            if "default" in config:
                return {
                    "access_key": config["default"].get("aws_access_key_id"),
                    "secret_key": config["default"].get("aws_secret_access_key"),
                    "session_token": config["default"].get("aws_session_token"),
                }
        except Exception:
            pass

        return None

    def _is_ec2_instance(self) -> bool:
        """Check if running on EC2 instance."""
        # Simple check for EC2 metadata service
        try:
            import urllib.request

            req = urllib.request.Request(
                "http://169.254.169.254/latest/meta-data/",
                headers={"X-aws-ec2-metadata-token-ttl-seconds": "10"},
            )
            with urllib.request.urlopen(req, timeout=1) as response:
                return response.status == 200
        except Exception:
            return False

    def _get_instance_credentials(self) -> dict[str, str] | None:
        """Get credentials from EC2 instance metadata."""
        # This is a simplified version - in production would use boto3's
        # credential provider chain which handles token refresh, etc.
        try:
            import json
            import urllib.request

            # Get IAM role
            req = urllib.request.Request(
                "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
            )
            with urllib.request.urlopen(req, timeout=2) as response:
                role = response.read().decode().strip()

            # Get credentials for role
            req = urllib.request.Request(
                f"http://169.254.169.254/latest/meta-data/iam/security-credentials/{role}"
            )
            with urllib.request.urlopen(req, timeout=2) as response:
                creds = json.loads(response.read())

            return {
                "access_key": creds["AccessKeyId"],
                "secret_key": creds["SecretAccessKey"],
                "session_token": creds["Token"],
            }
        except Exception:
            return None
