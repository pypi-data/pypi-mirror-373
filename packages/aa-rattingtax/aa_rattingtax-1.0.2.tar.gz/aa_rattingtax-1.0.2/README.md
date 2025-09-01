# Ratting Tax App for Alliance Auth (GitHub Version)<a name="rattingtax-plugin-app-for-alliance-auth-github-version"></a>

This is an rattingtax plugin app for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth)
(AA)
______________________________________________________________________

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=1 -->

- [Ratting Tax App for Alliance Auth (GitHub Version)](#rattingtax-plugin-app-for-alliance-auth-github-version)
  - [Features](#features)
  - [How to Use It](#how-to-use-it)
  - [Installing Into Your Website](#installing-into-your-website)
<!-- mdformat-toc end -->

______________________________________________________________________

## Features<a name="features"></a>

- Plugin calculates ratting tax for all corporations in the alliance

## How to Use It<a name="how-to-use-it"></a>

Set basic permissions for corp ceos and for alliance leadership view_all permission so they can see all the corps

## Installing Into Your Website<a name="installing-into-your-website"></a>

Make sure you're in your venv. Then install it with pip:

```bash
pip install aa-rattingtax
```

First add your app to the Django project by adding `rattingtax` to
INSTALLED_APPS in `settings/local.py`.

Next, run migrations:.

```bash
python manage.py migrate
```

Add celery schedule at the bottom of your `local.py` setting file

```bash
CELERYBEAT_SCHEDULE["rattingtax_pull_current"] = {
    "task": "rattingtax.tasks.pull_current_month_all",
    "schedule": crontab(minute=15, hour="2"),
}
CELERYBEAT_SCHEDULE["rattingtax_close_month"] = {
    "task": "rattingtax.tasks.close_previous_months",
    "schedule": crontab(minute=5, hour=1, day_of_month="1"),
}
```

Finally, restart your AA server and that's it.