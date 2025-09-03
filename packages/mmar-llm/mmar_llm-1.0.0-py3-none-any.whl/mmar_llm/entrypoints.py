from .open_router_entrypoint import OpenRouterEntryPoint
from .airi_entrypoint import AiriChatEntryPoint
from .yandex_gpt_entrypoint import YandexGPTEntryPoint
from .fusion_brain_entrypoint import FusionBrainEntrypoint
from .gigachat_entrypoint import (
    GigaChatCensoredEntryPoint,
    GigaChatEntryPoint,
    GigaPlusEntryPoint,
    GigaMaxEntryPoint,
    GigaMax2EntryPoint,
    GigaMax2SberdevicesEntryPoint,
)

ENTRYPOINTS: dict[str, str] = {
    "airi": AiriChatEntryPoint,
    "giga": GigaChatEntryPoint,
    "giga-max": GigaMaxEntryPoint,
    "giga-max-2": GigaMax2EntryPoint,
    "giga-plus": GigaPlusEntryPoint,
    "giga-censored": GigaChatCensoredEntryPoint,
    "open-router": OpenRouterEntryPoint,
    "yandex": YandexGPTEntryPoint,
    "fusion-brain": FusionBrainEntrypoint,
    "giga-max-2-sberdevices": GigaMax2SberdevicesEntryPoint,
}


def create_entrypoint(entrypoint_name: str, entrypoint_args: dict[str, any]):
    entrypoint_class = ENTRYPOINTS.get(entrypoint_name)
    if entrypoint_class is None:
        err = f"Not found entrypoint for entrypoint_name={entrypoint_name}"
        raise ValueError(err)
    return entrypoint_class(**entrypoint_args)
