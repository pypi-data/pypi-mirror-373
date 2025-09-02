from django.http import HttpRequest, JsonResponse

from . import utils


def get_table_choices(request: HttpRequest) -> JsonResponse:
    """
    After choosing table, form has to show available columns. It's done
    by JavaScript to call this view to get that data. URL expect one
    GET parameter called ``table``. It's because it's easier to dynamicly
    change in JavaScript.

    Output format is same as from :any:`cms_qe_table.utils.get_table_choices`.
    """
    table = request.GET.get('table', '')
    return JsonResponse(utils.get_table_choices(table))
