# Generated by Django 4.2.6 on 2023-10-30 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_remove_course_student_numberofquestion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='course',
        ),
    ]
