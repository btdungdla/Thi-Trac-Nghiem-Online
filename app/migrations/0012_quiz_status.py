# Generated by Django 4.2.6 on 2023-10-20 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_quizresult_quiz'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
