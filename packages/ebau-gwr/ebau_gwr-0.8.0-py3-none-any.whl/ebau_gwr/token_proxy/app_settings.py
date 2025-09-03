from django.conf import settings

base = (
    "https://www.housing-stat.ch"
    if settings.ENV == "production"
    else "https://www-r.housing-stat.ch"
)

DEFAULTS = {"GWR_HOUSING_STAT_BASE_URI": f"{base}/regbl/api/ech0216/2"}

REQUIRED_SETTINGS = ("GWR_FERNET_KEY", "GWR_HOUSING_STAT_WSK_ID")
