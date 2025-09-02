## OBytes Django Store App

[![Build & Test](https://github.com/obytes/ob-dj-store/workflows/Build%20&%20Test/badge.svg)](https://github.com/obytes/ob-dj-store/actions)
[![pypi](https://img.shields.io/pypi/v/ob-dj-store.svg)](https://pypi.python.org/pypi/ob-dj-store)
[![license](https://img.shields.io/badge/License-BSD%203%20Clause-green.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![downloads](https://pepy.tech/badge/ob-dj-store)](https://pepy.tech/project/ob-dj-store)
[![python](https://img.shields.io/pypi/pyversions/ob-dj-store.svg)](https://pypi.python.org/pypi/ob-dj-store)
[![docs](https://github.com/obytes/ob-dj-store/workflows/Docs/badge.svg)](https://github.com/obytes/ob-dj-store/blob/main/docs/source/index.rst)
[![health-check](https://snyk.io/advisor/python/ob-dj-store/badge.svg)](https://snyk.io/advisor/python/ob-dj-store)

OB-DJ-STORE is a Django application for managing ecommerce stores.

## Quick start

* This package requires running the PostGis GeoSpatial database for your Django project, check [GeoDjango](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/) for references.

1. Install `ob_dj_store` latest version `pip install ob-dj-store`

2. Add "ob_dj_store" to your `INSTALLED_APPS` setting like this:

```python
   # settings.py
   INSTALLED_APPS = [
        ...
        "ob_dj_store.core.stores",
        "ob_dj_store.core.stores.gateway.tap",
   ]
```

1. Include "ob_dj_store" URLs to your project's `urls.py` file like the following:

```python
   # urls.py
   urlpatterns = [
        ...
        path('ob-dj-store/', include('ob_dj_store.apis.stores.urls')),
   ]
```


## Configuration

No additional configuration is required (yet).

## Developer Guide

1. Clone github repo `git clone [url]`

2. `pipenv install --dev`

3. `pre-commit install`

4. Run unit tests `pytest`


