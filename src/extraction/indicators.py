
from __future__ import annotations
import re
import phonenumbers
import tldextract
from typing import Dict, List, Tuple, Iterable

# Regex patterns
URL_RE = re.compile(r"\bhttps?://[\w\-\.\%\?\#\/=\&\+\:]+", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.|$)){4}\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
DOMAIN_RE = re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b")
GA_RE = re.compile(r"\b(?:UA-\d{4,10}-\d{1,4}|G-[-A-Z0-9]{8,12})\b")
ADSENSE_RE = re.compile(r"\bpub-\d{10,20}\b")

# Social handles / URLs
SOCIAL_PATTERNS = {
    'twitter': re.compile(r"\b(?:https?://)?(?:www\.)?twitter\.com/([A-Za-z0-9_]{1,15})\b", re.I),
    'x': re.compile(r"\b(?:https?://)?(?:www\.)?x\.com/([A-Za-z0-9_]{1,15})\b", re.I),
    'facebook': re.compile(r"\b(?:https?://)?(?:www\.)?facebook\.com/([A-Za-z0-9\._-]+)\b", re.I),
    'instagram': re.compile(r"\b(?:https?://)?(?:www\.)?instagram\.com/([A-Za-z0-9\._-]+)\b", re.I),
    'youtube': re.compile(r"\b(?:https?://)?(?:www\.)?youtube\.com/(?:c/|channel/|@)?([A-Za-z0-9\._-]+)\b", re.I),
    'linkedin': re.compile(r"\b(?:https?://)?(?:[\w\.]+\.)?linkedin\.com/(?:in|company)/([A-Za-z0-9\-_%]+)\b", re.I),
    'tiktok': re.compile(r"\b(?:https?://)?(?:www\.)?tiktok\.com/@([A-Za-z0-9\._-]+)\b", re.I),
    'telegram': re.compile(r"\b(?:https?://)?t\.me/([A-Za-z0-9_]+)/?\b", re.I),
    'reddit': re.compile(r"\b(?:https?://)?(?:www\.)?reddit\.com/(?:u|user)/([A-Za-z0-9_\-]+)\b", re.I),
    'vk': re.compile(r"\b(?:https?://)?vk\.com/([A-Za-z0-9_\.-]+)\b", re.I),
    'truthsocial': re.compile(r"\b(?:https?://)?truthsocial\.com/@([A-Za-z0-9_\.-]+)\b", re.I),
    'parler': re.compile(r"\b(?:https?://)?parler\.com/profile/([A-Za-z0-9_\.-]+)\b", re.I)
}


def iter_phone_numbers(text: str) -> Iterable[str]:
    for m in phonenumbers.PhoneNumberMatcher(text, "US"):
        yield phonenumbers.format_number(m.number, phonenumbers.PhoneNumberFormat.E164)
    # Also try FR, DE to improve recall for docs
    for region in ["FR", "DE", "RU", "GB"]:
        for m in phonenumbers.PhoneNumberMatcher(text, region):
            yield phonenumbers.format_number(m.number, phonenumbers.PhoneNumberFormat.E164)


def normalize_domain(s: str) -> str:
    ext = tldextract.extract(s.lower())
    if not ext.domain:
        return s.lower()
    return ".".join([p for p in [ext.domain, ext.suffix] if p])


def extract_indicators(text: str) -> Dict[str, List[Tuple[str, float]]]:
    out: Dict[str, List[Tuple[str, float]]] = {
        'url': [], 'ip': [], 'email': [], 'domain': [], 'phone': [], 'social': [], 'tracker': []
    }

    for m in URL_RE.findall(text):
        out['url'].append((m, 0.95))
    for m in IP_RE.findall(text):
        out['ip'].append((m, 0.9))
    for m in EMAIL_RE.findall(text):
        out['email'].append((m, 0.95))
    # Domains: filter out those already part of URLs/emails
    url_domains = set()
    for u, _ in out['url']:
        url_domains.add(normalize_domain(u))
    for m in DOMAIN_RE.findall(text):
        dm = m.lower()
        if normalize_domain(dm) not in url_domains:
            out['domain'].append((dm, 0.8))

    for ph in set(iter_phone_numbers(text)):
        out['phone'].append((ph, 0.7))

    for name, pat in SOCIAL_PATTERNS.items():
        for m in pat.findall(text):
            handle = f"{name}:{m}"
            out['social'].append((handle, 0.9))

    for m in GA_RE.findall(text):
        out['tracker'].append((f"ga:{m}", 0.9))
    for m in ADSENSE_RE.findall(text):
        out['tracker'].append((f"adsense:{m}", 0.85))

    return out
