import asyncio
import json
import logging
import re
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import websockets

from .crud import Database
from .exceptions import InvalidPhoneError, WebSocketNotConnectedError
from .payloads import (
    BaseWebSocketMessage,
    DeleteMessagePayload,
    EditMessagePayload,
    FetchContactsPayload,
    FetchHistoryPayload,
    RequestCodePayload,
    SendCodePayload,
    SendMessagePayload,
    SendMessagePayloadMessage,
    SyncPayload,
)
from .static import AuthType, ChatType, Constants, Opcode
from .types import Channel, Chat, Dialog, Message, User

logger = logging.getLogger(__name__)


class MaxClient:
    """
    Основной клиент для работы с WebSocket API сервиса Max.


    Args:
        phone (str): Номер телефона для авторизации.
        uri (str, optional): URI WebSocket сервера. По умолчанию Constants.WEBSOCKET_URI.value.
        work_dir (str, optional): Рабочая директория для хранения базы данных. По умолчанию ".".
        logger (logging.Logger | None): Пользовательский логгер. Если не передан — используется
            логгер модуля с именем f"{__name__}.MaxClient".

    Raises:
        InvalidPhoneError: Если формат номера телефона неверный.
    """

    def __init__(
        self,
        phone: str,
        uri: str = Constants.WEBSOCKET_URI.value,
        work_dir: str = ".",
        logger: logging.Logger | None = None,
    ) -> None:
        self.uri: str = uri
        self.is_connected: bool = False
        self.phone: str = phone
        self.chats: list[Chat] = []
        self.dialogs: list[Dialog] = []
        self.channels: list[Channel] = []
        self._users: dict[int, User] = {}
        if not self._check_phone():
            raise InvalidPhoneError(self.phone)
        self._work_dir: str = work_dir
        self._database_path: Path = Path(work_dir) / "session.db"
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._database_path.touch(exist_ok=True)
        self._database = Database(self._work_dir)
        self._ws: websockets.ClientConnection | None = None
        self._seq: int = 0
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._recv_task: asyncio.Task[Any] | None = None
        self._incoming: asyncio.Queue[dict[str, Any]] | None = None
        self._device_id = self._database.get_device_id()
        self._token = self._database.get_auth_token()
        self.user_agent = Constants.DEFAULT_USER_AGENT.value
        self._on_message_handler: Callable[[Message], Any] | None = None
        self._on_start_handler: Callable[[], Any | Awaitable[Any]] | None = None
        self._background_tasks: set[asyncio.Task[Any]] = set()
        self.logger = logger or logging.getLogger(f"{__name__}.MaxClient")
        self._setup_logger()

        self.logger.debug(
            "Initialized MaxClient uri=%s work_dir=%s", self.uri, self._work_dir
        )

    def _setup_logger(self) -> None:
        self.logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    @property
    def ws(self) -> websockets.ClientConnection:
        if self._ws is None or not self.is_connected:
            self.logger.critical("WebSocket not connected when access attempted")
            raise WebSocketNotConnectedError
        return self._ws

    def on_message(
        self, handler: Callable[[Message], Any | Awaitable[Any]]
    ) -> Callable[[Message], Any | Awaitable[Any]]:
        """
        Устанавливает обработчик входящих сообщений.

        Args:
            handler: Функция или coroutine, принимающая объект Message.

        Returns:
            Установленный обработчик.
        """
        self._on_message_handler = handler
        self.logger.debug("on_message handler set: %r", handler)
        return handler

    def on_start(
        self, handler: Callable[[], Any | Awaitable[Any]]
    ) -> Callable[[], Any | Awaitable[Any]]:
        """
        Устанавливает обработчик, вызываемый при старте клиента.

        Args:
            handler: Функция или coroutine без аргументов.

        Returns:
            Установленный обработчик.
        """
        self._on_start_handler = handler
        self.logger.debug("on_start handler set: %r", handler)
        return handler

    def add_message_handler(
        self, handler: Callable[[Message], Any | Awaitable[Any]]
    ) -> Callable[[Message], Any | Awaitable[Any]]:
        self.logger.debug("add_message_handler (alias) used")
        self._on_message_handler = handler
        return handler

    def add_on_start_handler(
        self, handler: Callable[[], Any | Awaitable[Any]]
    ) -> Callable[[], Any | Awaitable[Any]]:
        self.logger.debug("add_on_start_handler (alias) used")
        self._on_start_handler = handler
        return handler

    def _check_phone(self) -> bool:
        return bool(re.match(Constants.PHONE_REGEX.value, self.phone))

    def _make_message(
        self, opcode: int, payload: dict[str, Any], cmd: int = 0
    ) -> dict[str, Any]:
        self._seq += 1

        msg = BaseWebSocketMessage(
            ver=11,
            cmd=cmd,
            seq=self._seq,
            opcode=opcode,
            payload=payload,
        ).model_dump(by_alias=True)

        self.logger.debug(
            "make_message opcode=%s cmd=%s seq=%s", opcode, cmd, self._seq
        )
        return msg

    async def _send_interactive_ping(self) -> None:
        while self.is_connected:
            try:
                await self._send_and_wait(
                    opcode=1,
                    payload={"interactive": True},
                    cmd=0,
                )
                self.logger.debug("Interactive ping sent successfully")
            except Exception:
                self.logger.warning("Interactive ping failed", exc_info=True)
            await asyncio.sleep(30)

    async def _connect(self, user_agent: dict[str, Any]) -> dict[str, Any]:
        try:
            self.logger.info("Connecting to WebSocket %s", self.uri)
            self._ws = await websockets.connect(self.uri)
            self.is_connected = True
            self._incoming = asyncio.Queue()
            self._pending = {}
            self._recv_task = asyncio.create_task(self._recv_loop())
            self.logger.info("WebSocket connected, starting handshake")
            return await self._handshake(user_agent)
        except Exception as e:
            self.logger.error("Failed to connect: %s", e, exc_info=True)
            raise ConnectionError(f"Failed to connect: {e}")

    async def _handshake(self, user_agent: dict[str, Any]) -> dict[str, Any]:
        try:
            self.logger.debug(
                "Sending handshake with user_agent keys=%s", list(user_agent.keys())
            )
            resp = await self._send_and_wait(
                opcode=Opcode.HANDSHAKE,
                payload={"deviceId": str(self._device_id), "userAgent": user_agent},
            )
            self.logger.info("Handshake completed")
            return resp
        except Exception as e:
            self.logger.error("Handshake failed: %s", e, exc_info=True)
            raise ConnectionError(f"Handshake failed: {e}")

    async def _request_code(
        self, phone: str, language: str = "ru"
    ) -> dict[str, int | str]:
        try:
            self.logger.info("Requesting auth code")

            payload = RequestCodePayload(
                phone=phone, type=AuthType.START_AUTH, language=language
            ).model_dump(by_alias=True)

            data = await self._send_and_wait(
                opcode=Opcode.REQUEST_CODE, payload=payload
            )
            self.logger.debug(
                "Code request response opcode=%s seq=%s",
                data.get("opcode"),
                data.get("seq"),
            )
            return data.get("payload")
        except Exception:
            self.logger.error("Request code failed", exc_info=True)
            raise RuntimeError("Request code failed")

    async def _send_code(self, code: str, token: str) -> dict[str, Any]:
        try:
            self.logger.info("Sending verification code")

            payload = SendCodePayload(
                token=token, verify_code=code, auth_token_type=AuthType.CHECK_CODE
            ).model_dump(by_alias=True)

            data = await self._send_and_wait(opcode=Opcode.SEND_CODE, payload=payload)
            self.logger.debug(
                "Send code response opcode=%s seq=%s",
                data.get("opcode"),
                data.get("seq"),
            )
            return data.get("payload")
        except Exception:
            self.logger.error("Send code failed", exc_info=True)
            raise RuntimeError("Send code failed")

    async def _recv_loop(self) -> None:
        if self._ws is None:
            self.logger.warning("Recv loop started without websocket instance")
            return

        self.logger.debug("Receive loop started")
        while True:
            try:
                raw = await self._ws.recv()
                try:
                    data = json.loads(raw)
                except Exception:
                    self.logger.warning("JSON parse error", exc_info=True)
                    continue

                seq = data.get("seq")
                fut = self._pending.get(seq) if isinstance(seq, int) else None

                if fut and not fut.done():
                    fut.set_result(data)
                    self.logger.debug("Matched response for pending seq=%s", seq)
                else:
                    if self._incoming is not None:
                        try:
                            self._incoming.put_nowait(data)
                        except asyncio.QueueFull:
                            self.logger.warning(
                                "Incoming queue full; dropping message seq=%s",
                                data.get("seq"),
                            )

                    if (
                        data.get("opcode") == Opcode.NEW_MESSAGE
                        and self._on_message_handler
                    ):
                        try:
                            payload = data.get("payload", {})
                            msg = Message.from_dict(payload.get("message"))
                            if msg:
                                result = self._on_message_handler(msg)
                                if asyncio.iscoroutine(result):
                                    task = asyncio.create_task(result)
                                    self._background_tasks.add(task)
                                    task.add_done_callback(
                                        lambda t: self._background_tasks.discard(t)
                                        or self._log_task_exception(t)
                                    )
                        except Exception:
                            self.logger.exception("Error in on_message_handler")

            except websockets.exceptions.ConnectionClosed:
                self.logger.info("WebSocket connection closed; exiting recv loop")
                break
            except Exception:
                self.logger.exception("Error in recv_loop; backing off briefly")
                await asyncio.sleep(0.5)

    def _log_task_exception(self, task: asyncio.Task[Any]) -> None:
        try:
            exc = task.exception()
            if exc:
                self.logger.exception("Background task exception: %s", exc)
        except Exception:
            pass

    async def _send_and_wait(
        self,
        opcode: int,
        payload: dict[str, Any],
        cmd: int = 0,
        timeout: float = Constants.DEFAULT_TIMEOUT.value,
    ) -> dict[str, Any]:
        ws = self.ws

        msg = self._make_message(opcode, payload, cmd)
        loop = asyncio.get_running_loop()
        fut: asyncio.Future[dict[str, Any]] = loop.create_future()
        self._pending[msg["seq"]] = fut

        try:
            self.logger.debug(
                "Sending frame opcode=%s cmd=%s seq=%s", opcode, cmd, msg["seq"]
            )
            await ws.send(json.dumps(msg))
            data = await asyncio.wait_for(fut, timeout=timeout)
            self.logger.debug(
                "Received frame for seq=%s opcode=%s",
                data.get("seq"),
                data.get("opcode"),
            )
            return data
        except Exception:
            self.logger.exception(
                "Send and wait failed (opcode=%s, seq=%s)", opcode, msg["seq"]
            )
            raise RuntimeError("Send and wait failed")
        finally:
            self._pending.pop(msg["seq"], None)

    async def _sync(self) -> None:
        try:
            self.logger.info("Starting initial sync")

            payload = SyncPayload(
                interactive=True,
                token=self._token,
                chats_sync=0,
                contacts_sync=0,
                presence_sync=0,
                drafts_sync=0,
                chats_count=40,
            ).model_dump(by_alias=True)

            data = await self._send_and_wait(opcode=19, payload=payload)
            if error := data.get("payload", {}).get("error"):
                self.logger.error("Sync error: %s", error)
                return

            for raw_chat in data.get("payload", {}).get("chats", []):
                try:
                    if raw_chat.get("type") == ChatType.DIALOG.value:
                        self.dialogs.append(Dialog.from_dict(raw_chat))
                    elif raw_chat.get("type") == ChatType.CHAT.value:
                        self.chats.append(Chat.from_dict(raw_chat))
                    elif raw_chat.get("type") == ChatType.CHANNEL.value:
                        self.channels.append(Channel.from_dict(raw_chat))
                except Exception:
                    self.logger.exception("Error parsing chat entry")
            self.logger.info(
                "Sync completed: dialogs=%d chats=%d channels=%d",
                len(self.dialogs),
                len(self.chats),
                len(self.channels),
            )
        except Exception:
            self.logger.exception("Sync failed")

    async def send_message(
        self, text: str, chat_id: int, notify: bool
    ) -> Message | None:
        """
        Отправляет сообщение в чат.
        """
        try:
            self.logger.info("Sending message to chat_id=%s notify=%s", chat_id, notify)
            payload = SendMessagePayload(
                chat_id=chat_id,
                message=SendMessagePayloadMessage(
                    text=text,
                    cid=int(time.time() * 1000),
                    elements=[],
                    attaches=[],
                ),
                notify=notify,
            ).model_dump(by_alias=True)

            data = await self._send_and_wait(
                opcode=Opcode.SEND_MESSAGE, payload=payload
            )
            if error := data.get("payload", {}).get("error"):
                self.logger.error("Send message error: %s", error)
            msg = (
                Message.from_dict(data["payload"]["message"])
                if data.get("payload")
                else None
            )
            self.logger.debug("send_message result: %r", msg)
            return msg
        except Exception:
            self.logger.exception("Send message failed")
            return None

    async def edit_message(
        self, chat_id: int, message_id: int, text: str
    ) -> Message | None:
        """
        Редактирует сообщение.
        """
        try:
            self.logger.info(
                "Editing message chat_id=%s message_id=%s", chat_id, message_id
            )
            payload = EditMessagePayload(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                elements=[],
                attaches=[],
            ).model_dump(by_alias=True)
            data = await self._send_and_wait(
                opcode=Opcode.EDIT_MESSAGE, payload=payload
            )
            if error := data.get("payload", {}).get("error"):
                self.logger.error("Edit message error: %s", error)
            msg = (
                Message.from_dict(data["payload"]["message"])
                if data.get("payload")
                else None
            )
            self.logger.debug("edit_message result: %r", msg)
            return msg
        except Exception:
            self.logger.exception("Edit message failed")
            return None

    async def delete_message(
        self, chat_id: int, message_ids: list[int], for_me: bool
    ) -> bool:
        """
        Удаляет сообщения.
        """
        try:
            self.logger.info(
                "Deleting messages chat_id=%s ids=%s for_me=%s",
                chat_id,
                message_ids,
                for_me,
            )

            payload = DeleteMessagePayload(
                chat_id=chat_id, message_ids=message_ids, for_me=for_me
            ).model_dump(by_alias=True)

            data = await self._send_and_wait(
                opcode=Opcode.DELETE_MESSAGE, payload=payload
            )
            if error := data.get("payload", {}).get("error"):
                self.logger.error("Delete message error: %s", error)
                return False
            self.logger.debug("delete_message success")
            return True
        except Exception:
            self.logger.exception("Delete message failed")
            return False

    async def close(self) -> None:
        try:
            self.logger.info("Closing client")
            if self._recv_task:
                self._recv_task.cancel()
                try:
                    await self._recv_task
                except asyncio.CancelledError:
                    self.logger.debug("recv_task cancelled")
            if self._ws:
                await self._ws.close()
            self.is_connected = False
            self.logger.info("Client closed")
        except Exception:
            self.logger.exception("Error closing client")

    def get_cached_user(self, user_id: int) -> User | None:
        """
        Получает юзера из кеша по его ID

        Args:
            user_id (int): ID пользователя.

        Returns:
            User | None: Объект User или None при ошибке.
        """
        user = self._users.get(user_id)
        self.logger.debug("get_cached_user id=%s hit=%s", user_id, bool(user))
        return user

    async def get_users(self, user_ids: list[int]) -> list[User]:
        """
        Получает информацию о пользователях по их ID (с кешем).
        """
        self.logger.debug("get_users ids=%s", user_ids)
        cached = {uid: self._users[uid] for uid in user_ids if uid in self._users}
        missing_ids = [uid for uid in user_ids if uid not in self._users]

        if missing_ids:
            self.logger.debug("Fetching missing users: %s", missing_ids)
            fetched_users = await self.fetch_users(missing_ids)
            if fetched_users:
                for user in fetched_users:
                    self._users[user.id] = user
                    cached[user.id] = user

        ordered = [cached[uid] for uid in user_ids if uid in cached]
        self.logger.debug("get_users result_count=%d", len(ordered))
        return ordered

    async def get_user(self, user_id: int) -> User | None:
        """
        Получает информацию о пользователе по его ID (с кешем).
        """
        self.logger.debug("get_user id=%s", user_id)
        if user_id in self._users:
            return self._users[user_id]

        users = await self.fetch_users([user_id])
        if users:
            self._users[user_id] = users[0]
            return users[0]
        return None

    async def fetch_users(self, user_ids: list[int]) -> None | list[User]:
        """
        Получает информацию о пользователях по их ID.
        """
        try:
            self.logger.info("Fetching users count=%d", len(user_ids))

            payload = FetchContactsPayload(contact_ids=user_ids).model_dump(
                by_alias=True
            )

            data = await self._send_and_wait(
                opcode=Opcode.GET_CONTACTS_INFO, payload=payload
            )
            if error := data.get("payload", {}).get("error"):
                self.logger.error("Fetch users error: %s", error)
                return None

            users = [User.from_dict(u) for u in data["payload"].get("contacts", [])]
            for user in users:
                self._users[user.id] = user

            self.logger.debug("Fetched users: %d", len(users))
            return users
        except Exception:
            self.logger.exception("Fetch users failed")
            return []

    async def fetch_history(
        self,
        chat_id: int,
        from_time: int | None = None,
        forward: int = 0,
        backward: int = 200,
    ) -> list[Message] | None:
        """
        Получает историю сообщений чата.
        """
        if from_time is None:
            from_time = int(time.time() * 1000)

        try:
            self.logger.info(
                "Fetching history chat_id=%s from=%s forward=%s backward=%s",
                chat_id,
                from_time,
                forward,
                backward,
            )

            payload = FetchHistoryPayload(
                chat_id=chat_id,
                from_time=from_time,  # pyright: ignore[reportCallIssue] FIXME: Pydantic Field alias
                forward=forward,
                backward=backward,
            ).model_dump(by_alias=True)

            self.logger.debug("Payload dict keys: %s", list(payload.keys()))

            data = await self._send_and_wait(
                opcode=Opcode.FETCH_HISTORY, payload=payload, timeout=10
            )

            if error := data.get("payload", {}).get("error"):
                self.logger.error("Fetch history error: %s", error)
                return None

            messages = [
                Message.from_dict(msg) for msg in data["payload"].get("messages", [])
            ]
            self.logger.debug("History fetched: %d messages", len(messages))
            return messages
        except Exception:
            self.logger.exception("Fetch history failed")
            return None

    async def _login(self) -> None:
        self.logger.info("Starting login flow")
        request_code_payload = await self._request_code(self.phone)
        temp_token = request_code_payload.get("token")
        if not temp_token or not isinstance(temp_token, str):
            self.logger.critical("Failed to request code: token missing")
            raise ValueError("Failed to request code")

        code = await asyncio.to_thread(input, "Введите код: ")
        if len(code) != 6 or not code.isdigit():
            self.logger.error("Invalid code format entered")
            raise ValueError("Invalid code format")

        login_resp = await self._send_code(code, temp_token)
        token: str | None = (
            login_resp.get("tokenAttrs", {}).get("LOGIN", {}).get("token")
        )
        if not token:
            self.logger.critical("Failed to login, token not received")
            raise ValueError("Failed to login, token not received")

        self._token = token
        self._database.update_auth_token(self._device_id, self._token)
        self.logger.info("Login successful, token saved to database")

    async def start(self) -> None:
        """
        Запускает клиент, подключается к WebSocket, авторизует
        пользователя (если нужно) и запускает фоновый цикл.
        """
        try:
            self.logger.info("Client starting")
            await self._connect(self.user_agent)
            if self._token is None:
                await self._login()
            else:
                await self._sync()

            if self._on_start_handler:
                self.logger.debug("Calling on_start handler")
                result = self._on_start_handler()
                if asyncio.iscoroutine(result):
                    await result

            if self._ws:
                ping_task = asyncio.create_task(self._send_interactive_ping())
                self._background_tasks.add(ping_task)
                ping_task.add_done_callback(
                    lambda t: self._background_tasks.discard(t)
                    or self._log_task_exception(t)
                )

                try:
                    await self._ws.wait_closed()
                except asyncio.CancelledError:
                    self.logger.debug("wait_closed cancelled")
        except Exception:
            self.logger.exception("Client start failed")
