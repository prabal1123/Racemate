import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_tournaments', '0012_tournamentcategory_fixture_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentcategory',
            name='uuid',
            field=models.UUIDField(null=True, editable=False, blank=True),
        ),
    ]
