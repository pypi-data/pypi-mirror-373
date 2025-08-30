import base64 as BASE64
import inspect
from enum import StrEnum
from typing import Any, Dict, List, Optional, Union

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from .bot_enums import *

funcs = {}

name_map = {
    "message_direct": "messageDirect",
    "message_add": "messageAdd",
    "bot_hourly": "botHourly",
    "file_create": "fileCreate",
    "conversation_hourly": "conversationHourly",
    "conversation_start": "conversationStart",
    "conversation_user_add": "conversationUserAdd",
    "conversation_user_show": "conversationUserShow",
    "user_visible": "userVisible",
    "web_page_updated": "webPageUpdated",
}


def export(name: str):
    """
    Decorator to export functions from your bot
    """

    def inner(func):
        global funcs

        sig = inspect.signature(func)
        parameters = sig.parameters.values()

        # Check if function accepts arbitrary kwargs (**kwargs)
        accepts_kwargs = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters
        )

        # Collect allowed parameter names if no **kwargs
        allowed_params = set()
        if not accepts_kwargs:
            for param in parameters:
                if param.kind in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY,
                ):
                    allowed_params.add(param.name)

        def wrapper(**kwargs):
            if not accepts_kwargs:
                # Filter kwargs to only allowed parameters
                filtered_kwargs = {
                    k: v for k, v in kwargs.items() if k in allowed_params
                }
                return func(**filtered_kwargs)
            return func(**kwargs)

        mapped_name = name_map.get(name)

        funcs[mapped_name if mapped_name is not None else name] = wrapper

        return func

    return inner


class ImageType(StrEnum):
    PUBLIC = "public"
    """public"""

    URI = "uri"
    """uri"""

    BASE64 = "base64"
    """base64"""


class ImageMimeType(StrEnum):
    JPG = "image/jpeg"
    """image/jpeg"""

    PNG = "image/png"
    """image/png"""

    GIF = "image/gif"
    """image/gif"""

    WEBP = "image/webp"
    """image/webp"""


@dataclass
class Image:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    type: ImageType
    width: int
    height: int
    base64: Optional[str] = None
    mime_type: Optional[ImageMimeType] = None
    uri: Optional[str] = None
    description: Optional[str] = None
    sizes: Optional[List[int]] = None

    def __init__(
        self,
        type: Optional[ImageType] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        base64: Optional[str] = None,
        mime_type: Optional[ImageMimeType] = None,
        uri: Optional[str] = None,
        description: Optional[str] = None,
        sizes: Optional[List[int]] = None,
        file: Optional[str] = None,
        buffer: Optional[bytes] = None,
    ):
        if file is not None:
            with open(file, "rb") as f:
                type = ImageType.BASE64
                base64 = BASE64.b64encode(f.read()).decode()

        if buffer is not None:
            type = ImageType.BASE64
            base64 = BASE64.b64encode(buffer).decode()

        self.type = (
            type
            if type is not None
            else (ImageType.URI if uri is not None else ImageType.BASE64)
        )
        self.width = width if width is not None else 1024
        self.height = height if height is not None else 1024
        self.base64 = base64
        self.mime_type = (
            mime_type
            if mime_type is not None
            else (ImageMimeType.JPG if base64 is not None else None)
        )
        self.uri = uri
        self.description = description
        self.sizes = sizes


class ButtonType(StrEnum):
    LINK = "link"
    """link"""

    TEXT = "text"
    """text"""

    BUTTON = "button"
    """button"""

    MENU = "menu"
    """menu"""


@dataclass
class Button:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    type: ButtonType
    icon: Optional[Icon] = None
    text: Optional[str] = None
    lang: Optional[UserLang] = None
    func: Optional[str] = None
    uri: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    buttons: Optional[List["Button"]] = None
    selected: Optional[bool] = None
    disabled: Optional[bool] = None


@dataclass
class MenuItem:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    func: str
    title: str
    params: Optional[Dict[str, Any]] = None
    checked: Optional[bool] = None
    enabled: Optional[bool] = None


@dataclass
class Message:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    id: str
    created: int
    user_id: str
    text: str
    is_bot: bool
    markdown: Optional[str] = None
    system: Optional[bool] = None
    mention_user_ids: Optional[List[str]] = None
    lang: Optional[UserLang] = None
    only_user_ids: Optional[List[str]] = None
    visibility: Optional[MessageVisibility] = None
    color: Optional[MessageColor] = None
    buttons: Optional[List[Button]] = None
    mood: Optional[Mood] = None
    impersonate_user_id: Optional[str] = None
    file_ids: Optional[List[str]] = None
    context_file_id: Optional[str] = None
    parent_message_id: Optional[str] = None


TextGenMessageContent = Union[str, Image]


@dataclass
class TextGenMessage:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    role: TextGenRole
    content: Union[str, List[TextGenMessageContent]]


@dataclass
class TextGenTool:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class Avatar:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    image: Image
    background: Optional[Image]


@dataclass
class User:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    id: str
    name: str
    bio: str
    avatar: Avatar
    voice_id: Optional[str]
    birthday: Optional[int]
    type: str
    lang: UserLang
    timezone: Timezone


@dataclass
class Emotion:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    neutral: int
    happy: int
    sad: int
    angry: int
    fearful: int
    disgusted: int
    surprised: int


@dataclass
class LiveUser:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    id: str
    emotion: Optional[Emotion]
    image: Optional[Image]


@dataclass
class Bot:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    id: str
    name: str
    bio: str
    tags: List[BotTag]


@dataclass
class File:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    id: str
    user_id: str
    type: FileType
    title: str
    text: Optional[str] = None
    image: Optional[Image] = None
    thumbnail: Optional[Image] = None
    markdown: Optional[str] = None
    uri: Optional[str] = None
    page: Optional[dict] = None
    tags: Optional[List[str]] = None


@dataclass
class Conversation:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    id: str
    type: ConversationType
    title: str
    file_id: Optional[str] = None


@dataclass
class NewsArticle:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    title: str
    content: str
    uri: Optional[str]


@dataclass
class FileChunk:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    file_id: str
    text: str


@dataclass
class SearchArticle:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    title: str
    synopsis: str
    uri: Optional[str]


class ConversationContentType(StrEnum):
    FILE = "file"
    """file"""

    URI = "uri"
    """uri"""


@dataclass
class ConversationContent:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    type: ConversationContentType
    file_id: Optional[str] = None
    disabled: Optional[bool] = None
    uri: Optional[str] = None


@dataclass
class WebPageData:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    html: str
    url: str
    title: str


@dataclass
class KagiSearchItem:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    url: str
    title: str
    snippet: str
    published: Optional[int] = None
    thumbnail: Optional[Image] = None

    def __init__(
        self,
        url: str,
        title: str,
        snippet: str,
        published: Optional[int] = None,
        thumbnail: Optional[Union[Image, dict]] = None,
    ):
        self.url = url
        self.title = title
        self.snippet = snippet
        self.published = published
        self.thumbnail = (
            Image(**thumbnail)
            if thumbnail is not None and isinstance(thumbnail, dict)
            else thumbnail
        )


@dataclass
class KagiSearchOutput:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    items: List[KagiSearchItem]
    related: Optional[List[str]] = None

    def __init__(
        self,
        items: List[Union[KagiSearchItem, dict]],
        related: Optional[List[str]] = None,
    ):
        self.related = related
        self.items = list(
            map(lambda x: KagiSearchItem(**x) if isinstance(x, dict) else x, items)
        )


@dataclass
class Padding:
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields

    left: int
    top: int
    right: int
    bottom: int
