# In 3.8, pytest/mock will have this behavior:
# When running `pytest guanaco_model_service/schema/test_db_leaderboard_schema.py`,
#   chaiverse.schema has competition_schema attribute
# when running `pytest -k test_db_leaderboard_schema`,
#   chaiverse.schema doesn't have competition_schema attribute
# Basically namespace package is wrongly handled by pytest when running from top level
# This fix is import them explicitly
from chaiverse.schemas import (
    date_range_schema,
    leaderboard_row_schema,
    leaderboard_schema,
    preference_summary_schema,
)

from chaiverse.schemas.date_range_schema import *
from chaiverse.schemas.leaderboard_row_schema import *
from chaiverse.schemas.leaderboard_schema import *
from chaiverse.schemas.preference_summary_schema import *
