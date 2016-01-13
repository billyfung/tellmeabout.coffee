tellmeabout.coffee
---

Flask + App Engine + NDB

### To start locally

1. git clone this project
2. Download the [Google App Engine SDK](https://cloud.google.com/appengine/downloads?hl=en) for python
3. Create a virtualenv (2.7 python) and `pip install -r requirements -t lib`
4. Add a new project in the Google App Engine Launcher
    - name: tellmeaboutcoffee
    - path: whereever you git cloned
5. Run using the Launcher and verify!

### Adding external packages
```
pip install <package_name> -t lib/
```
