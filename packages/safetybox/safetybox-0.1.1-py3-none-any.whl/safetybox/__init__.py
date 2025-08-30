"""safetybox — defensive security helpers (package root)"""
from ._version import __version__
from .passwords import generate_password, analyze_password, shannon_entropy
from .crypto import pbkdf2_derive, gen_salt, hash_file, hmac_hex
from .iocs import extract_iocs
from .logs import anonymize_text, parse_common_log_line
from .pcap import pcap_summary
from .plugin import load_plugins, register_plugin

__all__ = [
    "__version__",
    "generate_password", "analyze_password", "shannon_entropy",
    "pbkdf2_derive", "gen_salt", "hash_file", "hmac_hex",
    "extract_iocs", "anonymize_text", "parse_common_log_line",
    "pcap_summary", "load_plugins", "register_plugin",
]
