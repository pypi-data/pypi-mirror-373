__version__ = "5.2.4"

from .file_storage import FileStorage, ResourceId
from .models.base import Base
from .models.base_config_models import GigaChatConfig
from .models.chat import Chat, Context, ChatMessage, AIMessage, HumanMessage, MiscMessage, make_content
from .models.chat_item import ChatItem, OuterContextItem, InnerContextItem, ReplicaItem
from .models.enums import MTRSLabelEnum, DiagnosticsXMLTagEnum, MTRSXMLTagEnum, DoctorChoiceXMLTagEnum
from .models.tracks import TrackInfo, DomainInfo
from .models.widget import Widget
from .utils import make_session_id
from .xml_parser import XMLParser
