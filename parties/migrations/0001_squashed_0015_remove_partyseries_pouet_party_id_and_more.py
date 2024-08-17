# Generated by Django 5.0.8 on 2024-08-17 13:20

import django.contrib.postgres.indexes
import django.contrib.postgres.search
import django.core.files.storage
import django.db.migrations.operations.special
import django.db.models.deletion
import parties.models
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('parties', '0001_initial'), ('parties', '0002_auto_20170220_1950'), ('parties', '0003_increase_link_length'), ('parties', '0004_set_on_delete'), ('parties', '0005_party_share_image'), ('parties', '0004_add_party_search_index'), ('parties', '0005_party_search_title'), ('parties', '0006_merge_20180419_0025'), ('parties', '0007_search_document_noneditable'), ('parties', '0008_py3_strings'), ('parties', '0009_organiser'), ('parties', '0010_party_is_cancelled'), ('parties', '0011_remove_party_woe_id'), ('parties', '0012_delete_partyseriesdemozoo0reference'), ('parties', '0013_partyseriesexternallink'), ('parties', '0014_populate_party_series_external_links'), ('parties', '0015_remove_partyseries_pouet_party_id_and_more')]

    initial = True

    dependencies = [
        ('demoscene', '0017_membership_group_limit_choices'),
        ('platforms', '0001_initial'),
        ('productions', '0001_initial'),
        ('productions', '0006_remove_production_default_screenshot'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('shown_date_date', models.DateField(blank=True, null=True)),
                ('shown_date_precision', models.CharField(blank=True, choices=[(b'd', b'Day'), (b'm', b'Month'), (b'y', b'Year')], max_length=1)),
            ],
            options={
                'ordering': ('party__name', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Party',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('tagline', models.CharField(blank=True, max_length=255)),
                ('start_date_date', models.DateField()),
                ('start_date_precision', models.CharField(choices=[(b'd', b'Day'), (b'm', b'Month'), (b'y', b'Year')], max_length=1)),
                ('end_date_date', models.DateField()),
                ('end_date_precision', models.CharField(choices=[(b'd', b'Day'), (b'm', b'Month'), (b'y', b'Year')], max_length=1)),
                ('is_online', models.BooleanField(default=False)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('country_code', models.CharField(blank=True, max_length=5)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('woe_id', models.BigIntegerField(blank=True, null=True)),
                ('geonames_id', models.BigIntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('website', models.URLField(blank=True)),
                ('sceneorg_compofolders_done', models.BooleanField(default=False, help_text=b'Indicates that all compos at this party have been matched up with the corresponding scene.org directory')),
                ('invitations', models.ManyToManyField(blank=True, related_name='invitation_parties', to='productions.production')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Parties',
            },
        ),
        migrations.CreateModel(
            name='PartySeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('notes', models.TextField(blank=True)),
                ('website', models.URLField(blank=True)),
                ('twitter_username', models.CharField(blank=True, max_length=30)),
                ('pouet_party_id', models.IntegerField(blank=True, null=True, verbose_name=b'Pouet party ID')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Party series',
            },
        ),
        migrations.CreateModel(
            name='PartySeriesDemozoo0Reference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('demozoo0_id', models.IntegerField(blank=True, null=True, verbose_name=b'Demozoo v0 ID')),
                ('party_series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demozoo0_ids', to='parties.partyseries')),
            ],
        ),
        migrations.CreateModel(
            name='ResultsFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(blank=True, max_length=255)),
                ('file', models.FileField(blank=True, storage=django.core.files.storage.FileSystemStorage(), upload_to=b'results')),
                ('filesize', models.IntegerField()),
                ('sha1', models.CharField(max_length=40)),
                ('encoding', models.CharField(blank=True, max_length=32, null=True)),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results_files', to='parties.party')),
            ],
        ),
        migrations.AddField(
            model_name='party',
            name='party_series',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parties', to='parties.partyseries'),
        ),
        migrations.AddField(
            model_name='party',
            name='releases',
            field=models.ManyToManyField(blank=True, related_name='release_parties', to='productions.production'),
        ),
        migrations.CreateModel(
            name='CompetitionPlacing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ranking', models.CharField(blank=True, max_length=32)),
                ('position', models.IntegerField()),
                ('score', models.CharField(blank=True, max_length=32)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='placings', to='parties.competition')),
                ('production', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='competition_placings', to='productions.production')),
            ],
        ),
        migrations.AddField(
            model_name='competition',
            name='party',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='competitions', to='parties.party'),
        ),
        migrations.CreateModel(
            name='PartyExternalLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link_class', models.CharField(max_length=100)),
                ('parameter', models.CharField(max_length=4096)),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='external_links', to='parties.party')),
            ],
            options={
                'ordering': ['link_class'],
                'unique_together': {('link_class', 'parameter', 'party')},
            },
        ),
        migrations.AddField(
            model_name='competition',
            name='platform',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='platforms.platform'),
        ),
        migrations.AddField(
            model_name='competition',
            name='production_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='productions.productiontype'),
        ),
        migrations.AddField(
            model_name='party',
            name='share_image_file',
            field=models.ImageField(blank=True, height_field=b'share_image_file_height', help_text=b'Upload an image file to display when sharing this party page on social media', upload_to=parties.models.party_share_image_upload_to, width_field=b'share_image_file_width'),
        ),
        migrations.AddField(
            model_name='party',
            name='share_image_file_height',
            field=models.IntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='party',
            name='share_image_file_url',
            field=models.CharField(blank=True, editable=False, max_length=255),
        ),
        migrations.AddField(
            model_name='party',
            name='share_image_file_width',
            field=models.IntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='party',
            name='share_screenshot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='productions.screenshot'),
        ),
        migrations.AddField(
            model_name='party',
            name='search_document',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddIndex(
            model_name='party',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_document'], name='parties_par_search__4220e5_gin'),
        ),
        migrations.AddField(
            model_name='party',
            name='search_title',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='party',
            name='search_document',
            field=django.contrib.postgres.search.SearchVectorField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='competition',
            name='shown_date_precision',
            field=models.CharField(blank=True, choices=[('d', 'Day'), ('m', 'Month'), ('y', 'Year')], max_length=1),
        ),
        migrations.AlterField(
            model_name='party',
            name='end_date_precision',
            field=models.CharField(choices=[('d', 'Day'), ('m', 'Month'), ('y', 'Year')], max_length=1),
        ),
        migrations.AlterField(
            model_name='party',
            name='sceneorg_compofolders_done',
            field=models.BooleanField(default=False, help_text='Indicates that all compos at this party have been matched up with the corresponding scene.org directory'),
        ),
        migrations.AlterField(
            model_name='party',
            name='share_image_file',
            field=models.ImageField(blank=True, height_field='share_image_file_height', help_text='Upload an image file to display when sharing this party page on social media', upload_to=parties.models.party_share_image_upload_to, width_field='share_image_file_width'),
        ),
        migrations.AlterField(
            model_name='party',
            name='start_date_precision',
            field=models.CharField(choices=[('d', 'Day'), ('m', 'Month'), ('y', 'Year')], max_length=1),
        ),
        migrations.AlterField(
            model_name='partyseries',
            name='pouet_party_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Pouet party ID'),
        ),
        migrations.AlterField(
            model_name='partyseriesdemozoo0reference',
            name='demozoo0_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Demozoo v0 ID'),
        ),
        migrations.AlterField(
            model_name='resultsfile',
            name='file',
            field=models.FileField(blank=True, storage=django.core.files.storage.FileSystemStorage(), upload_to='results'),
        ),
        migrations.CreateModel(
            name='Organiser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(blank=True, max_length=50)),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organisers', to='parties.party')),
                ('releaser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parties_organised', to='demoscene.releaser')),
            ],
        ),
        migrations.AddField(
            model_name='party',
            name='is_cancelled',
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveField(
            model_name='party',
            name='woe_id',
        ),
        migrations.DeleteModel(
            name='PartySeriesDemozoo0Reference',
        ),
        migrations.CreateModel(
            name='PartySeriesExternalLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link_class', models.CharField(max_length=100)),
                ('parameter', models.CharField(max_length=4096)),
                ('party_series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='external_links', to='parties.partyseries')),
            ],
            options={
                'ordering': ['link_class'],
                'unique_together': {('link_class', 'parameter', 'party_series')},
            },
        ),
        migrations.RemoveField(
            model_name='partyseries',
            name='pouet_party_id',
        ),
        migrations.RemoveField(
            model_name='partyseries',
            name='twitter_username',
        ),
    ]