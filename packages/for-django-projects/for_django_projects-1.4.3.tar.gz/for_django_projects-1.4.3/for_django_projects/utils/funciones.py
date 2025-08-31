import json
from django.core import signing
from django.db.models import Q


def customgetattr(object, _name):
    name = _name
    kwargs = {}
    if "{" in _name:
        dict_obj = json.loads(_name)
        name = dict_obj["name"]
        kwargs = dict_obj.get('kwargs') or {}
    tree = name.split(".")
    obj = object
    for t in tree:
        if hasattr(obj, t):
            obj = getattr(obj, t)
            obj = obj(**kwargs) if callable(obj) else obj
        else:
            obj = ""
            break
    return obj


def redirectAfterPostGet(request, campos_add={}):
    dict_url_vars = request.GET.get('dict_url_vars') or request.POST.get('dict_url_vars') or ""
    if dict_url_vars:
        try:
            dict_url_vars = json.loads(get_decrypt(dict_url_vars)[1]).get(request.path) or ""
        except Exception as ex:
            print(ex)
    salida = "?action=add&" if '_add' in request.POST else request.path + "?"
    if '_add' in request.POST:
        for k, v in campos_add.items():
            salida += "&{}={}".format(k, v)
    return salida + "{}".format(dict_url_vars)


def ip_client_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_encrypt(values):
    try:
        return True, signing.dumps(values, compress=True)
    except Exception as ex:
        return False, str(ex)


def get_decrypt(cyphertxt):
    try:
        return True, signing.loads(cyphertxt)
    except Exception as ex:
        return False, str(ex)


def remover_espacios_de_mas(valor: str) -> str:
    import re
    return re.sub("[ \t]+", " ", (re.sub("[ \t]+", " ", (valor or "").strip()) or "").strip())


def formarCondicion(c, busqueda):
    if c.endswith("__islisttype"):
        return Q(**{c.replace("__islisttype", ""): [busqueda]})
    else:
        return Q(**{c: busqueda})
def campoSinFiltro(c):
    filtros = ["__icontains", "__contains", "__startswith", "__istartswith", "__endswith", "__iendswith", "__range", "__search"]
    for f in filtros:
        if c.endswith(f):
            return False
    return True
def criterioBusquedaDinamico(criterio: str, campos: list, isPostgres=True):
    '''Si el modelo no proviene de una base de datos postgres set isPostgres=False'''
    from django.db.models import Q
    from django.utils.text import smart_split
    import re
    filtros = Q()
    valor_a_buscar = remover_espacios_de_mas(criterio)
    or_values = valor_a_buscar.split('|')
    for ov in or_values:
        or_filters = Q()
        icontains_texts = [f'%{x}%' for x in re.findall(r'%([^%]+)%', ov)]
        for it in icontains_texts:
            ov = ov.replace(it, '')
        criterio_list = icontains_texts + list(smart_split(ov))
        for cl in criterio_list:
            cri = cl.strip()
            f = Q()
            if cri:
                for c in campos:
                    if campoSinFiltro(c):
                        if cri.startswith("%") and cri.endswith("%"):
                            c = c + "__icontains"
                        elif cri.startswith("%"):
                            c = c + "__iendswith"
                        elif cri.endswith("%"):
                            c = c + "__istartswith"
                        else:
                            if isPostgres:
                                f |= formarCondicion(c + "__search", cri.replace("%", ""))
                            c = c + "__icontains"
                    f |= formarCondicion(c, cri.replace("%", ""))
                or_filters &= (f)
        filtros |= (or_filters)
    return (filtros)