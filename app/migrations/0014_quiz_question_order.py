# Generated by Django 4.2.6 on 2023-10-20 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_rename_status_quiz_finish'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='question_order',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
