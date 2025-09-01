from contextvars import ContextVar
import time


trace_id = ContextVar("trace_id", default='')
session_id = ContextVar("session_id", default='')
seq = ContextVar("seq", default=1)
user_id = ContextVar("user_id", default='0')
user_info = ContextVar("user_info", default={})
current_tenant_id = ContextVar("current_tenant_id", default=0)
tenant_ids = ContextVar("tenant_ids", default=[])
dep_id = ContextVar("dep_id", default=0)
kxy_roles = ContextVar("roles", default=[])
access_token = ContextVar("access_token", default='')
last_log_time = ContextVar("last_log_time", default=time.time())
