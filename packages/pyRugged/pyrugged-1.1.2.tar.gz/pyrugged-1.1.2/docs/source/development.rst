.. _development:

===========
Development
===========

Contributing to pyRugged
=========================

Rugged is free software, which means you can use the source code as you wish, without charges, in your applications, and that you can improve it and have your improvements included in the next mainstream release.

If you are interested in participating in the development effort, subscribe to the forums (as described in the Contact page) and step up to discuss it. The larger the community is, the better pyRugged will be. The main rule is that everything intended to be included in pyRugged core must be distributed under the Apache License Version 2.0.

Read also `Rugged Contribution guide`_

Development
===========

pyRugged is an intermediate level library. It may be used in very different contexts which cannot be foreseen, from quick studies up to critical operations. The main driving goals are the following ones:

*   validation
*   robustness
*   maintainability
*   efficiency

The first goal, validation, implies tests must be as extensive as possible. They should include realistic operational cases but also contingency cases. The jacoco tool must be used to monitor test coverage. A very high level of coverage is desired. We do not set up mandatory objective figures, but only guidelines here. However,a 60% line coverage would clearly not be acceptable at all and 80% would be considered deceptive.

The second goal, robustness, has some specific implications for a low level component like Rugged. In some sense, it can be considered an extension of the previous goal as it can also be improved by testing. It can also be improved by automatic checking tools that analyze either source code or binary code. The spotbugs tool is already configured for automatic checks of the library using a maven plugin.

This is however not sufficient. A library is intended to be used by applications unknown to the library development team. The library development should be as flexible as possible to be merged into an environment with specific constraints. For example, perhaps an application should run 24/7 during months or years, so caching all results to improve efficiency may prove disastrous in such a use case, or it should be embedded in a server application, so printing to standard output should never be done. Experience has shown that developing libraries is more difficult than developing high level applications where most of the constraints are known beforehand.

The third goal, maintainability, implies code must be readable, clear and well documented. Part of this goal is enforced by the stylistic rules explained in the next section, but this is only for the automatic and simple checks. It is important to keep a clean and extensible design. Achieving simplicity is really hard, so this goal should not be taken too lightly. Good designs are a matter of balance between two few objects that do too many things internally an ignore each other and too many objects that do nothing alone and always need a bunch of other objects to work. Always think in terms of balance, and check what happens if you remove something from the design. Quite often, removing something improves the design and should be done.

The fourth goal, efficiency, should be handled with care to not conflict with the second and third goals (robustness and maintainability). Efficiency is necessary but trying too much too achieve it can lead to overly complex unmaintainable code, to too specific fragile code, and unfortunately too often without any gain after all because of premature optimization and unfounded second-guess.

One surprising trick, that at first sight might seem strange and inappropriate has been used in many part for Rugged and should be considered a core guideline. It is the use of immutable objects. This trick improves efficiency because many costly copying operation are avoided, even unneeded one added for defensive programming. It improves maintainability because both the classes themselves and the classes that use them are much simpler. It also improves robustness because many (really many …) difficult to catch bugs are caused by mutable objects that are changed in some deeply buried code and have an impact on user code that forgot to perform a defensive copy. Orbits, dates, vectors, and rotations are all immutable objects.

Style Rules
===========

For reading ease and consistency, the existing code style should be preserved for all new developments. pyRugged follows `PEP8`_ coding rules.

Pre-commit validation
---------------------

A pre-commit validation is installed with code quality tools (see below).

Here is the way to install it in the dev virtual env:

.. code-block:: console

  $ pre-commit install

This installs the pre-commit hook in `.git/hooks/pre-commit`  from `.pre-commit-config.yaml` file configuration.

It is possible to test pre-commit before commiting:

.. code-block:: console

  $ pre-commit run --all-files                # Run all hooks on all files
  $ pre-commit run --files pyrugged/__init__.py   # Run all hooks on one file
  $ pre-commit run pylint                     # Run only pylint hook


Code quality
~~~~~~~~~~~~

pyRugged uses `Isort`, `Black`, `Flake8` and `Pylint` quality code checking.


Tests
======

pyRugged includes a set of tests executed with `pytest <https://docs.pytest.org/>`_ tool.

To launch tests:

.. code-block:: console

    $ pytest

It is also possible to execute only a specific part of the test, either by indicating the test file to run by using the ``-k`` option.

.. _`PEP8`: https://peps.python.org/pep-0008/
.. _`Rugged Contribution guide` : https://gitlab.cloud-espace.si.c-s.fr/RemoteSensing/pyrugged/-/blob/main/CONTRIBUTING.md