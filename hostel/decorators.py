from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test

def admin_required(usernames):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.username in usernames:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/login/')  # Redirect to login page if not authenticated or not in the admin list
        return wrapper
    return decorator
