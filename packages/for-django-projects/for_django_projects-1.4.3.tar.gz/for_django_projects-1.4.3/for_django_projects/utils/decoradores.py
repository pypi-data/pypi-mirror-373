import re
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings

from for_django_projects.utils.custom_models import SomeValueException
from for_django_projects.utils.funciones import redirectAfterPostGet


def custom_atomic_request(func):
    from for_django_projects.utils.custom_models import FormException
    import sys
    def validate_request(*args, **kwargs):
        res_json = []
        request = args[0]
        has_except = False
        error_message = ""
        if request.method == "POST":
            action = request.POST.get("action")
            try:
                with transaction.atomic():
                    val_func = func(*args, **kwargs)
            except ValueError as ex:
                res_json.append({'error': True,
                                 "message": str(ex)
                                 })
                val_func = JsonResponse(res_json, safe=False)
                has_except = True
                error_message = str(ex)
            except FormException as ex:
                res_json.append(ex.dict_error)
                val_func = JsonResponse(res_json, safe=False)
                has_except = True
                error_message = "Formulario no válido"
            except IntegrityError as ex:
                has_except = True
                msg = str(ex)
                error_message = "Integrity Error"
                constraing_msgs = getattr(settings, 'CONSTRAINT_MSG', {})
                if hasattr(ex, '__cause__') and ex.__cause__ and hasattr(ex.__cause__, 'args') and ex.__cause__.args:
                    error_message = ex.__cause__.args[0]
                elif "UNIQUE constraint failed".upper() in msg.upper():
                    error_message = constraing_msgs.get('unique_constraint_failed') or "UNIQUE constraint failed"
                elif "CHECK constraint failed" in msg:
                    error_message = constraing_msgs.get('check_constraint_failed') or "CHECK constraint failed"
                if request.user.is_superuser:
                    error_message = f"{error_message} | {msg}"
                res_json.append(
                    {
                        'error': has_except,
                        "message": error_message
                    }
                )
                val_func = JsonResponse(res_json, safe=False)
            except Exception as ex:
                res_json.append({'error': True,
                                 "message": "Intente Nuevamente"
                                 })
                val_func = JsonResponse(res_json, safe=False)
                has_except = True
                error_message = "Intente Nuevamente"
                if request.user.is_superuser:
                    error_message = f"{error_message} | {ex}"
        elif request.method == "GET":
            val_func = func(*args, **kwargs)
        if has_except and not request.is_ajax:
            messages.error(request, error_message)
            val_func = redirect(redirectAfterPostGet(request))
        return val_func

    return validate_request


def sync_to_async_function(f):
    import threading
    def threading_func(*a, **kw):
        t = threading.Thread(target=f, args=a, kwargs=kw)
        t.start()
        # t.join()

    return threading_func


def validate_atomic_request(func):
    from for_django_projects.utils.custom_models import FormException
    import sys
    def validate_request(*args, **kwargs):
        res_json = {}
        request = args[0]
        has_except = False
        error_message = ""
        if request.method == "POST":
            action = request.POST.get("action")
            try:
                with transaction.atomic():
                    val_func = func(*args, **kwargs)
            except SomeValueException as ex:
                res_json = {"message": str(ex)}
                val_func = JsonResponse(res_json, status=202)
                has_except = True
                error_message = str(ex)
            except FormException as ex:
                res_json = ex.dict_error
                val_func = JsonResponse(res_json, status=202)
                has_except = True
                error_message = "Formulario no válido"
            except IntegrityError as ex:
                has_except = True
                msg = str(ex)
                error_message = "Integrity Error"
                constraing_msgs = getattr(settings, 'CONSTRAINT_MSG', {})
                if hasattr(ex, '__cause__') and ex.__cause__ and hasattr(ex.__cause__, 'args') and ex.__cause__.args:
                    error_message = ex.__cause__.args[0]
                elif "UNIQUE constraint failed".upper() in msg.upper():
                    error_message = constraing_msgs.get('unique_constraint_failed') or "UNIQUE constraint failed"
                elif "CHECK constraint failed" in msg:
                    error_message = constraing_msgs.get('check_constraint_failed') or "CHECK constraint failed"
                if request.user.is_superuser:
                    error_message = f"{error_message} | {msg}"
                res_json = {
                    'error': has_except,
                    "message": error_message
                }
                val_func = JsonResponse(res_json, status=202)
            except Exception as ex:
                error_message = "Intente Nuevamente"
                if request.user.is_superuser:
                    error_message = f"{error_message} | {ex}"
                res_json = {
                    "message": error_message
                }
                val_func = JsonResponse(res_json, status=202)
                has_except = True
        elif request.method == "GET":
            val_func = func(*args, **kwargs)
        if has_except and not request.is_ajax:
            messages.error(request, error_message)
            val_func = redirect(redirectAfterPostGet(request))
        return val_func

    return validate_request
