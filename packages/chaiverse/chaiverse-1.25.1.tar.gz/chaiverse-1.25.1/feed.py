from datetime import datetime

from pydantic import BaseModel, validator
from typing import List

from chaiverse.config import FEED_ENDPOINT, USER_FEED_ENDPOINT
from chaiverse.http_client import SubmitterClient
from chaiverse.lib.now import utcnow


class FeedEntry(BaseModel):
    event_type: str
    timestamp: str
    resource_id: str
    message: str
    user: dict

    @validator("timestamp", pre=True)
    def convert_timestamp(cls, timestamp):
        if isinstance(timestamp, datetime):
            timestamp = int(timestamp.timestamp())
        return str(timestamp)


class Feed(BaseModel):
    entries: List[FeedEntry]


def get_feed(limit, end_time=None, username=None):
    if end_time is None:
        end_time = int(utcnow().timestamp())
    params = {"end_time": end_time, "limit": limit}
    if username:
        params.update({"username": username})
    client = SubmitterClient()
    feed = client.get(endpoint=FEED_ENDPOINT, params=params)
    feed = Feed(entries=feed)
    return feed
