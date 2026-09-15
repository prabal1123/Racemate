import uuid
from django.db import migrations


def populate_uuids(apps, schema_editor):
    TournamentCategory = apps.get_model('app_tournaments', 'TournamentCategory')
    for category in TournamentCategory.objects.filter(uuid__isnull=True):
        category.uuid = uuid.uuid4()
        category.save(update_fields=['uuid'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('app_tournaments', '0013_tournamentcategory_uuid'),
    ]

    operations = [
        migrations.RunPython(populate_uuids, noop_reverse),
    ]
