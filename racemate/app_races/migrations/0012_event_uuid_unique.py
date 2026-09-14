import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_races', '0011_populate_event_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='uuid',
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text="Public identifier used in this event's shareable registration link.",
            ),
        ),
    ]
