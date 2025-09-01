# dj-raincheck ☔️

> Schedule functions to run after a request in Django without additional infrastructure.

Background tasks are great, but they are often overpowered for certain tasks and can require additional services. `dj-raincheck` is a simpler alternative. It will execute code after the request is complete, without the need for additional background tasks, daemons, or queues.

## Installation 💻

```shell
uv add dj-raincheck

OR

pip install dj-raincheck
```

## Usage 🧑‍🔧

1. Add `dj_raincheck` to your `INSTALLED_APPS` in `settings.py`.

```python
# settings.py

INSTALLED_APPS = (
    ...
    "dj_raincheck",
)
```

2. Create a function that you want to run after the current request/response lifecycle.

```python
# tasks.py

from django.core.mail import send_mail
from dj_raincheck import raincheck

@raincheck
def send_email(to: str, subject: str, body: str) -> None:
    send_mail(subject, body, 'me@example.com', [to])
```

3. Queue the function in view code to be run after the current request/response lifecycle by calling its `schedule` method and passing in the necessary args or kwargs.

```python
# views.py

from .tasks import send_email

# Function-based view example
def index(request):
    ...

    send_email.schedule('customer@example.com', 'Confirm Signup', body)

    return render(...)

# Class-based view example
class IndexView(View):
    def get(self, request, *args, **kwargs):
        ...
        
        send_email.schedule('customer@example.com', 'Confirm Signup', body)

        return render(...)
```

## Settings ⚙️

### `RAINCHECK_RUN_ASYNC`

`True` by default. Set to `False` to execute the jobs in the current thread as opposed to starting a new thread for each function.

NOTE: This is primarily for debugging purposes. When set to `False`, Django will wait for all scheduled functions to complete before closing the request, which can significantly increase response times.

### `RAINCHECK_IMMEDIATE`

`False` by default. Set to `True` to execute scheduled functions immediately when `schedule()` is called, rather than queuing them to run after the response is completed.

NOTE: When set to `True`, functions will execute synchronously during the request/response cycle.

## How does this work? ✨

1. `dj-raincheck` attaches a callback to the [`request_finished`](https://docs.djangoproject.com/en/stable/ref/signals/#django.core.signals.request_finished) signal provided by Django
2. Using the `@raincheck` decorator adds a `schedule` function to the original function
3. Calling `schedule()` queues the original function, args, and kwargs
4. When the current request is complete, `dj-raincheck` pops all scheduled functions from the queue and starts a new thread for each one

## Drawbacks 😢

`dj-raincheck` does not persist data to the disk or a database, so there are no guarantees if will be executed if the current request thread hangs or dies.

This is an explicit design trade-off to provide operational simplicity. `dj-raincheck` is useful for "fire-and-forget" tasks which, if they happen to fail, would be ok. If an application requires transactional guarantees, I recommend using [django-tasks](https://github.com/RealOrangeOne/django-tasks) instead.

## Supported Webservers 🕸️

- ✅ Django development server
- ✅ `gunicorn`
- 🤷 `uWSGI` (might require [enabling threads](https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html#a-note-on-python-threads))

Please make a PR for other production webservers with your findings.

## Inspiration 🙏

- Forked from [django-after-response](https://github.com/defrex/django-after-response)
