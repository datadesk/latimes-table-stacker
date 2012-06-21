# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Table.publication_time'
        db.add_column('table_stacker_table', 'publication_time',
                      self.gf('django.db.models.fields.TimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Table.publication_time'
        db.delete_column('table_stacker_table', 'publication_time')


    models = {
        'table_stacker.table': {
            'Meta': {'ordering': "('-publication_date',)", 'object_name': 'Table'},
            'byline': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'credits': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'csv_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'kicker': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'legend': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.DateField', [], {}),
            'publication_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'show_download_links': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_in_feeds': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_search_field': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'sources': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'yaml_data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'yaml_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['table_stacker']