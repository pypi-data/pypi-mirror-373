Overview
========

The `dkist-processing-common` code repository is a library that works with
`dkist-processing-core <https://docs.dkist.nso.edu/projects/core/>`_ and
`dkist-processing-*instrument*` to form the DKIST calibration processing stack.

The classes in this library are used as the base of all DKIST processing pipeline
tasks. Task classes used in instrument pipelines are built on an abstract base class
defined here.  Developers implement a `run` method with the required steps that the
task should take for a particular application.  The class with its `run` method
is then used as the callable object for the workflow and scheduling engine
(which is managed by `dkist-processing-core <https://docs.dkist.nso.edu/projects/core/>`_).
