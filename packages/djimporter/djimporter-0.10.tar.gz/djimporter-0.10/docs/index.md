# Welcome to djimporter's documentation!

## Introduction
This app maps CSV files with django models to import related data into the database.

It supports the following use cases:
  1. Simple mapping between a one-to-one correspondence.
     In other words, a file corresponds to a django model
  2. Simple mapping with one or more Foreingkeys associated to the model
  3. Pre_save and post_save methods

## How to install it
To install the django-importer, follow the steps described on the [installation](installation.md) page.

## Usage

* [CsvModel](csvmodels.md)
  - [Simple Mapping](csvmodels.md#simple-mapping)
  - [Simple Mapping with ForeingKey](csvmodels.md#simple-mapping-with-a-foreingkey)
  - [FoeringKey with more than one column](csvmodels.md#foreingkey-con-m%C3%A1s-de-una-columna)
  - [Pre_save and Post_save](csvmodels.md#pre_save-and-post_save)
  - [One csv and two models](csvmodels.md#one-csv-two-models)
  - [Specials Fields](csvmodels.md#specials-fields)
* [How to use](howto.md)
  - [Initialize with context](howto.md#initialize-with-context)
  - [Validate](howto.md#validate)
  - [Save](howto.md#save)

## Deployment on production environments

* [Deployment](deployment.md)
  - [Install app](deployment.md#install-app)
  - [Supervisor](deployment.md#supervisor)
