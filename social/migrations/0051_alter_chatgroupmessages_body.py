from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0050_chatgroupmessages_deleted_for_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatgroupmessages",
            name="body",
            field=models.TextField(blank=True, null=True),
        ),
    ]
