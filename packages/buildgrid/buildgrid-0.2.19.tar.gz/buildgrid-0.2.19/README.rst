.. image:: https://gitlab.com/BuildGrid/buildgrid/badges/master/pipeline.svg
    :target: https://gitlab.com/BuildGrid/buildgrid/-/commits/master
    :alt: pipeline status

.. image:: https://gitlab.com/BuildGrid/buildgrid/badges/master/coverage.svg
    :target: https://gitlab.com/BuildGrid/buildgrid/-/commits/master
    :alt: coverage report

.. image:: https://gitlab.com/BuildGrid/buildgrid/-/badges/release.svg
    :target: https://gitlab.com/BuildGrid/buildgrid/-/releases
    :alt: coverage report


.. _about:

About
=====

.. _what-is-it:

What is BuildGrid?
------------------

BuildGrid is a Python remote execution service which implements Google's
`Remote Execution API`_ and the `Remote Workers API`_. The project's goal is to
be able to execute build jobs remotely on a grid of computers in order to
massively speed up build times. Workers on the grid should be able to run with
different environments. It works with clients such as `Bazel`_,
`BuildStream`_ and `RECC`_, and is designed to be able to work with any client
that conforms to the above API protocols.

BuildGrid is designed to work with any worker conforming to the `Remote Workers API`_
specification. Workers actually execute the jobs on the backend while BuildGrid does
the scheduling and storage. The `BuildBox`_ ecosystem provides a suite of workers and
sandboxing tools that work with the Workers API and can be used with BuildGrid.

.. _Remote Execution API: https://github.com/bazelbuild/remote-apis
.. _Remote Workers API: https://docs.google.com/document/d/1s_AzRRD2mdyktKUj2HWBn99rMg_3tcPvdjx3MPbFidU/edit#heading=h.1u2taqr2h940
.. _BuildStream: https://wiki.gnome.org/Projects/BuildStream
.. _Bazel: https://bazel.build
.. _RECC: https://gitlab.com/BuildGrid/buildbox/buildbox/-/tree/master/recc
.. _Trexe: https://gitlab.com/BuildGrid/buildbox/buildbox/-/tree/master/trexe
.. _BuildBox: https://buildgrid.gitlab.io/buildbox/buildbox-home/


.. _readme-getting-started:

Getting started
---------------

Please refer to the `documentation`_ for `installation`_ and `usage`_
instructions, plus guidelines for `contributing`_ to the project.

.. _contributing: https://buildgrid.build/developer/contributing.html
.. _documentation: https://buildgrid.build/
.. _installation: https://buildgrid.build/user/installation.html
.. _usage: https://buildgrid.build/user/using.html


.. _about-resources:

Resources
---------

- `Homepage`_
- `GitLab repository`_
- `Bug tracking`_
- `Mailing list`_
- `Slack channel`_ [`invite link`_]
- `FAQ`_

.. _Homepage: https://buildgrid.build/
.. _GitLab repository: https://gitlab.com/BuildGrid/buildgrid
.. _Bug tracking: https://gitlab.com/BuildGrid/buildgrid/boards
.. _Mailing list: https://lists.buildgrid.build/cgi-bin/mailman/listinfo/buildgrid
.. _Slack channel: https://buildteamworld.slack.com/messages/CC9MKC203
.. _invite link: https://bit.ly/2SG1amT
.. _FAQ: https://buildgrid.build/user/faq.html
