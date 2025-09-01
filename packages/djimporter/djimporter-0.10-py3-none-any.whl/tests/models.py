from django.db import models


class DJImporterModel(models.Model):
    """
    Base for test models that sets app_label, so they play nicely.
    """

    class Meta:
        app_label = 'tests'
        abstract = True


class ForeignKeyTarget(DJImporterModel):
    name = models.CharField(max_length=100)


class ForeignKeySource(DJImporterModel):
    name = models.CharField(max_length=100)
    target = models.ForeignKey(ForeignKeyTarget, related_name='sources',
                               help_text='Target', verbose_name='Target',
                               on_delete=models.CASCADE)


class Musician(models.Model):
    name = models.CharField(max_length=50, unique=True)
    instrument = models.CharField(max_length=100)


class Album(models.Model):
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    num_stars = models.IntegerField()
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)


class Song(models.Model):
    name = models.CharField(max_length=100)
    album = models.ForeignKey(Album, null=True, on_delete=models.SET_NULL)
