========
sitewide
========

Sitewide is a Django app that helps web app/site developers focus on the main contents of their projects by automating the creation of headers, sidebars and footers. It aims to reduce the routine adaptation of snippets when starting new projects. The developer only needs to introduce the latest information for the repeating page layouts via a YAML file. Although Sitewide operates as a middleware, users can alter its settings via the response context data. Sitewide is the product of a Python hobbyist and is currently in the pre-alpha stage. 

Quick start
-----------

1. Add "sitewide" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "sitewide",
    ]

2. Include the sitewide URLconf in your project urls.py like this::

    path("", include("sitewide.urls")),

3. Add "sitewide.middleware.connect.SitewideMiddleware" to the MIDDLEWARE list in your project setting after the stock middleware entries::

    MIDDLEWARE = [
        ...,
        "sitewide.middleware.connect.SitewideMiddleware",
    ]

4. Run ``python manage.py migrate`` to create the model for sitewide settings. In the future, Sitewide will use the model for performing word replacements depending on the context of your project.

5. Start the web service on your local development machine::
    
    ./manage.py runserver

6. Open a web browser on the same machine and browse to ``http://localhost:8000/``

7. If every goes well, you should see a page saying "Sitewide is Working!"
