# file: backend/accounts/migrations/0002_remove_donation_amount_remove_donation_donor_name_and_more.py
# (or 0003_... - paste same content into both files)

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # No-op migration: the schema changes referenced earlier were already
        # applied/removed manually or differ in the DB. Keeping a no-op file
        # prevents Django from attempting to drop columns that don't exist.
    ]
