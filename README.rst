Youtube integration
===================

.. image:: https://img.shields.io/pypi/v/pretalx-youtube.svg
   :target: https://pypi.org/project/pretalx-youtube/
   :alt: PyPI version

This is a plugin for `pretalx`_ that provides an integration with Youtube, allowing you to embed recordings on talk pages.

.. image:: https://github.com/pretalx/pretalx-youtube/blob/main/assets/screenshot.png?raw=true

API
---

Reading data
~~~~~~~~~~~~

The Plugin supplies an API at ``/api/events/<event>/p/youtube/`` that returns all configured Youtube URLs:

.. code:: json

   {
       "count": 1,
       "next": null,
       "previous": null,
       "results": [
           {
               "submission": "DPC6RT",
               "youtube_link": "https://youtube.com/watch?v=AAAAAB",
               "video_id": "AAAAAB"
           },
       ]
   }

A detail view for specific submissions is available at ``/api/events/<event>/p/youtube/<code>/``:

.. code:: json

   {
       "submission": "DPC6RT",
       "youtube_link": "https://youtube.com/watch?v=AAAAAB",
       "video_id": "AAAAAB"
   }

Writing data
~~~~~~~~~~~~

You can use ``POST`` requests against the list endpoint and ``PATCH`` or ``PUT`` requests against the detail endpoint to
create or update Youtube links. The ``video_id`` field is required, as is the ``submission`` field unless you are using
``PATCH``. The ``submission`` field must be the code of an existing submission, and the API will take care of updating
existing links if you use ``POST``, so it's safe to just always ``POST`` to the list endpoint.

You can also **bulk import** data in either JSON or CSV format. The JSON format is the same as the one used by the API,
and the CSV format is a simple CSV file with a header row containing the fields ``submission`` and ``video_id``. You can
upload the file to ``/api/events/<event>/p/youtube/import/`` using a ``POST`` request with the file as the body.
(For JSON, you can also instead put the data in the request body.)


c3voc publishing webhook
------------------------

If you use the c3voc ``voctopublish`` tool to upload recordings to YouTube,
the plugin can receive the publishing notification and attach the YouTube
link to the matching session automatically.

Go to the plugin's settings page in the organiser backend to find the
webhook URL and a freshly-generated token. In your voctopublish ticket,
configure the webhook URL and set the webhook *password* (``webhook_pass``)
to the token — leave the username empty so voctopublish uses the
``Authorization`` header. Always use HTTPS to protect the token in transit.

The token is a shared secret. Anyone who knows it can set YouTube links on
your sessions, so keep it private. Use the *Generate new token* button in
the settings to rotate it if you believe it has leaked.


Installation
------------

Install the plugin with pip, in the same environment as your pretalx
installation::

    (env)$ python -m pip install pretalx-youtube

Afterwards, run ``migrate`` and ``rebuild`` and restart your pretalx services,
just like after any pretalx update (see `performing updates`_ in the
administrator documentation).

You can then enable the plugin under "Settings → Plugins" in your event settings.

Development setup
-----------------

1. Make sure that you have a working `pretalx development setup`_.

2. Clone this repository, eg to ``local/pretalx-youtube``.

3. Install the plugin in editable mode: ``uv pip install -e .``

4. Restart your local pretalx server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


Development commands
~~~~~~~~~~~~~~~~~~~~

This plugin uses `just`_ as a task runner and `uv`_ for dependency management.
Run ``just`` with no arguments to list every available command. The most useful ones
are:

``just fmt``
    Auto-format and lint the code.

``just test``
    Run the full test suite with pytest.

Installing pretalx
~~~~~~~~~~~~~~~~~~~~

The tests need pretalx installed in the environment. ``just test`` handles this for
you: if pretalx cannot be imported, it installs the latest version from git before
running the test suite.

If you already have a development version of pretalx around (for example if you want
to test your changes against a specific commit or branch of pretalx), you can also
install pretalx up front yourself:

``just install-pretalx-local /path/to/pretalx``
    Install pretalx from a local checkout as an editable install.

``just install-pretalx``
    Install the latest pretalx from git (runs before tests if no pretalx is installed).


License
-------

Copyright 2021 Tobias Kunze

Released under the terms of the Apache License 2.0


.. _pretalx: https://github.com/pretalx/pretalx
.. _pretalx development setup: https://docs.pretalx.org/en/latest/developer/setup.html
.. _just: https://just.systems/
.. _uv: https://docs.astral.sh/uv/
.. _performing updates: https://docs.pretalx.org/administrator/maintenance/#performing-updates
