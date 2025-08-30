"""日志解析与匿名化"""
import re
from typing import Optional, Dict

IPV4_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
COMMON_LOG_RE = re.compile(r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<req>[^\"]*)" (?P<status>\d{3}) (?P<size>\S+)(?: "(?P<ref>[^\"]*)" "(?P<ua>[^\"]*)")?')

def anonymize_ipv4(ip: str, keep_last_octet: bool = False) -> str:
    parts = ip.split('.')
    if len(parts) != 4:
        return ip
    if keep_last_octet:
        return '.'.join([parts[0], parts[1], parts[2], '0'])
    return '.'.join([parts[0], '0', '0', '0'])

def anonymize_text(text: str, keep_last_octet: bool = False) -> str:
    def repl(m):
        return anonymize_ipv4(m.group(0), keep_last_octet=keep_last_octet)
    return IPV4_RE.sub(repl, text)

def parse_common_log_line(line: str) -> Optional[Dict[str, str]]:
    m = COMMON_LOG_RE.search(line)
    if not m:
        return None
    return m.groupdict()
