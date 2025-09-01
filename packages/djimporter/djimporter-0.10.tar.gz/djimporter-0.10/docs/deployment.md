# Deployment

## Install app
To perform the deployment, it is necessary to add the application, in the INSTALLED_APPS section of the settings.py of our project.
This app depend and use an other django app, **django-background-tasks**.
You need to install it before **djimporter**

For start this app manualy you need to exec:
```
python manager process_tasks
```

## Supervisor
For run this process in background you need to add a package to your system called **supervisor**.
In Debian it would be like this:
```
apt-get install supervisor
```
Then the file is copied:

```
cp docs/config/supervisord.conf
/etc/supervisor/supervisord.conf
```

In this file you have to change ```command=``` setting your virtualenv path and your project path.

