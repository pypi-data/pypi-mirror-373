CHANGELOG
=========

**Pythonic FP namespace projects**

Developer Tools supporting a functional style of programming yet endeavoring to
remain Pythonic. All projects are under the ``pythonic-fp`` namespace on PyPI.

Important Milestones
--------------------

Update - 2025-08-13
~~~~~~~~~~~~~~~~~~~

Moved pythonic_fp.gadgets to its own repo. Replaced it with
an empty module called pythonic_fp.name_claim.

Update - 2025-08-13
~~~~~~~~~~~~~~~~~~~

Generated docs for pythonic-fp-booleans PyPI project

- first development (prerelease) generation of of docs for booleans.sbool

Update - 2025-08-11
~~~~~~~~~~~~~~~~~~~

The next gadget's release will be v1.2.0.

- added module pythonic_fp.gadgets.lca for function latest common ancestor

2025-08-09 - Preparing for upcoming PyPI release for gadgets

- decided to make gadget's pyproject.toml the exemplar for rest of pythonic-fp namespace
- pythonic_fp.gadget works with previous and next release of singletons

2025-08-02 - Completed coordinated release of pythonic-fp namespace projects

- released pythonic-fp v1.1.0 which contains pythonic_fp.gadgets package
- released pythonic-fp-circulararray v5.3.0 immediately followed by v5.3.1

  - had to fix a link in README.rst, changed

    - pythonic-fp.circulararray to pythonic-fp-circulararray 

      - linked still worked since PyPI maps ``.`` and ``_`` to ``-``

    - had to update development/source/conf.py
    - had to update development/source/releases.py
    - had to copy generated html to release directories

- released pythonic-fp-containers v3.0.0
- released pythonic-fp-fptools v5.0.0
- released pythonic-fp-iterables v5.0.0
- released pythonic-fp-singletons v1.0.0
- released pythonic-fp-splitends v1.0.0
- setup Sphinx for development environment documentation

  - bumped all version numbers by one patch level
  - redid Sphinx development docs for entire namespace project

2025-08-01 - Added pythonic_fp.gadgets to pythonic-fp
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added package pythonic_fp.gadgets to PyPI project pythonic-fp. Now
this "name-claim" package is installable.

The gadgets library is for simple, but useful, data structures with
minimal dependencies.

2025-07-30 - Updated all Sphinx docs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updated Sphinx docs for all pythonic_fp namespace projects to the latest format.
Still need to do consistency checks.

2025-07-30 - Updated Sphinx docs for pythonic_fp.queues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Which has been deprecated. Use pythonic_fp.containers.queues instead.

2025-07-30 - Added Sphinx docs for gadgets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fairly easy copy and edit from circulararray.

2025-07-29 - Complete redo of circulararray docs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now PyPI project pythonic-fp.circulararray will be the exemplar for
Sphinx documentation. The toctrees are no longer hidden.

2025-07-27 - Finished Sphinx documentation for two PyPI projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Satisfied with the development versions of Sphinx documentation for
pythonic-fp.circulararray and pythonic-fp.queues.

2025-07-21 - Unified coordinated upgrade all pytonic-fp projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updated all pyprojects.toml files and corresponding Sphinx documentation for
an upcoming coordinated release of all packages. From a flowchart of library
dependencies, a better organization became apparent to the maintainer. Will be
removing all "from future import annotations" from the code. All this does is
replace module names with strings. It was a hack to support a future feature
that will never happen. This future import will be deprecated in Python 3.14.

- rename GH-Pages mount point from pypi-release-docs/ to just docs/
- removed ``/API/`` from ``docs/*/API/*``
- move maybe and (xor -> either) modules back to fptools
- broke out module fptools/singletons to its own repo
- moved fptools.bool -> singletons.sbool

TODO:

- finish pdoc -> Sphinx migration

  - all informational content will come from docstrings
  - replace the Markdown Pythonic FP "homepage" with Sphinx based one

    - grscheller/pythonic-fp/README.md will point to the new docs

- next PyPI release will happen when "everything is ready"

2025-07-13 - All document generation brought back to this repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Sphinx now used

  - looks much more professional
  - all documentation generation moved back to this repo
  - docstrings in code a bit rough, but now more terse

- Updated docs for circulararray PyPI release v5.2.0
- Updated docs for queues PyPI release v4.0.1
- the docs links on the README.md pythonic-fp homepage updated

  - now points to docs development's release page instead of docs development itself

2025-07-04 - Beginning dtools deprecation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Published version 5.1.0 pythonic-fp.circulararray to PyPI
- Updated pyproject.toml files for all pythonic-fp namespace repos
- Updated all README.md files to use GitHub, not GH-Pages, for Pythonic FP Homepage
- Updated all repo root CHANGELOG.rst files

  - preparing to rename them docs/source/changelog.rst for Sphinx build
  - all except this one

2025-06-29 - Switching from pdoc to Sphinx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Building pythonic-fp.circulararray docs with Sphinx

  - ended up using the Sphinx autodoc extension
  - using the `piccolo-theme <https://pypi.org/project/piccolo-theme>`_ as the html_theme

- Not yet "publishing" them on gh-pages, looking into ``sphinx.ext.githubpages``

  - realized I will need to move docs over to pythonic-fp repo for PyPI releases
  - the gh-pages for the namespace repos will host the current devel env docs

2025-05-29 - Beginning transition pdoc -> Sphinx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Stumble on PyPI project python-sphinx-doc
- Supposedly will parse Python type annotations

  - uninstall ``pdoc``, install ``python-sphinx-doc``
  - when I get these packages with "sphinx" in their names

    ================================= =====
    ``python-sphinx-doc``             0.1
    ``Sphinx``                        8.2.3
    ``sphinxcontrib-applehelp``       2.0.0
    ``sphinxcontrib-devhelp``         2.0.0
    ``sphinxcontrib-htmlhelp``        2.1.0
    ``sphinxcontrib-jsmath``          1.0.1
    ``sphinxcontrib-qthelp``          2.0.0
    ``sphinxcontrib-serializinghtml`` 2.0.0
    ``sphinx_design``                 0.6.1
    ================================= =====

  - Only ``sphinx_design`` is a ``python-sphinx-doc`` dependency
    that is not also a ``Sphinx`` dependency.

2025-05-24 - More work "biting-the-bullet"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Decided on the pythonic-fp namespace name instead of fpythonic 
- Brought over source code from all dtools namespace projects

  - pythonic-fp.circulararray 5.0.0
  - pythonic-fp.containers 2.0.0
  - pythonic-fp.fptools 3.0.0
  - pythonic-fp.iterables 3.0.0
  - pythonic-fp.queues 3.0.0
  - pythonic-fp.splitends 0.30.0
  - pythonic-fp (name_claim) 1.0.0 - DO NOT INSTALL

2025-05-23 - Decided to "bite-the-bullet" and drop dtools name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Decided on the unclaimed name fpythonic

  - for fp + pythonic

- Releases under this name

  - fpythonic 1.2.0
  - fpythonic 1.1.0
  - fpythonic 1.0.0
  - fpythonic.circular-array v4.1.0
  - fpythonic.circular-array v4.0.0 (Yanked)
  - yanked because v4.0.0 was published on PyPI too soon

- fpythonic is an empty module

  - will permanently be <2.0
  - has a __init__.py file

    - DO NOT INSTALL IT!!!
    - if you do, fpythonic will no longer be a namespace module!
    - PyPI was happy to accept it

      - thought it best to take the name

  - its GitHub repo has 2 purposes other than implementing this "module"

    - serves as a homepage for the fpythonic namespace modules
    - hosts the generated documentation on gh-pages

2025-05-22 - Rebuilt docs for all projects for next PyPI releases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- dtools.circular-array 3.15.0
- dtools.containers 1.0.0
- dtools.fp 2.0.0
- dtools.iterables 2.0.0
- dtools.queues 2.0.0
- dtools.splitends 0.29.0

2025-05-20 - Broke out dtools.fp.iterables to its own repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- dtools.fp.iterables -> dtools.iterables
- GitHub repo: https://github.com/grscheller/dtools-iterables/

2025-05-12 - MayBe and Xor moved
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- From dtools.fp
- To dtools.containers

2025-05-10 - Changed GitHub name of this repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
- GitHub repo name change

  - grscheller/dtools-docs -> grscheller/dtools-namespace-projects
  - will double as a project homepage as well as the document repo

2025-05-05 Added dtools.containers project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Added dtools.containers project and deprecated dtools.tuples
- dtools.tuples content moved to dtools.containers

  - actually dtools.tuples repo just renamed to dtools.containers

    - this allows older PyPI source code links to keep working
    - thought necessary since my Boring Math Library not updated yet

2025-04-24: Decided to change name back to dtools-docs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
- A PyPI project named dtools already exists
- Unfortunately, I missed this back in January

2025-04-24: Renamed repo from dtools-docs to just dtools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
- Morphing README.md into a project-wide Homepage
- Created CHANGELOG.md file
- Removed README.md links to deprecated dtools.datastructures project

2025-03-31: Updates for new dtools project Mar 31
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Adding infrastructure for dtools.tuples

2025-03-28: updated docs for all dtools projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Ran linters and against all dtools namespace repos

2025-02-06: Standardized dtools and bm docs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Standardized Developer Tools and Boring Math project documentation

2025-01-17: Created this repo - dtools-docs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Created this repo for pdoc generated dtools project documentation

  - purpose to keep actual source code repos smaller
  - detailed documentation generated from source code docstrings
  - replaces grscheller-pypi-namespace-docs 

    - older repo still exits as a "zombie" project

      - to keep older PyPI document links working

- Added development documentation infrastructure for all dtools repos

  - dtools.datastructures
  - dtools.fp
  - dtools.circular-array

- Generated docs for first PyPI releases under dtools namespace
