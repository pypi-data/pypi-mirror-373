=================================
Peek Platform - Admin Doc Service
=================================

The Peek Admin Doc service contains the admin documentation container.

Admin documentation from other plugins are linked in to this container, this will be
RST text files and images.

A sphinx build is then run to generate the HTML and PDF documentation

Manual Builds
-------------

Builds are performed by either the peek-office-service or peek-logic-service service much the same way
the builds are performed for the mobile-web frontends.

Manual builds can be performed by running the following :

::

        cd <project dir>/peek_admin_doc
        build_html_docs.sh

