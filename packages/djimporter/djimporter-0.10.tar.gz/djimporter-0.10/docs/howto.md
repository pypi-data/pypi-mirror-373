# How to use
Here we want to basically explain how our csvmodel is used

## Initialize with context
To initialize our csvmodel class we just have to add the path where our file is or add the io object.

```
album_csv = AlbumCsv(path_to_csv)
```

### Context
Sometimes we have to pass some data to initialize our csv objects.
For example. Imagine we have a django model like this:

```
class Musician(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    instrument = models.CharField(max_length=100)

class Album(models.Model):
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    num_stars = models.IntegerField()
```

Our csv data in a file are like this:

```
release_date;num_stars;name
2000-01-01;5;aaa
2001-01-01;4;bbb
```

Imagine that we want to introduce this csv file to an artist that we already know, so we would use the context variable to initialize our CsvModel class like so:

```
artist = Musician.objects.get(name='Wolf')
album_csv = AlbumCsv(path_to_csv, context={'artist': artist})
```
For this to work properly we need to define our CsvModel like so:

```
class AlbumCsv(importers.CsvModel):

    class Meta:
        pre_save = ['get_musician']
        delimiter = ';'
        dbModel = Album
        fields = ['name', 'release_date', 'num_stars']

        @classmethod
        def get_musician(cls, readrow):
            obj = readrow.object
            obj.artist = cls.context['artist']
```

Notice that we use **cls.context** to access the context variable passed when we initialize AlbumCsv.

## Validate
Once our CsvModel has been initialized, we can validate the reading of the file with:

```
album.is_valid()
```

This will read the file and will look for possible errors. If there are errors, it will return a list of the errors found.
We can access this list from **album.errors** whenever we want.
If there are no errors it will not return anything. But it creates a list of the objects that are not yet saved. To access this list we can see it in **album.list_objs**

## Save
If we want to save this objects list in the data base we need exec:
```
album.save()
```
