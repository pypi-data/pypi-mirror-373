from datetime import datetime
import json
from math import inf
from typing import List, Optional, Union, Dict

import numpy as np
from pydantic import BaseModel, Extra, Field, model_validator
from typing_extensions import Literal

from chaiverse import config
from chaiverse.lib.now import utcnow
from chaiverse.lib.pydantic_tools import get_fields_in_schema, UnionParser
from chaiverse.lib.date_tools import convert_to_us_pacific_date


class BaseLeaderboardRow(BaseModel, extra=Extra.allow):
    developer_uid: str
    submission_id: str
    model_name: Optional[str] = ""
    model_group: Optional[str] = ""
    status: str
    timestamp: datetime = Field(default_factory=utcnow)

    # preference metrics
    num_battles: int = 0
    num_wins: int = 0
    celo_rating: Optional[float] = None

    # family friendly scores
    family_friendly_score: float = 0
    family_friendly_standard_error: float | None = None

    @model_validator(mode="after")
    def validate_model_group(self):
        if not self.model_group:
            model_repo = getattr(self, "model_repo", "")
            self.model_group = model_repo[:24]
        return self

    @property
    def display_name(self):
        name = self.model_name if self.model_name else self.submission_id
        return name

    @property
    def win_ratio(self):
        return self.num_wins / self.num_battles if self.num_battles > 0 else None

    @property
    def us_pacific_date(self):
        us_pacific_date = convert_to_us_pacific_date(self.timestamp).date()
        return us_pacific_date

    @property
    def ranking_group(self):
        ''' this is a string that labels whether this type of model will be ranked in single or blended group '''
        return None

    @property
    def is_internal_developer(self):
        is_internal = self.developer_uid in config.INTERNAL_USERS
        return is_internal

    @property
    def ineligible_reason(self) -> Optional[str]:
        return None

    def can_auto_deactivate(self):
        is_deployed = self.status == 'deployed'
        has_enough_battles = self.num_battles >= config.AUTO_DEACTIVATION_MIN_NUM_BATTLES
        return is_deployed and has_enough_battles

    def all_fields_dict(self):
        fields = get_fields_in_schema(self.__class__)
        fields_dict = {key: getattr(self, key) for key in fields}
        return fields_dict

    def base_fields_dict(self):
        fields = BaseLeaderboardRow.__fields__.keys()
        fields_dict = {key: getattr(self, key) for key in fields}
        return fields_dict

    ## pydantic 2.x implements model_dump. Existing dict() in pydantic 1.x doesn't serialize recursively
    #def model_dump(self):
    #    return json.loads(self.json())


class SingleGroupLeaderboardRow(BaseLeaderboardRow):
    ''' minimum implementation to show a model in single-model leaderboard '''
    submission_type: str = Field(default='single_model')

    @property
    def ranking_group(self):
        return 'single'


class BlendedGroupLeaderboardRow(BaseLeaderboardRow):
    ''' minimum implementation for a model in blended leaderboard '''
    submission_type: Literal['blended_model'] = Field(default='blended_model')

    @property
    def ranking_group(self):
        return 'blended'


class LatencyRecord(BaseModel):
    batch_size: int
    throughput: float  # throughput for all the samples provided, subject to window dressing error
    latency_mean: float  # a better approximate of throughput without window dressing error
    latency_p50: float  # a better typical latency estimate removing outliners
    latency_p90: float  # proxy for worst case latency estiamte


class BasicLeaderboardRow(SingleGroupLeaderboardRow):
    submission_type: Literal['basic'] = Field(default='basic')
    model_repo: str
    model_architecture: Optional[str] = ""
    model_num_parameters: float | None = None
    best_of: int = 1
    max_input_tokens: int
    max_output_tokens: Optional[int] = 64

    # throughput and cost metrics
    latencies: Optional[List[LatencyRecord]] = Field(default=None)
    gpu_counts: Optional[Dict[str, int]] = Field(default=None)

    @property
    def language_model(self):
        return self.model_repo

    @property
    def model_size(self):
        size_gb = round(self.model_num_parameters / 1e9) if self.model_num_parameters else None
        size_gb = f'{size_gb}B'
        return size_gb

    @property
    def ineligible_reason(self) -> Optional[str]:
        reason = None
        if self.status != 'deployed' and self.num_battles < config.LEADERBOARD_STABLE_ELO_REQUIRED_BATTLES:
            reason = f'num_battles<{config.LEADERBOARD_STABLE_ELO_REQUIRED_BATTLES}'
        if self.max_output_tokens != config.DEFAULT_MAX_OUTPUT_TOKENS and self.max_output_tokens != None:
            reason = f'max_output_tokens!={config.DEFAULT_MAX_OUTPUT_TOKENS}'
        if self.status not in ['inactive', 'deployed', 'torndown']:
            reason = 'model is not deployable'
        if self.developer_uid == config.E2E_DEVELOPER_UID:
            reason = 'model is only for e2e test'
        return reason

    @property
    def throughput_3p7s(self):
        return self.throughput(3.7)

    def throughput(self, target_latency):
        return _get_throughput(target_latency, self.latencies)


def _get_throughput(target_latency, records: Optional[List[LatencyRecord]]):
    throughput = None
    if records:
        latency_means = [record.latency_mean for record in records]
        batch_sizes = [record.batch_size for record in records]
        if min(latency_means) <= target_latency <= max(latency_means):
            target_batch_size = np.interp(target_latency, latency_means, batch_sizes)
            throughput = target_batch_size / target_latency
            throughput = round(throughput, 2)
            throughput = _convert_nan_to_none(throughput)
    return throughput


def _convert_nan_to_none(value):
    value = None if np.isnan(value) else value
    return value


class FunctionLeaderboardRow(SingleGroupLeaderboardRow):
    submission_type: Literal['function'] = Field(default='function')


class BlendLeaderboardRow(BlendedGroupLeaderboardRow):
    submission_type: Literal['blend'] = Field(default='blend')
    submissions: List[str]

    @property
    def language_model(self):
        return ','.join(self.submissions)

    @property
    def model_size(self):
        return 'n/a'


class TaggedSubmissionID(BaseModel):
    submission_id: str
    tags: Optional[List[str]] = None


LeaderboardRow = Union[
    BasicLeaderboardRow,
    FunctionLeaderboardRow,
    BlendLeaderboardRow,
    SingleGroupLeaderboardRow,  # simplest implementation for a single model leaderboard row
    BlendedGroupLeaderboardRow,  # simplest implementation for a blended model leaderboard row
]
