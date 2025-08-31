"""Sitewide Middleware Implementation"""

from pathlib import Path
import yaml
from django.conf import settings
from sitewide.middleware.parts import Sitewide


def set_logo(conf, path) -> dict:
    """Set path to logo in Sitewide configuration dict"""

    if "logo" not in conf:
        conf.setdefault("logo", {"path": path})
    else:
        conf["logo"]["path"] = path
    return conf


def sitelogo(confyaml) -> dict:
    """Prefer on-premise site Logo in Sitewide project folder or settings over
    developer's default provision."""

    if (
        (Path(settings.BASE_DIR) / "static/imgs/sitelogo.png")
        .resolve()
        .exists()
    ):
        return set_logo(confyaml, "imgs/sitelogo.png")
    if hasattr(settings, "SITEWIDE_LOGO"):
        return set_logo(confyaml, str(getattr(settings, "SITEWIDE_LOGO")))
    return confyaml


def get_config() -> dict:
    """get_config() -> dict
    Read configuration from sitewide.yaml in the project folder.
    If one doesn't exist, load defaults"""

    projyaml = (Path(settings.BASE_DIR) / "sitewide.yaml").resolve()
    confyaml = (
        projyaml
        if projyaml.exists()
        else (Path(__file__).parent / "sitewide.yaml").resolve()
    )
    with open(confyaml, "rb") as file:
        return sitelogo(yaml.safe_load(file))


class SitewideMiddleware:
    """Django Bridge/connection for Sitewide"""

    def __init__(self, get_response):
        """One-time configuration and initialization."""

        self.get_response = get_response
        self.sitewide = Sitewide(**get_config())

    def __call__(self, request):
        """Middleware caller"""

        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response

    def process_template_response(self, request, response):
        """Get, Update and inject Sitewide instance back to context_data"""

        changes = response.context_data.get("sitewide", {})
        changes.update({"user": request.user})
        self.sitewide.apply(**changes)
        response.context_data["sitewide"] = self.sitewide
        return response
