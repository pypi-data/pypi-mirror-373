v2.2.1 (2025-08-30)
===================

Misc
----

- Add code coverage badge to README.rst. (`#21 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/21>`__)
- Removing usage of the deprecated `pkg_resources`. (`#22 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/22>`__)
- Update pre-commit hook versions and replace python-reorder-imports with isort. (`#23 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/23>`__)


v2.2.0 (2025-02-24)
===================

Features
--------

- Add `stddev_numpy_arrays` function for computing the per-pixel standard deviation of an iterable of arrays.
  If a `generator` is provided this function is very memory-light, even for huge stacks of arrays. (`#20 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/20>`__)


Misc
----

- Update bitbucket pipelines to use common scripts for checking for changelog snippets and verifying doc builds. (`#18 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/18>`__)
- Update Bitbucket pipelines to use execute script for standard steps. (`#19 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/19>`__)


v2.1.2 (2024-12-20)
===================

Misc
----

- Update Bitbucket pipelines to use standardized lint and scan steps. (`#17 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/17>`__)


Documentation
-------------

- Change the documentation landing page to focus more on users and less on developers. (`#16 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/16>`__)


v2.1.1 (2024-10-14)
===================

Misc
----

- Make and publish wheels at code push in build pipeline (`#15 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/15>`__)
- Switch from setup.cfg to pyproject.toml for build configuration (`#15 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/15>`__)


v2.1.0 (2023-11-28)
===================

Features
--------

- Add functions to broadcast matrix multiplication over extra array dimensions. (`#14 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/14>`__)


v2.0.0 (2023-06-29)
===================

Misc
----

- Update to python 3.11 and update library package versions. (`#13 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/13>`__)


v1.0.1 (2022-12-14)
===================

Documentation
-------------

- Add changelog to RTD left hand TOC to include rendered changelog in documentation build. (`#12 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/12>`__)


v1.0.0 (2022-11-02)
===================

Misc
----

- Major version change for production release.


v0.3.1 (2022-08-04)
===================

Features
--------

- Expose `width` and `func` parameters of `peakutils.interpolate` in the signature of `feature.find_px_angles`. (`#11 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/11>`__)


Bugfixes
--------

- If peak angle interpolation fails return the non-interpolated peak instead of garbage. (`#11 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/11>`__)


v0.3.0 (2022-07-07)
===================

Features
--------

- Changed underlying algorithm in `resize_arrays` to allow for higher-order interpolation methods. Local-mean resizing is still available in the new `resize_arrays_local_mean` function. (`#10 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/10>`__)


v0.2.4 (2022-04-20)
===================

Features
--------

- Add `resize_arrays` function for arbitrary reshaping (`#8 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/8>`__)


Documentation
-------------

- Add CHANGELOG and towncrier machinery (`#9 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/9>`__)


v0.2.3 (2022-02-24)
===================

Documentation
-------------

- Set up Read the Docs documentation builds

v0.2.2 (2022-01-20)
===================

Documentation
-------------

- Remove unneeded RTD git dependency

v0.2.1 (2021-12-19)
===================

Bugfixes
--------

- Fix error in Hough transform caused by `scikit-image >= 0.0.19` (`#7 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/7>`__)

v0.2.0 (2021-10-28)
===================

Bugfixes
--------

- Fix mis-ordering of axis caused by difference between skimage and numpy (`#6 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/6>`__)

v0.1.0 (2021-07-28)
===================

The beginning of history
