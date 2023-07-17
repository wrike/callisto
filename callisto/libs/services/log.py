from __future__ import annotations

import collections
import json
import logging
import typing as t

from ... import __module_name__, __version__
from ..trace import get_trace_id_value


if t.TYPE_CHECKING:
    BaseAdapter = logging.LoggerAdapter[logging.Logger]
else:
    BaseAdapter = logging.LoggerAdapter

TRACE_CONTEXT_KEY_NAME = "__trace_context__"


def traced_logger_adapter_factory(
    trace_id_getter: t.Callable[[], str],
    separator: str = ">>>",
    overall_context: t.Mapping[str, t.Any] | None = None,
) -> t.Type[logging.LoggerAdapter[logging.Logger]]:
    class TracedLoggerAdapter(BaseAdapter):
        # an adapter to reformat log message and parse additional context

        def process(self, msg: str, kwargs: t.MutableMapping[str, t.Any]) -> tuple[str, dict[str, t.Any]]:
            message_context = {
                "tid": trace_id_getter(),
            }

            if "extra" in kwargs:
                trace_context = extract_trace_context(kwargs["extra"])

                message_context.update(trace_context)
            else:
                kwargs["extra"] = {}

            if overall_context:
                kwargs["extra"].update(overall_context)

            update_msg = f"{msg} {separator} {json.dumps(message_context)}"

            return update_msg, t.cast(dict[str, t.Any], kwargs)

    return TracedLoggerAdapter


def add_trace_context(
    trace_context: t.MutableMapping[str, t.Any] | None = None,
    additional: t.Mapping[str, t.Any] | None = None,
    **kwargs: t.Any,
) -> dict[str, t.Any]:
    # must be used with any log message to attach special trace section

    normalized_context = {}

    if trace_context:
        overall_trace_context = dict(collections.ChainMap(trace_context, kwargs))
    else:
        overall_trace_context = kwargs

    for k, v in overall_trace_context.items():
        normalized_context[k] = repr(v) if not isinstance(v, str) else v

    context = {TRACE_CONTEXT_KEY_NAME: normalized_context}

    if additional:
        context.update(additional)

    return context


def extract_trace_context(context: t.MutableMapping[str, t.Any]) -> dict[str, t.Any]:
    return context.pop(TRACE_CONTEXT_KEY_NAME, {})


traced_logger_adapter = traced_logger_adapter_factory(
    get_trace_id_value,
    overall_context={
        "env": "production",
        "module_version": __version__,
        "module_name": __module_name__,
    },
)


def get_logger(name: str) -> logging.LoggerAdapter[logging.Logger]:
    return traced_logger_adapter(logging.getLogger(name), extra={})


logger = get_logger("callisto.services")

l_ctx = add_trace_context
