# from django.apps import AppConfig


# class AccountsConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'accounts'

# racemate/accounts/apps.py
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'racemate.accounts'   # ← THIS LINE WAS WRONG BEFORE