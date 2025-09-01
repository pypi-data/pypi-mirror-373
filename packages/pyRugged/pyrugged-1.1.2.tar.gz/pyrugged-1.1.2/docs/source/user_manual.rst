.. _user_manual:

===========
User manual
===========

:ref:`tutorials`, api and tests gives information and examples to use pyrugged.


Configuration
-------------

As pyRugged relied on Orekit for the frames computation, Orekit must be properly initialized for Rugged to run.

The simplest way to configure is to first retrieve orekit-data in tests/data/orekit-data-master/ . A gitlab project is also
available to download `orekit-data's <https://gitlab.orekit.org/orekit/orekit-data>`_

Note that some of the data in the orekit-data-master folder needs to be updated, typically the UTC-TAI history file, which is updated about once every 18 months by IERS, and the files in the Earth-Orientation-Parameters folder which are updated regularly by IERS. The update frequency depends on which file you use.

The data provided in the example archive from pyRugged site are example only and are not kept up to date. The real operational data are live, and remain under the responsibility of the user.

Quick start
-----------

.. code-block:: console

 #init_orekit import must be placed before any org.orekit or org.hipparchus import
 from pyrugged.api.init_orekit import init_orekit

 init_orekit(orekit_data_path)


.. toctree::
    :maxdepth: 1
    :caption: user manual:

    tutorials
    pyRugged API reference <apidoc/modules>