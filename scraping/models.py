from django.db import models

# Create your models here.
class Google_Patent(models.Model):
    title = models.CharField(max_length = 250, blank = True, null = True)
    patent_num = models.CharField(max_length = 250, blank = True, null = True)
    abstract = models.TextField(blank = True, null = True)
    classification = models.TextField(blank = True, null = True)
    claims = models.TextField(blank = True, null = True)
    images = models.JSONField(blank = True, null = True)
    description = models.TextField(blank = True, null = True)
    background = models.TextField(blank = True, null = True)
    summary = models.TextField(blank = True, null = True)
    tech_field = models.TextField(blank = True, null = True)
    drawing = models.TextField(blank = True, null = True)
    detail_desc = models.TextField(blank = True, null = True)

    class Meta:
        db_table = 'google_patent'
        verbose_name = 'google_patent'
        verbose_name_plural = 'google_patents'