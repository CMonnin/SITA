# sita-web

Flask web interface and batch CLI for [SITA](https://github.com/CMonnin/SITA)
natural-abundance correction of GC-MS mass distribution vectors.

## Install

```
pip install sita-web
```

## Run the web app

```
gunicorn "sita_web.app:create_app()"
```

See the [project repository](https://github.com/CMonnin/SITA) for details and
the underlying `sita-core` library.
