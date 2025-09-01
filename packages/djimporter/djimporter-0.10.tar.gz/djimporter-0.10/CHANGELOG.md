# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## main

## [0.10.0] - 2025-09-01
- [added] #66 Added progress to importer tasks

## [0.9.0] - 2025-04-09
- [added] #65 Added update method set_extra_fields 

## [0.8.0] - 2024-12-16
- [added] #64 Added help_text field for field mapper importer view

## [0.7.0] - 2024-07-18
- [added] #61 Group by error type and message to show a brief summary in importlog
- [added] #57 Allow partial imports

## [0.6.0] - 2024-05-02
- [fixed] #59 Django 4.0 compatibility

## [0.5.0] - 2024-02-27
- [added] #53 Implement CSV guesser to allow dynamic column mapping using JS.
- [changed] #58 Allow null values on SlugRelatedField.
- [fixed] #56 Handle too long values of ImportLog.user.

## [0.4.0] - 2022-07-06
- [added] #48 CachedSlugRelatedField: optimize DB queries (1 big vs N small)
- [fixed] #49 CachedSlugRelatedField produces cross dependencies
- [fixed] #51 Build setup config.

## [0.3.0] - 2021-11-28
- [added] `log` attribute to CSV models.
- [added] Implement append mode. If enabled, existing objects will be ignored.
- [fixed] #14 Detect CSV file encoding.
- [fixed] #43 Handle unexpected errors.

## [0.2.0] - 2021-05-26
- [changed] Show human-friendly error messages.
- [changed] Optimize speed.

## [0.1.0] - 2021-05-10
- [added] Support passing delimiter and headers mapping as parameters.

## [0.0.1] - 2021-03-15
- First beta release.
