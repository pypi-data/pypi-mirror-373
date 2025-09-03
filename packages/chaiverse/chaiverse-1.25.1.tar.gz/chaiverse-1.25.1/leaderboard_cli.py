from chaiverse import config
from chaiverse.http_client import SubmitterClient
from chaiverse.lib import dataframe_tools
from chaiverse.schemas import Leaderboard


def get_leaderboard(realtime: bool=False, developer_key=None) -> Leaderboard:
    submitter_client = SubmitterClient(developer_key)
    leaderboard = submitter_client.get(config.LATEST_LEADERBOARD_ENDPOINT, params=dict(realtime=realtime))
    leaderboard = Leaderboard(**leaderboard)
    return leaderboard


def get_leaderboards() -> Leaderboard:
    submitter_client = SubmitterClient()
    leaderboards = submitter_client.get(config.LEADERBOARDS_ENDPOINT)
    leaderboards = [Leaderboard(**leaderboard) for leaderboard in leaderboards]
    return leaderboards


def display_leaderboard(realtime:bool=False):
    leaderboard = get_leaderboard(realtime=realtime)
    display_df = leaderboard.to_display_df()
    formatted = dataframe_tools.format_dataframe(display_df)
    print(formatted)


def auto_deactivate(dryrun:bool=True, developer_key=None):
    submitter_client = SubmitterClient(developer_key=developer_key)
    result = submitter_client.post(config.LEADERBOARD_AUTO_DEACTIVATE, params=dict(dryrun=dryrun))
    return result
