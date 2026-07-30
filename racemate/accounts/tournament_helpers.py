# accounts/tournament_helpers.py
"""
Small helpers that bridge the anonymous public Registration flow
with app_tournaments, which requires a real auth User for every
TournamentEntryPlayer.

Save this as accounts/tournament_helpers.py
"""

from django.contrib.auth.models import User


def get_or_create_user_for_registration(name, email):
    """
    Tournament entries require a real User (TournamentEntryPlayer.player FK),
    but public registration stays login-free. This transparently
    get_or_creates a User keyed on email, with an unusable password,
    so anonymous registrants can still be linked into TournamentEntryPlayer rows.

    Returns None if no email was provided (caller must handle that case —
    a TournamentEntryPlayer cannot be created without a User).

    NOTE: Django's User.email field is NOT unique by default. If two
    different people ever share an email this could match the wrong
    account, or raise MultipleObjectsReturned once duplicates exist.
    Flagged for a future migration (Phase 7) to add unique=True on email,
    or better: a dedicated OneToOne "PlayerProfile" instead of reusing
    the admin/login User model directly.
    """
    if not email:
        return None

    email = email.strip().lower()

    user = User.objects.filter(email__iexact=email).first()
    if user:
        return user

    first_name = ''
    if name:
        first_name = name.strip().split(' ')[0]

    # username must be unique; email is a safe default here since we
    # already confirmed no existing user has this email
    user = User(
        username=email,
        email=email,
        first_name=first_name,
    )
    user.set_unusable_password()
    user.save()
    return user