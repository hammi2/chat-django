# Generated by Django 4.1.7 on 2023-02-16 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0016_alter_message_receiver_alter_message_seen_by_users_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendrequest',
            name='message',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
    ]
