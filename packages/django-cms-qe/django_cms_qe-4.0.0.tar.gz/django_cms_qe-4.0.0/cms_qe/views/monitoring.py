from django.http import JsonResponse

from cms_qe.utils import get_functions


def get_monitoring(request):  # pylint: disable=unused-argument
    """
    Returns JSON response with data about monitoring of application.
    """
    result = get_monitoring_data()
    status_code = 200 if result['status'] else 500
    return JsonResponse(result, status=status_code)


def get_monitoring_data():
    """
    Helper to check all installed apps. It looks for function ``get_status`` in
    modules ``monitoring``. If you want to add check for your module, create your
    file called ``monitoring.py`` and add something like this:

    .. code-block:: python

        def get_status():
            # check
            return True  # or False or error message or dict

    Result is dictionary of two keys, overall ``status`` which is ``True`` is all
    calls returns ``True``, in other cases ``False``. Second key is ``app_details``
    with dictionary with key of every app which has monitoring and it's status.
    Status can be bool or any message which means something is wrong.

    You can also return dictionary with the details of your app. For example::

        {
            'databse': True,
            'cache': 'problem to connect',
            # ...
        }
    """
    result = {
        'status': True,
        'app_details': {},
    }
    for app_name, monitoring_function in get_functions('monitoring', 'get_status'):
        try:
            app_state = monitoring_function()
        except Exception as exc:  # pylint: disable=broad-except
            app_state = str(exc)
            is_ok = False
        else:
            if isinstance(app_state, dict):
                is_ok = all(v is True for v in app_state.values())
            else:
                is_ok = app_state is True

        result['app_details'][app_name] = app_state
        result['status'] &= is_ok
    return result
