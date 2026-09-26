"""Deterministic normalization utilities (GOAL.md §22)."""

import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# Common tracking parameters stripped during canonicalization.
TRACKING_PARAMS = {
    "fbclid",
    "gclid",
    "ref",
    "ref_src",
    "ref_url",
    "igshid",
    "mc_cid",
    "mc_eid",
    "cmpid",
    "sgm",
}

_WHITESPACE = re.compile(r"\s+")


def normalize_title(title: str) -> str:
    return _WHITESPACE.sub(" ", title).strip().lower()


def canonicalize_url(url: str) -> str:
    try:
        parts = urlparse(url.strip())
    except ValueError:
        return url.strip()
    if not parts.netloc:
        return url.strip()

    host = parts.netloc.lower()
    # Strip leading www.
    if host.startswith("www."):
        host = host[4:]
    # Drop default ports.
    if parts.port in (80, 443):
        host = host.split(":", 1)[0]

    path = parts.path.rstrip("/") or "/"
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in TRACKING_PARAMS and not k.lower().startswith("utm_")
    ]
    return urlunparse((parts.scheme.lower(), host, path, "", urlencode(query), ""))


def content_hash(title: str, canonical_url: str) -> str:
    basis = f"{normalize_title(title)}|{canonical_url}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()
