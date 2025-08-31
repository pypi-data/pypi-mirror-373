from django.contrib import messages

__all__ = (
    "info",
    "success",
    "warning",
    "error"
)

def __general(tipo, request, message, extra_tags="", fail_silently=False):
    extra = "type_swal " + (extra_tags or "")
    if tipo == "info":
        messages.info(request, message, extra, fail_silently)
    if tipo == "success":
        messages.success(request, message, extra, fail_silently)
    if tipo == "warning":
        messages.warning(request, message, extra, fail_silently)
    if tipo == "error":
        messages.error(request, message, extra, fail_silently)

def info(request, message, extra_tags="", fail_silently=False):
    __general("info", request, message, extra_tags, fail_silently)

def success(request, message, extra_tags="", fail_silently=False):
    __general("success", request, message, extra_tags, fail_silently)

def warning(request, message, extra_tags="", fail_silently=False):
    __general("warning", request, message, extra_tags, fail_silently)

def error(request, message, extra_tags="", fail_silently=False):
    __general("error", request, message, extra_tags, fail_silently)