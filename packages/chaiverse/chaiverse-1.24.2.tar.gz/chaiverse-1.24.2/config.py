import os
from pathlib import Path

BASE_SUBMITTER_URL = "http://guanaco-submitter.guanaco-backend.k2.chaiverse.com"
BASE_TRAINING_URL = "http://guanaco-training-service.guanaco-backend.k.chaiverse.com"
BASE_FEEDBACK_URL = "https://guanaco-feedback.chai-research.com"
BASE_AUTH_URL = "https://auth.chaiverse.com"

LATEST_LEADERBOARD_ENDPOINT = "/latest_leaderboard"
LEADERBOARDS_ENDPOINT = "/leaderboards"
LEADERBOARD_AUTO_DEACTIVATE = '/auto_deactivate'
LEADERBOARD_ENDPOINT = "/leaderboard"
CHAT_ENDPOINT = "/models/{submission_id}/chat"
REWARD_MODEL_SCORES_ENDPOINT = "/endpoints/{reward_model_endpoint_id}/score"
FEEDBACK_SUMMARY_ENDPOINT = "/feedback"
FEEDBACK_ENDPOINT = "/feedback/{submission_id}"

LEADERBOARD_API_ENDPOINT = "/api/leaderboard"

SUBMISSION_ENDPOINT = "/models/submit"
FUNCTION_SUBMISSION_ENDPOINT = "/models/submit_function"
BLEND_SUBMISSION_ENDPOINT = "/models/submit_blend"
REWARD_BLEND_SUBMISSION_ENDPOINT = "/models/submit_reward_blend"
ROUTED_BLEND_SUBMISSION_ENDPOINT = "/models/submit_routed_blend"
ALL_SUBMISSION_STATUS_ENDPOINT = "/models/"
SEARCH_SUBMISSIONS_ENDPOINT = "/models/search"
INFO_ENDPOINT = "/models/{submission_id}"
DEACTIVATE_ENDPOINT = "/models/{submission_id}/deactivate"
REDEPLOY_ENDPOINT = "/models/{submission_id}/redeploy"
EVALUATE_ENDPOINT = "/models/{submission_id}/evaluate"
TEARDOWN_ENDPOINT = "/models/{submission_id}/teardown"
FEED_ENDPOINT = "/feed"
USER_FEED_ENDPOINT = "/users/{username}/feed"

TRAINER_ENDPOINT = "/trainers"
TRAINER_INFO_ENDPOINT = "/trainers/{trainer_id}"

DEFAULT_BEST_OF = 8
DEFAULT_MAX_INPUT_TOKENS = 1024
DEFAULT_MAX_OUTPUT_TOKENS = 64

AUTO_DEACTIVATION_MIN_NUM_BATTLES = 5000
AUTO_DEACTIVATION_MAX_ELO_RATING = 1000
AUTO_DEACTIVATION_MIN_RANK = 1

LEADERBOARD_STABLE_ELO_REQUIRED_BATTLES = AUTO_DEACTIVATION_MIN_NUM_BATTLES

ELO_REQUIRED_BATTLES = 1000

ELO_BASE_SUBMISSION_ID = 'mistralai-mixtral-8x7b-_3473_v11'
ELO_BASE_RATING = 1114

DEVELOPER_UID = "chai_backend_admin"
E2E_DEVELOPER_UID = "end_to_end_test"

REPO_ROOT = Path(__file__).absolute().parent.parent.parent
TEST_RESOURCES_DIR = os.path.join(REPO_ROOT, "tests", "test_chaiverse", "resources")
UNIT_TEST_MODEL_DIR = os.path.join(TEST_RESOURCES_DIR, "llama2-0b-unit-test")

DEFAULT_CLUSTER_NAME = "kchai-coreweave-us-east-04"


# TODO: Implement user roles in guanaco_auth to avoid this
INTERNAL_USERS = [
    "chai_backend_admin",
    "end_to_end_test",
    "chaiverse_console_tests",
    "Meliodia",
    "alexdaoud",
    "zonemercy",
    "chai_tester",
    "albert_chai",
    "chaiwill",
    "azuruce",
    "robert_irvine",
    "chaiversetests",
    "valentin",
    "Jellywibble",
    "valentin87",
    "rirv938",
    "ebony59",
    "jxlu90",
    "NischayDnk",
    "dtnewman",
    "richhx",
    "bogoconic1",
]


def get_elo_base_submission_id():
    return ELO_BASE_SUBMISSION_ID


def get_elo_base_rating():
    return ELO_BASE_RATING
