"""插件系统：通过 entry_points (group='safetybox.plugins') 加载第三方扩展。"""
from importlib import metadata
from typing import Callable, List

PluginCallable = Callable[..., dict]

def load_plugins() -> List[PluginCallable]:
    plugins = []
    for ep in metadata.entry_points().select(group='safetybox.plugins'):
        try:
            fn = ep.load()
            plugins.append(fn)
        except Exception:
            continue
    return plugins

def register_plugin(fn: PluginCallable):
    global _REG_PLUGINS
    try:
        _REG_PLUGINS.append(fn)
    except NameError:
        _REG_PLUGINS = [fn]

def get_runtime_plugins():
    return list(globals().get('_REG_PLUGINS', []))
