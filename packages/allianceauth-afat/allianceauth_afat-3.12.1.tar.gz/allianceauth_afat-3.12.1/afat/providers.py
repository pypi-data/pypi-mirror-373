"""
Providers
"""

# Alliance Auth
from esi.clients import EsiClientProvider

# Alliance Auth AFAT
from afat import __app_name_useragent__, __github_url__, __version__

# ESI client
esi = EsiClientProvider(
    ua_appname=__app_name_useragent__, ua_version=__version__, ua_url=__github_url__
)
