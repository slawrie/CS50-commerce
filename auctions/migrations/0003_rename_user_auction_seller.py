# Generated by Django 3.2.5 on 2022-05-02 13:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auction_bid_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auction',
            old_name='user',
            new_name='seller',
        ),
    ]
