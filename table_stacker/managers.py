from django.db import models
from django.template.defaultfilters import slugify


class TableManager(models.Manager):
    """
    A few tricks we'll use with our tables.
    """
    def live(self):
        """
        Returns only Tables that are ready to publish.
        """
        return self.filter(is_published=True, show_in_feeds=True)
    
    def update_or_create(self, yaml_data):
        """
        If the Table outlined by the provided YAML file exists, it's updated.
        
        If it doesn't, it's created.
        
        Returns a tuple with the object first, and then a boolean that is True
        when the object was created.
        """
        from table_stacker.models import Tag
        
        try:
            obj = self.get(slug=yaml_data.get("slug", yaml_data['yaml_name']))
        except self.model.DoesNotExist:
            obj = None
        
        if obj:
            obj.csv_name=yaml_data['file']
            obj.yaml_name=yaml_data['yaml_name']
            obj.yaml_data=str(yaml_data)
            obj.title=yaml_data['title']
            obj.slug=yaml_data.get("slug", yaml_data['yaml_name'])
            obj.kicker=yaml_data.get('kicker', '')
            obj.byline=yaml_data.get("byline", '')
            obj.publication_date=yaml_data['publication_date']
            obj.legend=yaml_data.get('legend', '')
            obj.description=yaml_data.get('description', '')
            obj.footer=yaml_data.get('footer', '')
            obj.sources=yaml_data.get('sources', '')
            obj.credits=yaml_data.get('credits', '')
            obj.is_published=yaml_data.get('is_published', False)
            obj.show_download_links=yaml_data.get("show_download_links", True)
            obj.show_in_feeds=yaml_data.get("show_in_feeds", True)
            obj.tags.clear()
            created = False
        else:
            obj = self.create(
                csv_name=yaml_data['file'],
                yaml_name=yaml_data['yaml_name'],
                yaml_data=str(yaml_data),
                title=yaml_data['title'],
                slug=yaml_data.get("slug", yaml_data['yaml_name']),
                kicker=yaml_data.get("kicker", ""),
                byline=yaml_data.get("byline", ""),
                publication_date=yaml_data['publication_date'],
                legend=yaml_data.get('legend', ''),
                description=yaml_data.get('description', ''),
                footer=yaml_data.get('footer', ''),
                sources=yaml_data.get('sources', ''),
                credits=yaml_data.get('credits', ''),
                is_published=yaml_data.get('is_published', False),
                show_download_links=yaml_data.get("show_download_links", True),
                show_in_feeds=yaml_data.get("show_in_feeds", True),
            )
            created = True
        [obj.tags.add(Tag.objects.get_or_create_by_name(i)[0])
            for i in yaml_data.get('tags', [])]
        obj.save()
        return obj, created


class TableLiveManager(models.Manager):
    """
    Returns only Tables that are ready to publish.
    """
    def get_query_set(self):
        qs = super(TableLiveManager, self).get_query_set()
        return qs.filter(is_published=True, show_in_feeds=True)


class TagManager(models.Manager):
    
    def get_or_create_by_name(self, name):
        """
        If the Tag outlined by the provided YAML file exists, it's return.
        
        If it doesn't, it's created.
        
        Returns a tuple with the object first, and then a boolean that is True
        when the object was created.
        """
        try:
            return self.get(slug=slugify(name)), False
        except self.model.DoesNotExist:
            return self.create(title=name, slug=slugify(name)), True



