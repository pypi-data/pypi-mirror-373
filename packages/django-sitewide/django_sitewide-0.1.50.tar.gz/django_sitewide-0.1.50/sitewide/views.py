"""Sitewide Default View Classes"""

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Sitewide's Home View"""

    template_name = "sitewide/home.html"
    extra_context = {"sitewide": {"titles": {"sub": "Optional Subtitle"}}}
