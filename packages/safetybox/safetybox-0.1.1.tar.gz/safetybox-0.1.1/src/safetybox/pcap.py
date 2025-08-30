"""被动 PCAP 读取和简单统计（依赖 scapy，可选）

注意：只读统计，不发包。
"""
from typing import Dict, Any

try:
    from scapy.all import rdpcap, PcapReader
    _HAS_SCAPY = True
except Exception:
    _HAS_SCAPY = False

def pcap_summary(path: str, max_packets: int = 0) -> Dict[str, Any]:
    if not _HAS_SCAPY:
        raise RuntimeError('scapy 未安装。请 install with `pip install safetybox[pcap]` 或者 `pip install scapy`')
    counts = {"packets": 0, "ip_versions": {}, "protocols": {}, "top_talkers": {}}
    seen_ips = {}
    reader = PcapReader(path)
    try:
        for i, pkt in enumerate(reader):
            if max_packets and i >= max_packets:
                break
            counts['packets'] += 1
            if pkt.haslayer('IP'):
                v = 'ipv4'
                src = pkt['IP'].src
                dst = pkt['IP'].dst
            elif pkt.haslayer('IPv6'):
                v = 'ipv6'
                src = pkt['IPv6'].src
                dst = pkt['IPv6'].dst
            else:
                v = 'other'
                src = dst = None
            counts['ip_versions'][v] = counts['ip_versions'].get(v, 0) + 1
            proto = pkt.payload.name if hasattr(pkt, 'payload') else 'unknown'
            counts['protocols'][proto] = counts['protocols'].get(proto, 0) + 1
            if src:
                seen_ips[src] = seen_ips.get(src, 0) + 1
            if dst:
                seen_ips[dst] = seen_ips.get(dst, 0) + 1
    finally:
        reader.close()
    top = sorted(seen_ips.items(), key=lambda x: x[1], reverse=True)[:10]
    counts['top_talkers'] = top
    return counts
