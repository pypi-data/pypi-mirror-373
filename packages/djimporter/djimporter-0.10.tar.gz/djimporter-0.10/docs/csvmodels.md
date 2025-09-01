# CsvModel

The cornerstone of this application is defining a class that will help the application understand the mapping between django models and the csv file.

It consists of a class that inherits from the CsvModel class.


```
from djimporter import importers

class MyModelCsv(importers.CsvModel):
    pass
```


Suppose we have this simple django model:

## Simple mapping
We call those maps that are built from the relationship between a csv file and a simple django model, a simple mapping
Now we are going to define this case with an example

Suppose we have this simple django model:

```
from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
```

and we want to map it with a file with this content:

```
last_name;name
Schmith;Susan
Wolf;Johan
```

We will present an example and then define each of its parts.
We define a csvmodel class like so:

```
from myModel import Person
from djimporter import importers, fields

class MyPersonCsv(importers.CsvModel):
    name = fields.CharField(match='first_name')

    class Meta:
        delimiter = ';'
        dbModel = Person
        fields = ['name', 'last_name']
```

What we first see is a Meta class inside our MyPersonCsv class.
This Meta class is the basis for defining the relationship between the django models and the file.
In it we see:
- **delimiter** which is a variable in which we will define what symbol we will use to delimit the columns of our csv file
- **dbModel** is the django model to which we are going to associate the csv file
- **fields** is the definition of the columns that must appear in the csv file. Order is not important

We will now look at the ** name ** definition of our MyPersonCsv class:

```
name = fields.CharField(match='first_name')
```
This line makes a mapping between **name**, which is a column name that must appear in the csv file, and **first_name** which is the field of the model to which we are going to associate the column data.

As you can see **last_name** appears in fields but is not defined in MyPersonCsv.
This indicates that the name that should appear in the file is the same as the one that appears defined in the django model, so we will not need a mapping definition. Instead if we are going to need to tell the MyPersonCsv class that this column must exist

The next point to highlight is that we have not defined anything for **last_name**, it only appears in the fields list. If the csv column name and the model name is the same, we do not need to define anything else. We want to warn that if a model field is not defined in the **fields** variable, then it will take what appears in the **default** variable that we have described in our model.


## Simple mapping with a ForeingKey
A simple mapping with a ForeingKey requires that the object to which we are going to relate using the ForeingKey already exists.
In many cases the ForeignKey is a value that depends on each installation of a database and is usually different depending on each particular case.
It is for this reason that it is not advisable to map the value of the ForeinKey itself. We need to find the object by other values that make it unique, (like a slug).
The example we propose for this case is as follows:

Assuming we have the following django models:

```
from django.db import models


class Musician(models.Model):
    name = models.CharField(max_length=50, unique=True)
    instrument = models.CharField(max_length=100)


class Album(models.Model):
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    num_stars = models.IntegerField()
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
```

Our csv data in a file are like this:


```
name;artist;release_date;num_stars
aaa;Susan Schmith;2000-01-01;5
bbb;Johan Wolf;2001-01-01;4
```

In this case we will define our csvmodel in this way:

```
class AlbumCsv(importers.CsvModel):
    artist = fields.SlugRelatedField(slug_field="name", queryset=Musician.objects.all())

    class Meta:
        delimiter = ';'
        dbModel = Album
        fields = ['name', 'release_date', 'num_stars', 'artist']
```

Here we see that the field **SlugRelatedField** allows us to find the object through the
field **slug_field**.
**NOTE**: field defined as `slug_field` must be unique.


### CachedSlugRelatedField
Similar usage than `SlugRelatedField` but caching queryset in **memory** to optimize performance.
On the previous example just replace `SlugRelatedField` with `CachedSlugRelatedField`.


## ForeignKey with more than one column:
There are some cases where we need to find an object that will be a ForeingKey of our Django model.
But to do that we need more than one slug. This means that we must relate several columns
csv with an object. For this we have a Field called **MultiSlugRelatedField**
Let's see an example:
Our csv data is as follows:

```
first_name;surname;release_date;num_stars;name
Susan;Schmith;2000-01-01;5;aaa
Wolf;Schmith;2001-01-01;4;bbb
```
In this csv we have to find an Artist from the first_name and surname columns.
For this we will use a definition of CsvModel like this:

```
class AlbumCsv(importers.CsvModel):
    artist = fields.MultiSlugRelatedField(
        matchs={"first_name": "musician__first_name", "surname": "musician__last_name"}
    )

    class Meta:
        delimiter = ';'
        dbModel = Album
        fields = ['name', 'release_date', 'num_stars']
        extra_fields = ['first_name', 'surname']
```
The variable **extra_fields** of the class **Meta** allows us to define names that must appear in any of the csv columns that we will then use to find the **artist** object, but we do not use it for direct mapping.


## pre_save and post_save.
Sometimes we need to modify the data before or after saving it.
Other times we must execute a process independent of the model if the data has a particular characteristic.
For most complex examples we will use **pre_save** or **post_save**.

In this case we will define our ForeignKey using a **pre_save** in csvmodel like this:
```
class AlbumCsv(importers.CsvModel):

    class Meta:
        pre_save = ['get_musician']
        delimiter = ';'
        dbModel = Album
        fields = ['name', 'release_date', 'num_stars']
        extra_fields = ['first_name', 'surname']

        @classmethod
        def get_musician(cls, readrow):
            obj = readrow.object
            first_name = readrow.line['first_name']
            surname = readrow.line['surname']
            musician = Musician.objects.get(first_name=first_name, last_name=surname)
            obj.artist = musician
```

As we can see we do not have any defined field.
As we have indicated before, this is so because all the fields of the model have the same name as the columns of our csv file.

The next thing we want to highlight is the definition of the variable **pre_save** that appears in the **Meta** subclass.
**pre_save** is a list of methods of the Meta class that are executed before writing the object to the database. This allows us to define a method where we can capture the object to which we are going to relate.

As we see, the Album object is already created when these **pre_save** functions are executed. It appears to us as **readrow.object**.

The variable in the **extra_fields** class allows us to define names that must appear in any of the csv columns that we will later use in one of the **pre_save** or **post_save** methods.
In this case **first_name** and **surname** columns from our csv and we will use them to be able to capture the musician object and thus associate it with our new object in **obj.artist**.

## One csv two models
We can also use a pre_save or post_save to save from a single csv in two django models.
Until now we have assumed that the artist object was in the database. Now let's assume that it not exist in our data base and that the csv file brings it to us.
Suppose we have the following csv file:

```
first_name;surname;instrument;release_date;num_stars;name
Susan;Schmith;guitar;2000-01-01;5;aaa
Wolf;Schmith;violin;2001-01-01;4;bbb
```

We could define a CsvModel like so:
```
class AlbumCsv(importers.CsvModel):

    class Meta:
        pre_save = ['set_musician']
        delimiter = ';'
        dbModel = Album
        fields = ['name', 'release_date', 'num_stars']
        extra_fields = ['first_name', 'surname']

        @classmethod
        def set_musician(cls, readrow):
            obj = readrow.object
            first_name = readrow.line['first_name']
            surname = readrow.line['surname']
            instrument = readrow.line['instrument']
            musician = Musician.objects.create(
                first_name=first_name, last_name=surname, instrument=instrument
            )
            obj.artist = musician
```

# Specials Fields
## DateField
DateField allows us to go from a text format to a date format. It has a variable that allows us to define how it will be formatted. This variable is called DEFAULT_DATE_FORMAT and we can modify it when we initialize the DateField class using the var 'strptime'

```
f = DateField(strptime='%d-%m%Y')
```

The default value of DEFAULT_DATE_FORMAT is
```
f = DateField()
f.DEFAULT_DATE_FORMAT == '%Y-%m-%d'
```

## DefaultField
We use this field for override all values in csv
For example if we have:

```
f = DefaultField(1, match='count')
```

this mean than when we have a csv file with a 'count' in one column of that file, then all registers is saved with the value '1' This is usefull when we want put as a reset one value and it's is diferent of the default value of the database.

