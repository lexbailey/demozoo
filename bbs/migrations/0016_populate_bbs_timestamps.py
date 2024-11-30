# Generated by Django 5.1 on 2024-11-30 20:57

from django.db import migrations


def populate_bbs_timestamps(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'contenttype')
    ct, created = ContentType.objects.get_or_create(model='bbs', app_label='bbs')
    BBS = apps.get_model('bbs', 'BBS')
    bbses = list(BBS.objects.raw("""
        select
        bbs_bbs.id, min(timestamp) AS first_edit, max(timestamp) AS last_edit
        from bbs_bbs
        inner join demoscene_edit on (
            (focus_content_type_id = %s and focus_object_id = bbs_bbs.id) or
            (focus2_content_type_id = %s and focus2_object_id = bbs_bbs.id)
        )
        group by bbs_bbs.id
    """, [ct.id, ct.id]))
    for bbs in bbses:
        bbs.created_at = bbs.first_edit
        bbs.updated_at = bbs.last_edit
        bbs.save()
    BBS.objects.bulk_update(bbses, ['created_at', 'updated_at'], batch_size=1000)


class Migration(migrations.Migration):

    dependencies = [
        ('bbs', '0015_bbs_timestamps'),
    ]

    operations = [
        migrations.RunPython(populate_bbs_timestamps, migrations.RunPython.noop),
    ]
