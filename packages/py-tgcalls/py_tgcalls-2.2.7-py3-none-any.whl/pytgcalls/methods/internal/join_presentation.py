from typing import Union

from ntgcalls import ConnectionMode
from ntgcalls import ConnectionNotFound
from ntgcalls import TelegramServerError

from ...scaffold import Scaffold


class JoinPresentation(Scaffold):
    async def _join_presentation(
        self,
        chat_id: Union[int, str],
        join: bool,
    ):
        connection_mode = await self._binding.get_connection_mode(
            chat_id,
        )
        if connection_mode == ConnectionMode.STREAM:
            if chat_id in self._pending_connections:
                self._pending_connections[chat_id].presentation = join
        elif connection_mode == ConnectionMode.RTC:
            if join:
                if chat_id in self._presentations:
                    return
                for retries in range(4):
                    try:
                        self._wait_connect[
                            chat_id
                        ] = self.loop.create_future()
                        payload = await self._binding.init_presentation(
                            chat_id,
                        )
                        result_params = await self._app.join_presentation(
                            chat_id,
                            payload,
                        )
                        await self._binding.connect(
                            chat_id,
                            result_params,
                            True,
                        )
                        await self._wait_connect[chat_id]
                        self._presentations.add(chat_id)
                        break
                    except TelegramServerError:
                        if retries == 3:
                            raise
                        self._log_retries(retries)
                    finally:
                        self._wait_connect.pop(chat_id, None)
            elif chat_id in self._presentations:
                try:
                    await self._binding.stop_presentation(chat_id)
                    await self._app.leave_presentation(chat_id)
                except ConnectionNotFound:
                    pass
                self._presentations.discard(chat_id)
