__version__ = "1.11.6"

from .base_chat import AbstractEntryPoint
from .entrypoints import (
    OpenRouterEntryPoint,
    AiriChatEntryPoint,
    YandexGPTEntryPoint,
    GigaChatCensoredEntryPoint,
    GigaChatEntryPoint,
    GigaPlusEntryPoint,
    GigaMaxEntryPoint,
    GigaMax2EntryPoint,
    GigaMax2SberdevicesEntryPoint,
    FusionBrainEntrypoint,
)

from .entrypoints_accessor import (
    create_entrypoint,
    EntrypointsAccessor,
)

from .entrypoints_config import EntrypointsConfig
