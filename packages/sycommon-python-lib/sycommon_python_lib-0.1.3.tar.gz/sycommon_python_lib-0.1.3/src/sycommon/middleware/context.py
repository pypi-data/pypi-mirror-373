import contextvars

current_trace_id = contextvars.ContextVar("trace_id", default=None)
