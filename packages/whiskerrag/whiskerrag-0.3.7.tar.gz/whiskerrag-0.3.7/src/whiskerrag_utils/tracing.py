# tracing_context.py
from contextvars import ContextVar

# 定义全局 ContextVars
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="unknown")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="unknown")
tenant_id_ctx: ContextVar[str] = ContextVar("tenant_id", default="system")


# --- traceId ---
def set_trace_id(trace_id: str) -> None:
    trace_id_ctx.set(trace_id)


def get_trace_id() -> str:
    return trace_id_ctx.get()


# --- userId ---
def set_user_id(user_id: str) -> None:
    user_id_ctx.set(user_id)


def get_user_id() -> str:
    return user_id_ctx.get()


# --- tenantId ---
def set_tenant_id(tenant_id: str) -> None:
    tenant_id_ctx.set(tenant_id)


def get_tenant_id() -> str:
    return tenant_id_ctx.get()
