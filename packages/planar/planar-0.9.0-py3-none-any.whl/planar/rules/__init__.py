from typing import TYPE_CHECKING, Mapping, Tuple

from planar.dependencies import lazy_exports

_DEFERRED_IMPORTS: Mapping[str, Tuple[str, str]] = {
    "rule": (".decorator", "rule"),
    "Rule": (".models", "Rule"),
    "RuleSerializeable": (".models", "RuleSerializeable"),
}

if TYPE_CHECKING:
    from .decorator import rule
    from .models import Rule, RuleSerializeable

    __all__ = ["Rule", "RuleSerializeable", "rule"]

lazy_exports(__name__, _DEFERRED_IMPORTS)
