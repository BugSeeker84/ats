"""Optional S3-compatible object storage (Supabase Storage by default).

The Render container disk is ephemeral — it's wiped on every redeploy, restart, and
free-tier spin-down. When the S3_* env vars are set, generated files and the
applications.csv index are mirrored to a bucket so they survive. When unset, the app
falls back to local-only storage (unchanged behavior).

Works with any S3-compatible endpoint (Supabase, Cloudflare R2, AWS S3, …) via boto3.
"""
import mimetypes
import os
from functools import lru_cache
from pathlib import Path

_ENDPOINT = os.getenv("S3_ENDPOINT_URL", "").strip()
_BUCKET = os.getenv("S3_BUCKET", "").strip()
_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_ID", "").strip()
_SECRET_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "").strip()
_REGION = os.getenv("S3_REGION", "us-east-1").strip() or "us-east-1"
_PREFIX = os.getenv("S3_PREFIX", "").strip().strip("/")


def enabled() -> bool:
    """True only when every credential is present — otherwise we stay local-only."""
    return bool(_ENDPOINT and _BUCKET and _ACCESS_KEY and _SECRET_KEY)


@lru_cache(maxsize=1)
def _client():
    import boto3
    from botocore.config import Config

    # Path-style addressing + SigV4 is what Supabase/R2 expect for custom endpoints.
    return boto3.client(
        "s3",
        endpoint_url=_ENDPOINT,
        aws_access_key_id=_ACCESS_KEY,
        aws_secret_access_key=_SECRET_KEY,
        region_name=_REGION,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def _key(*parts: str) -> str:
    segs = ([_PREFIX] if _PREFIX else []) + [p.strip("/") for p in parts if p]
    return "/".join(segs)


def upload_file(local_path: Path, *key_parts: str) -> None:
    ctype = mimetypes.guess_type(str(local_path))[0] or "application/octet-stream"
    _client().upload_file(
        str(local_path), _BUCKET, _key(*key_parts), ExtraArgs={"ContentType": ctype}
    )


def download_bytes(*key_parts: str) -> bytes | None:
    """Return the object's bytes, or None if it doesn't exist."""
    from botocore.exceptions import ClientError

    try:
        resp = _client().get_object(Bucket=_BUCKET, Key=_key(*key_parts))
        return resp["Body"].read()
    except ClientError:
        return None


def read_text(*key_parts: str) -> str | None:
    data = download_bytes(*key_parts)
    return data.decode("utf-8-sig") if data is not None else None


def write_text(text: str, *key_parts: str) -> None:
    _client().put_object(
        Bucket=_BUCKET,
        Key=_key(*key_parts),
        Body=text.encode("utf-8-sig"),
        ContentType="text/csv; charset=utf-8",
    )
