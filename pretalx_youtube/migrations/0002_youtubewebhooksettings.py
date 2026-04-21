import django.db.models.deletion
from django.db import migrations, models

import pretalx_youtube.models


class Migration(migrations.Migration):
    dependencies = [("event", "0001_initial"), ("pretalx_youtube", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="YouTubeWebhookSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "token",
                    models.CharField(
                        default=pretalx_youtube.models.generate_webhook_token,
                        max_length=128,
                    ),
                ),
                (
                    "event",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="youtube_webhook_settings",
                        to="event.event",
                    ),
                ),
            ],
        )
    ]
