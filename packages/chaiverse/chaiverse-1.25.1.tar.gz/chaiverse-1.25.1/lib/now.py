from datetime import datetime, timezone


# Freezegun or time_machine can mock current time, but not reliably.
# Freezegun and time_machine won't work in e2e test dependent on authenticated API that requires untempered timestamp.
# This library addressed two problem above.
# The _now is present so only one patch is needed


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def utcnow():
    return _now()


def utctoday():
    return utcnow().date()