import uuid
from django.db import migrations


def populate_uuids(apps, schema_editor):
    Event = apps.get_model('app_races', 'Event')
    for event in Event.objects.filter(uuid__isnull=True):
        event.uuid = uuid.uuid4()
        event.save(update_fields=['uuid'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('app_races', '0010_event_uuid'),
    ]

    operations = [
        migrations.RunPython(populate_uuids, noop_reverse),
    ]
