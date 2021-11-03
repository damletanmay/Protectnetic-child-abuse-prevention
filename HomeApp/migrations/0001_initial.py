# Generated by Django 3.2.8 on 2021-11-03 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('link', models.TextField()),
                ('csrfmiddlewaretoken', models.TextField()),
                ('img_1', models.ImageField(upload_to='report_images')),
                ('img_2', models.ImageField(upload_to='report_images')),
                ('result', models.BooleanField(default=False)),
            ],
        ),
    ]
