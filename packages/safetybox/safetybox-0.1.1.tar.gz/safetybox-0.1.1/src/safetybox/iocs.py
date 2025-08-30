"""IOC 提取与处理（IP/域名/邮箱/哈希/URL）"""
import re
from typing import Dict, List

IPV4_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(\.[\w-]+)+\b")
DOMAIN_RE = re.compile(r"\b((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,})\b", re.IGNORECASE)
HASH_RE = re.compile(r"\b([a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64})\b")
URL_RE = re.compile(r"\bhttps?://[\w\-._~:/?#[\]@!$&'()*+,;=%]+", re.IGNORECASE)

def extract_iocs(text: str) -> Dict[str, List[str]]:
    ips = sorted({m.group(0) for m in IPV4_RE.finditer(text)})
    emails = sorted({m.group(0) for m in EMAIL_RE.finditer(text)})
    domains = sorted({m.group(0) for m in DOMAIN_RE.finditer(text)})
    hashes = sorted({m.group(0) for m in HASH_RE.finditer(text)})
    urls = sorted({m.group(0) for m in URL_RE.finditer(text)})
    return {"ips": ips, "emails": emails, "domains": domains, "hashes": hashes, "urls": urls}
