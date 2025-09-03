from contextlib import contextmanager
import re


REGEXES = [
    # AWS Secret Key Detector
    re.compile(r'[A-Za-z0-9]{43}'),
    # HuggingFace Token Detector
    re.compile(r'hf_[A-Za-z0-9_]{34}'),
    # Chaiverse Token Detector
    re.compile(r'CR_[A-Za-z0-9_]{32}'),
    # Github Token Detector
    re.compile(r'(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36}'),
    # Gitlab Token Detector
    re.compile(r'(?:gldt|glpat|glrt|glptt|glft|gmimt|glagent)-[A-Za-z0-9]{3}-[A-Za-z]{10}_[a-z]{5}'),
    # Discord bot Token Detector
    re.compile(r'[MNO][a-zA-Z\d_-]{23,25}\.[a-zA-Z\d_-]{6}\.[a-zA-Z\d_-]{27}'),
]


def scrub_secrets(string: str, redaction=""):
    try:
        decoded_string = string.decode("utf-8") if isinstance(string, bytes) else string
        secrets = detect_secrets(decoded_string)
        for secret in secrets:
            decoded_string = decoded_string.replace(secret, redaction)
        string = str.encode(decoded_string) if isinstance(string, bytes) else decoded_string
    except UnicodeDecodeError:
        pass
    return string


def detect_secrets(string: str):
    regex_matches = [regex.search(str(string)) for regex in REGEXES]
    secrets = [match.group() for match in regex_matches if match]
    return secrets
