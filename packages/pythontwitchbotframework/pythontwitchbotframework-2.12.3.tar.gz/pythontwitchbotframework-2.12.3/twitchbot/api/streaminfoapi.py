from datetime import datetime
from traceback import format_exc

from .baseapi import Api
from .. import util
from ..translations import translate


class StreamInfoApi(Api):
    def __init__(self, client_id: str, user: str):
        super().__init__(client_id, user)

        self.viewer_count: int = 0
        self.title: str = ''
        self.game_id: int = 0
        self.started_at: datetime = datetime.min
        self.user_id: int = 0
        self.tag_ids: frozenset = frozenset()

    async def update(self, log=False):
        """
        requests the updated stream info from twitch, called every X seconds (default 60)

        calls `self.on_successful_update` when it updates without errors

        calls `self.on_failed_update` when the update fails, (usually due to key errors)

        :param log: should errors be logged?
        """
        try:
            data = await util.get_stream_data(self.user)
            self.viewer_count = data.get('viewer_count', 0)
            self.title = data.get('title', '')
            self.game_id = data.get('game_id', 0)
            # self.community_ids = frozenset(data['community_ids'])
            #                                                      2018-05-17T16:47:46Z
            self.started_at = datetime.strptime(data['started_at'], '%Y-%m-%dT%H:%M:%SZ') if 'started_at' in data else datetime.min
            self.user_id = data.get('user_id', 0)
            self.tag_ids = frozenset(data.get('tag_ids', {}))

            await self.on_successful_update()
        except Exception as e:
            if log:
                print(translate('stream_info_api_error', user=self.user, error=str(e), error_type=str(type(e)), formatted_exception=format_exc()))

            await self.on_failed_update()
