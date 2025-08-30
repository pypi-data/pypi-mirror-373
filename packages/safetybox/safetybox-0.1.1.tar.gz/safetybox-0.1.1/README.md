# safetybox

Secutils 是一个专注于防御与取证的 Python 工具包，提供密码学辅助、IOC 提取、日志匿名化、PCAP 被动统计与插件扩展点。

**安装**（基础）：
```bash
pip install .
# 或者安装带 pcap 支持
pip install .[pcap]
```

**示例**
```bash
safetybox gen-pass --length 20
safetybox check-pass "correct horse battery staple"
safetybox extract-iocs -f access.log
safetybox pcap-summary traffic.pcap --max-packets 2000
```
