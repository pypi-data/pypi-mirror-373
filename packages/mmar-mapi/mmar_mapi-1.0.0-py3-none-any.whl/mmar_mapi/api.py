from mmar_mapi.models.chat import Chat, ChatMessage
from mmar_mapi.models.tracks import DomainInfo, TrackInfo
from pydantic import BaseModel


Value = str
Interpretation = str
ResourceId = str


class ChatManagerAPI:
    def get_domains(self, *, client_id: str, language_code: str = "ru") -> list[DomainInfo]:
        raise NotImplementedError

    def get_tracks(self, *, client_id: str, language_code: str = "ru") -> list[TrackInfo]:
        raise NotImplementedError

    def get_response(self, *, chat: Chat) -> list[ChatMessage]:
        raise NotImplementedError


class TextGeneratorAPI:
    def process(self, *, chat: Chat) -> str:
        raise NotImplementedError


class ContentInterpreterRemoteResponse(BaseModel):
    interpretation: str
    resource_fname: str
    resource: bytes


class ContentInterpreterRemoteAPI:
    def interpret_remote(
        self, *, kind: str, query: str, resource: bytes, chat: Chat | None = None
    ) -> ContentInterpreterRemoteResponse:
        raise NotImplementedError


class ClassifierAPI:
    def get_values(self) -> list[Value]:
        raise NotImplementedError

    def evaluate(self, *, chat: Chat) -> Value:
        raise NotImplementedError


class CriticAPI:
    def evaluate(self, *, text: str, chat: Chat | None = None) -> float:
        raise NotImplementedError


class ContentInterpreterAPI:
    def interpret(
        self, *, kind: str, query: str, resource_id: str = "", chat: Chat | None = None
    ) -> tuple[Interpretation, ResourceId | None]:
        raise NotImplementedError


class TextProcessorAPI:
    def process(self, *, text: str, chat: Chat | None = None) -> str:
        raise NotImplementedError
