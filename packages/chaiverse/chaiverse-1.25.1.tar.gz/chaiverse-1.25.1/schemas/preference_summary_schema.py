from datetime import datetime
import logging
from typing import Dict

from pydantic import BaseModel, Field, Extra, root_validator

from chaiverse.config import get_elo_base_rating, get_elo_base_submission_id, ELO_REQUIRED_BATTLES
from chaiverse.lib.elo import get_elo_rating, get_mle_elo_scores
from chaiverse.lib.now import utcnow


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PreferenceSummary(BaseModel):
    '''
    wins_dict[player_a,player_b] is a sparse matrix of win count for player a vs player b
    elo_scores[player] must include all players, and the value is last known best elo score
    '''
    wins_dict: Dict[str, Dict[str, int]] = Field(default={})
    elo_scores: Dict[str, float] = Field(default={})

    def recalculate_elo_scores(self):
        logger.info('Recalculating elo scores')
        self.elo_scores = get_mle_elo_scores(self.elo_scores, self.wins_dict)
        logger.info('Recalculated elo scores')

    @property
    def submission_ids(self):
        elo_scores = self.elo_scores or {}
        return elo_scores.keys()

    def wins(self, a_id: str, b_id: str):
        wins = self.wins_dict.get(a_id, {}).get(b_id, 0)
        return wins

    def battles(self, a_id: str, b_id: str):
        return self.wins(a_id, b_id) + self.wins(b_id, a_id)

    def win_ratio(self, a_id: str, b_id: str):
        battles = self.battles(a_id, b_id)
        return self.wins(a_id, b_id) / battles if battles > 0 else float('nan')

    def submission_num_wins(self, submission_id: str):
        submission_total = sum(self.wins_dict.get(submission_id, {}).values())
        return submission_total

    def submission_num_battles(self, submission_id: str):
        submission_total = 0
        for opponent_id in self.submission_ids:
            submission_total += self.battles(submission_id, opponent_id)
        return submission_total

    def submission_win_ratio(self, submission_id: str):
        battles = self.submission_num_battles(submission_id)
        return self.submission_num_wins(submission_id) / battles if battles > 0 else None

    def submission_elo_score(self, submission_id: str, default_score: float = None):
        elo_scores = self.elo_scores or {}
        elo_score = elo_scores.get(submission_id, default_score)
        return elo_score

    def submission_elo_rating(self, submission_id, elo_base_id: str = None, elo_base_rating: float = None):
        elo_base_id = elo_base_id or get_elo_base_submission_id()
        elo_base_rating = elo_base_rating or get_elo_base_rating()

        elo_base_score = self.submission_elo_score(elo_base_id)
        elo_score = self.submission_elo_score(submission_id)
        elo_rating = get_elo_rating(elo_score, elo_base_score, elo_base_rating) if elo_score is not None else None
        return elo_rating

    def submission_metrics(self, submission_id: str, elo_base_id: str = None, elo_base_rating: float = None, is_blend: bool = False):
        num_battles = self.submission_num_battles(submission_id)
        num_wins = self.submission_num_wins(submission_id)
        win_ratio = self.submission_win_ratio(submission_id)

        # blends do not have an elo rating
        if num_battles >= ELO_REQUIRED_BATTLES and not is_blend:
            celo_rating = self.submission_elo_rating(submission_id, elo_base_id=elo_base_id, elo_base_rating=elo_base_rating)
        else:
            celo_rating = None

        metrics = dict(num_battles=num_battles, num_wins=num_wins, win_ratio=win_ratio, celo_rating=celo_rating)
        return metrics

    def get_all_metrics_dict(self, elo_base_id: str = None, elo_base_rating: float = None, is_blend: bool = False):
        metrics = {
            submission_id: self.submission_metrics(submission_id, elo_base_id=elo_base_id, elo_base_rating=elo_base_rating, is_blend=is_blend)
            for submission_id in self.submission_ids
        }
        return metrics


class PreferenceSummaries(BaseModel, extra=Extra.allow):
    summaries: Dict[str, PreferenceSummary] = Field(default={})
    created_at: datetime = Field(default_factory=utcnow)
