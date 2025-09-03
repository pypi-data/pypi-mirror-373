import warnings
from copy import deepcopy
from datetime import datetime
from typing import Any, Literal, TypeVar
from collections.abc import Callable

from mmar_mapi.models.chat_item import ChatItem, ReplicaItem, OuterContextItem
from mmar_mapi.models.widget import Widget
from mmar_mapi.type_union import TypeUnion
from pydantic import Field, ValidationError, Extra

from .base import Base


_DT_FORMAT: str = "%Y-%m-%d-%H-%M-%S"
_EXAMPLE_DT: str = datetime(year=1970, month=1, day=1).strftime(_DT_FORMAT)
StrDict = dict[str, Any]
ContentBase = str | Widget | StrDict
Content = ContentBase | list[ContentBase]
T = TypeVar("T")


def now_pretty() -> str:
    return datetime.now().strftime(_DT_FORMAT)


class Context(Base):
    client_id: str = Field("", examples=["543216789"])
    user_id: str = Field("", examples=["123456789"])
    session_id: str = Field(default_factory=now_pretty, examples=["987654321"])
    track_id: str = Field("", examples=["Hello"])
    extra: StrDict | None = Field(None, examples=[None])

    def create_id(self, short: bool = False) -> str:
        uid, sid, cid = self.user_id, self.session_id, self.client_id
        if short:
            return f"{cid}_{uid}_{sid}"
        return f"client_{cid}_user_{uid}_session_{sid}"

    def _get_deprecated_extra(self, field, default):
        # legacy: eliminate after migration
        res = (self.extra or {}).get(field, default)
        warnings.warn(f"Deprecated property `{field}`, should be eliminated", stacklevel=2)
        return res

    # fmt: off
    @property
    def sex(self) -> bool: return self._get_deprecated_extra('sex', True)
    @property
    def age(self) -> int: return self._get_deprecated_extra('age', 0)
    @property
    def entrypoint_key(self) -> str: return self._get_deprecated_extra('entrypoint_key', '')
    @property
    def language_code(self) -> str: return self._get_deprecated_extra('language_code', '')
    @property
    def parent_session_id(self) -> str: return self._get_deprecated_extra('parent_session_id', '')
    # fmt: on


def _get_field(obj: dict, field, val_type: type[T]) -> T | None:
    if not isinstance(obj, dict):
        return None
    val = obj.get(field)
    if val is not None and isinstance(val, val_type):
        return val
    return None


def _get_text(obj: Content) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return "".join(map(_get_text, obj))
    if isinstance(obj, dict) and obj.get("type") == "text":
        return _get_field(obj, "text", str) or ""
    return ""


def _modify_text(obj: Content, callback: Callable[[str], str | None]) -> str:
    if isinstance(obj, str):
        return callback(obj)
    if isinstance(obj, list):
        return [_modify_text(el, callback) for el in obj]
    if isinstance(obj, dict) and obj.get("type") == "text":
        text = _get_field(obj, "text", str) or ""
        text_upd = callback(text)
        return {"type": "text", "text": text_upd}
    return obj


def _get_resource_id(obj: Content) -> str | None:
    if isinstance(obj, list):
        return next((el for el in map(_get_resource_id, obj) if el), None)
    if isinstance(obj, dict) and obj.get("type") == "resource_id":
        return _get_field(obj, "resource_id", str)
    return None


def _get_command(obj: Content) -> dict | None:
    if isinstance(obj, list):
        return next((el for el in map(_get_command, obj) if el), None)
    if isinstance(obj, dict) and obj.get("type") == "command":
        return _get_field(obj, "command", dict)
    return None


def _get_widget(obj: Content) -> Widget | None:
    if isinstance(obj, list):
        return next((el for el in map(_get_widget, obj) if el), None)
    if isinstance(obj, Widget):
        return obj
    return None


# todo fix: generalize functions _get_field


class BaseMessage(Base):
    type: str
    content: Content = Field("", examples=["Привет"])
    date_time: str = Field(default_factory=now_pretty, examples=[_EXAMPLE_DT])
    extra: StrDict | None = Field(None, examples=[None])

    @property
    def text(self) -> str:
        return _get_text(self.content)

    def modify_text(self, callback: Callable[[str], str]) -> "BaseMessage":
        content_upd = _modify_text(self.content, callback)
        return self.model_copy(update=dict(content=content_upd))

    @property
    def body(self) -> str:
        # legacy: eliminate after migration
        return self.text

    @property
    def resource_id(self) -> str | None:
        return _get_resource_id(self.content)

    @property
    def command(self) -> dict | None:
        return _get_command(self.content)

    @property
    def widget(self) -> Widget | None:
        return _get_widget(self.content)

    @staticmethod
    def DATETIME_FORMAT() -> str:
        return _DT_FORMAT

    def with_now_datetime(self):
        return self.model_copy(update=dict(date_time=now_pretty()))

    @property
    def is_ai(self):
        return self.type == "ai"

    @property
    def is_human(self):
        return self.type == "human"


class HumanMessage(BaseMessage):
    type: Literal["human"] = "human"


class AIMessage(BaseMessage):
    type: Literal["ai"] = "ai"
    state: str = Field("", examples=["COLLECTION"])

    @property
    def action(self) -> str:
        return (self.extra or {}).get("action", "")


class MiscMessage(BaseMessage):
    type: Literal["misc"] = "misc"


ChatMessage = TypeUnion[HumanMessage, AIMessage, MiscMessage]


class Chat(Base):
    context: Context = Field(default_factory=Context)
    messages: list[ChatMessage] = Field(default_factory=list)

    class Config:
        extra = Extra.ignore

    def __init__(self, **data):
        extra_fields = set(data.keys()) - set(self.__fields__.keys())
        if extra_fields:
            warnings.warn(f"Chat initialization: extra fields will be ignored: {extra_fields}")
        super().__init__(**data)

    def create_id(self, short: bool = False) -> str:
        return self.context.create_id(short)

    @staticmethod
    def parse(chat_obj: str | dict | ChatItem) -> "Chat":
        return _parse_chat_compat(chat_obj)

    def to_chat_item(self) -> ChatItem:
        return convert_chat_to_chat_item(self)

    def add_message(self, message: ChatMessage):
        self.messages.append(message)

    def add_messages(self, messages: list[ChatMessage]):
        for message in messages:
            self.messages.append(message)

    def replace_messages(self, messages: list[ChatMessage]):
        return self.model_copy(update=dict(messages=messages))

    def get_last_state(self, default: str = "empty") -> str:
        for ii in range(len(self.messages) - 1, -1, -1):
            message = self.messages[ii]
            if isinstance(message, AIMessage):
                return message.state
        return default


def make_content(
    text: str | None = None,
    *,
    resource_id: str | None = None,
    command: dict | None = None,
    widget: Widget | None = None,
) -> Content:
    resource_id = (resource_id or None) and {"type": "resource_id", "resource_id": resource_id}
    command = (command or None) and {"type": "command", "command": command}

    content = list(filter(None, [text, resource_id, command, widget]))
    if len(content) == 0:
        content = ""
    elif len(content) == 1:
        content = content[0]

    return content


def convert_replica_item_to_message(replica: ReplicaItem) -> ChatMessage:
    date_time = replica.date_time
    content = make_content(
        text=replica.body,
        resource_id=replica.resource_id,
        command=replica.command,
        widget=replica.widget,
    )
    # legacy: eliminate after migration
    resource_id = (replica.resource_id or None) and {"type": "resource_id", "resource_id": replica.resource_id}
    body = replica.body
    command = (replica.command or None) and {"type": "command", "command": replica.command}
    widget = replica.widget
    date_time = replica.date_time

    content = list(filter(None, [body, resource_id, command, widget]))
    if len(content) == 0:
        content = ""
    elif len(content) == 1:
        content = content[0]

    is_bot_message = replica.role

    if is_bot_message:
        kwargs = dict(
            content=content,
            date_time=date_time,
            state=replica.state,
            extra=dict(
                **(replica.extra or {}),
                action=replica.action,
                moderation=replica.moderation,
            ),
        )
        res = AIMessage(**kwargs)
    else:
        kwargs = dict(content=content, date_time=date_time)
        res = HumanMessage(**kwargs)
    return res


def convert_outer_context_to_context(octx: OuterContextItem) -> Context:
    # legacy: eliminate after migration
    context = Context(
        client_id=octx.client_id,
        user_id=octx.user_id,
        session_id=octx.session_id,
        track_id=octx.track_id,
        extra=dict(
            sex=octx.sex,
            age=octx.age,
            parent_session_id=octx.parent_session_id,
            entrypoint_key=octx.entrypoint_key,
            language_code=octx.language_code,
        ),
    )
    return context


def convert_chat_item_to_chat(chat_item: ChatItem) -> Chat:
    # legacy: eliminate after migration
    context = convert_outer_context_to_context(chat_item.outer_context)
    messages = list(map(convert_replica_item_to_message, chat_item.inner_context.replicas))
    res = Chat(context=context, messages=messages)
    return res


def convert_context_to_outer_context(context: Context) -> OuterContextItem:
    # legacy: eliminate after migration
    extra = context.extra or {}
    return OuterContextItem(
        client_id=context.client_id,
        user_id=context.user_id,
        session_id=context.session_id,
        track_id=context.track_id,
        sex=extra.get("sex"),
        age=extra.get("age"),
        parent_session_id=extra.get("parent_session_id"),
        entrypoint_key=extra.get("entrypoint_key"),
        language_code=extra.get("language_code"),
    )


def convert_message_to_replica_item(message: ChatMessage) -> ReplicaItem | None:
    # legacy: eliminate after migration
    m_type = message.type
    if m_type in {"ai", "human"}:
        role = m_type == "ai"
    else:
        return None

    extra = deepcopy(message.extra) if message.extra else {}
    action = extra.pop("action", "")
    moderation = extra.pop("moderation", "OK")

    kwargs = dict(
        role=role,
        body=message.text,
        resource_id=message.resource_id,
        command=message.command,
        widget=message.widget,
        date_time=message.date_time,
        extra=extra or None,
        state=getattr(message, "state", ""),
        action=action,
        moderation=moderation,
    )
    return ReplicaItem(**kwargs)


def convert_chat_to_chat_item(chat: Chat) -> ChatItem:
    # legacy: eliminate after migration
    return ChatItem(
        outer_context=convert_context_to_outer_context(chat.context),
        inner_context=dict(replicas=list(map(convert_message_to_replica_item, chat.messages))),
    )


def parse_chat_item_as_chat(chat_obj: str | dict | ChatItem) -> Chat:
    # legacy: eliminate after migration
    if isinstance(chat_obj, ChatItem):
        chat_item = chat_obj
    else:
        chat_item = ChatItem.parse(chat_obj)
    res = convert_chat_item_to_chat(chat_item)
    return res


def _parse_chat(chat_obj: str | dict) -> Chat:
    if isinstance(chat_obj, dict):
        return Chat.model_validate(chat_obj)

    return Chat.model_validate_json(chat_obj)


def is_chat_item(chat_obj: str | dict | ChatItem) -> bool:
    if isinstance(chat_obj, ChatItem):
        return True
    if isinstance(chat_obj, dict):
        return "OuterContext" in chat_obj
    if isinstance(chat_obj, str):
        return "OuterContext" in chat_obj
    warnings.warn(f"Unexpected chat object: {chat_obj} :: {type(chat_obj)}")
    return False


def _parse_chat_compat(chat_obj: str | dict | ChatItem) -> Chat:
    # legacy: eliminate after migration
    if is_chat_item(chat_obj):
        return parse_chat_item_as_chat(chat_obj)
    try:
        return _parse_chat(chat_obj)
    except ValidationError as ex:
        warnings.warn(f"Failed to parse chat: {ex}")
        return parse_chat_item_as_chat(chat_obj)
