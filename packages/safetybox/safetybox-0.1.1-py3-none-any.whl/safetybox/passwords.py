"""密码学与口令工具（防御/评估）"""
from __future__ import annotations
import secrets, string, math, re
from dataclasses import dataclass

COMMON_PASSWORDS = {"123456","password","qwerty","abc123","letmein","111111"}

PRONOUNCEABLE_ONSETS = ["ba","be","bi","bo","bu","da","de","di","do","du","ga","ge","gi","go","gu","la","le","li","lo","lu","ma","me","mi","mo","mu"]
PRONOUNCEABLE_VOWELS = list("aeiou")

def generate_password(length: int = 16, charset: str = "all", pronounceable: bool = False) -> str:
    if pronounceable:
        s = []
        while len("".join(s)) < length:
            s.append(secrets.choice(PRONOUNCEABLE_ONSETS) + secrets.choice(PRONOUNCEABLE_VOWELS))
        return ("".join(s))[:length]
    if charset == 'all':
        pool = string.ascii_letters + string.digits + string.punctuation
    elif charset == 'alnum':
        pool = string.ascii_letters + string.digits
    elif charset == 'hex':
        pool = string.hexdigits.lower()
    else:
        pool = string.ascii_letters + string.digits
    return ''.join(secrets.choice(pool) for _ in range(length))

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    H = 0.0
    L = len(s)
    for c in freq.values():
        p = c / L
        H -= p * math.log2(p)
    return H

@dataclass
class PasswordAnalysis:
    score: int
    entropy_bits: float
    length: int
    suggestions: list
    found_common: bool

def analyze_password(pw: str) -> PasswordAnalysis:
    length = len(pw)
    entropy = shannon_entropy(pw) * length
    score = 0
    suggestions = []
    if length >= 16:
        score += 30
    elif length >= 12:
        score += 20
    elif length >= 8:
        score += 10
    else:
        suggestions.append("长度应至少为 12—16 个字符。")
    classes = 0
    if re.search(r"[a-z]", pw): classes += 1
    if re.search(r"[A-Z]", pw): classes += 1
    if re.search(r"\d", pw): classes += 1
    if re.search(r"[^A-Za-z0-9]", pw): classes += 1
    score += classes * 15
    if entropy >= 80:
        score += 25
    elif entropy >= 50:
        score += 10
    else:
        suggestions.append("密码熵偏低，避免可预测短语或重复模式。")
    found_common = pw.lower() in COMMON_PASSWORDS
    if found_common:
        suggestions.append("检测到常见弱口令，请立即更换。")
    score = max(0, min(100, score))
    return PasswordAnalysis(score=score, entropy_bits=entropy, length=length, suggestions=suggestions, found_common=found_common)
