Changelog
=========

1.5.0 (2025-09-01)
------------------
- | Now about_from_setup() returns an instance of the 'about' class
  | (but backward compatibility is preserved).
- Making the package typed.
- Setup (dependencies) update.

1.3.7 (2025-07-07)
------------------
- Use standard importlib.metadata instead of importlib-metadata.
- Setup (dependencies) update.

1.3.6 (2025-06-11)
------------------
- Setup (dependencies) update.

1.3.5 (2025-05-15)
------------------
- | The 'License-Expression' metadata field takes precedence over the
  | 'License' metadata field.
- The distribution is now created using 'build' instead of 'setuptools'.
- Setup (dependencies) update (due to regressions in tox and setuptools).

1.3.3 (2025-05-04)
------------------
- Setup (dependencies) update.

1.3.1 (2025-05-01)
------------------
- Add support for Python 3.14
- Drop support for Python 3.9 (due to compatibility issues).
- Update readthedocs's python to version 3.13
- Update tox's base_python to version 3.13
- | Remove the ability to obtain __copyright__ from the README.rst or
  | __about__.py due to significant compatibility issue(s) (because the
  | 'Copyright' field is not a member of the package metadata at all).
  | For now, the __copyright__ field is the same as __author__ field
  | (which is always obtained from the package metadata).
- Remove dependencies on docutils.
- Setup (dependencies) update.

1.2.11 (2025-03-20)
-------------------
- Add support for PyPy 3.11
- Drop support for PyPy 3.9
- Setup (dependencies) update.

1.2.10 (2025-03-15)
-------------------
- Setup (dependencies) update.

1.2.9 (2025-02-14)
------------------
- Setup (dependencies) update.

1.2.8 (2025-01-25)
------------------
- Setup (dependencies) update.

1.2.7 (2025-01-20)
------------------
- Copyright year update.
- Setup (dependencies) update.

1.2.6 (2024-12-13)
------------------
- Source distribution (\*.tar.gz now) is compliant with PEP-0625.
- Setup (dependencies) update.

1.2.5 (2024-11-13)
------------------
- More unittests.
- 100% code linting.
- 100% code coverage.
- Tox configuration is now in native (toml) format.
- Setup (dependencies) update.

1.2.2 (2024-10-30)
------------------
- Setup (dependencies) update.

1.2.0 (2024-09-30)
------------------
- Drop support for Python 3.8
- Ability to obtain __copyright__ from the README.rst content.
- Setup (dependencies) update.

1.1.8 (2024-08-13)
------------------
- Add support for Python 3.13
- Setup (dependencies) update.

1.1.7 (2024-07-15)
------------------
- Setup (dependencies) update.

1.1.6 (2024-06-20)
------------------
- Setup (dependencies) update.

1.1.5 (2024-01-26)
------------------
- Setup update (now based on tox >= 4.0).
- Cleanup.

1.1.0 (2023-12-15)
------------------
- Add support for Python 3.12
- Drop support for Python 3.7
- Add support for PyPy 3.10
- Drop support for PyPy 3.7 and 3.8
- Bugfix for parsing metadata's 'Project-URL'.
- Bugfix of about_from_setup() for __version_info__.
- | Enhancement: the 'package_path' parameter of the about_from_setup()
  | can now be of type string or Path.
- Bugfix of about_from_setup() for parsing author and maintainer emails.
- Copyright year update.
- Added a trivial unit test.

1.0.8 (2022-10-18)
------------------
- Tox configuration has been moved to pyproject.toml

1.0.7 (2022-08-22)
------------------
- Setup update.

1.0.6 (2022-07-24)
------------------
- Add __author_email__ (as alias of __email__).
- Add __maintainer_email__.
- Setup update (currently based mainly on pyproject.toml).

1.0.5 (2022-07-20)
------------------
- Add about_from_setup() (to use e.g. in docs.conf.py).
- Add support for Python 3.10 and 3.11
- Add support for PyPy 3.7, 3.8 and 3.9
- Setup update.

1.0.4 (2022-01-10)
------------------
- Drop support for Python 3.6
- Copyright year update.
- Setup update.

1.0.3 (2021-10-14)
------------------
- Setup update.

1.0.2 (2021-07-20)
------------------
- First functional release.

0.0.1 (2020-10-16)
------------------
- Initial commit.
