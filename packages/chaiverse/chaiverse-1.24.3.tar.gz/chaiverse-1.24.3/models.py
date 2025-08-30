from chaiverse.config import REWARD_MODEL_SCORES_ENDPOINT
from chaiverse.http_client import SubmitterClient
from chaiverse.cli_utils.login_cli import auto_authenticate


@auto_authenticate
def get_reward_model_scores(conversation_state, responses, endpoint_id, developer_key=None):
    http_client = SubmitterClient(developer_key=developer_key)
    response = http_client.post(
        endpoint=REWARD_MODEL_SCORES_ENDPOINT.format(reward_model_endpoint_id=endpoint_id),
        json={
            "conversation_state": conversation_state.dict(),
            "responses": responses
        },
    )
    return response