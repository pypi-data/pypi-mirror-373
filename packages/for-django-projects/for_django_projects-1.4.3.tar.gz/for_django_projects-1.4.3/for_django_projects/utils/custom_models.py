import re
from django.db.models import Value
from django.utils.safestring import mark_safe
from django.conf import settings

class CustomValueDb(Value):
    def __init__(self, value, output_field=None):
        from django.db.models import IntegerField, CharField, FloatField, DecimalField, BooleanField, DateField, DateTimeField
        type_value = type(value).__name__.lower()
        if not output_field:
            if "int" in type_value:
                output_field = IntegerField()
            if "str" in type_value:
                output_field = CharField()
            if "float" in type_value:
                output_field = FloatField()
            if "decimal" in type_value:
                output_field = DecimalField()
            if "bool" in type_value:
                output_field = BooleanField()
            if "date" in type_value:
                output_field = DateField()
            if "datetime" in type_value:
                output_field = DateTimeField()
        super().__init__(value, output_field=output_field)


class FormException(Exception):
    def __init__(self, form, prefix="", sufix=""):
        super().__init__("Error en el formulario")
        alerta = ""
        if isinstance(form, list) or isinstance(form, tuple):
            self.errors = []
            for x in form:
                for k, v in x.errors.items():
                    self.errors.append({prefix+k+sufix: v[0]})
                    self.errors.append({form[k].html_name: v[0]})
        else:
            self.errors = [{prefix+k+sufix: v[0]} for k, v in form.errors.items()]
            self.errors = [{form[k].html_name: v[0]} for k, v in form.errors.items()]
        for x in form.errors.get('__all__') or []:
            for key in getattr(settings, 'CONSTRAINT_MSG', {}).keys():
                if re.search(f"\\b{key}\\b", x):
                    alerta += f'<div>{getattr(settings, "CONSTRAINT_MSG", {})[key]}</div>'
        self.dict_error = {
            'error': True,
            "form": self.errors,
            "message": "Datos incorrectos, revise la información registrada.",
            "alerta": mark_safe(alerta)
        }


class SomeValueException(Exception):
    def __init__(self, error):
        super().__init__(error)