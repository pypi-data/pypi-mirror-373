MPSPlots
========

.. list-table::
   :widths: 10 25 25
   :header-rows: 0

   * - Meta
     - |python|
     - |docs|
   * - Testing
     - |ci/cd|
     - |coverage|
   * - PyPi
     - |PyPi|
     - |PyPi_download|
   * - Anaconda
     - |anaconda|
     - |anaconda_download|


Overview
********

**MPSPlots** is a personal plotting library developed as a streamlined wrapper around two popular visualization tools: **Matplotlib** for 2D plotting and **PyVista** for 3D visualization.
This library was created with the goal of balancing ease-of-use with flexibility, allowing users to produce consistent plots for scientific publications.
Initially developed to standardize the author’s scientific plots, **MPSPlots** continues to evolve, providing a customizable yet simple interface for a wide range of plotting needs.

Key Features:
- Intuitive and straightforward API, abstracting common plotting tasks.
- High-quality outputs tailored for scientific journals.
- Seamless integration with Matplotlib and PyVista.
- Easily customizable plots without sacrificing flexibility.

The motivation behind this library was to make complex plotting routines more accessible while maintaining the ability to fine-tune results as needed, making it ideal for researchers and scientists who require consistent, publication-ready plots.

----

Installation
************

To install the library from PyPI, simply use `pip`, or `conda`:

.. code:: console

   pip install MPSPlots
   conda install --channels martinpdes mpsplots

For a development version, clone the GitHub repository and install the dependencies manually:

.. code:: console

   git clone https://github.com/MartinPdeS/MPSPlots.git
   cd MPSPlots
   pip install -r requirements/requirements.txt

This setup ensures that you have access to the latest updates and features under active development.

----

Usage
*****

**MPSPlots** can be integrated into your scientific workflow with minimal effort. Here’s a simple example showing how you can create a 2D Matplotlib plot:

.. code:: python

   from MPSPlots.render2D import Scene

   plot = Scene()
   plot.add_line(x_data, y_data, label="Sample Line")
   plot.show()

For more complex 3D visualizations using PyVista:

.. code:: python

   from MPSPlots.render3D import Scene

   plot = Scene()
   plot.add_surface(mesh)
   plot.show()

Whether it's a 2D line chart or a 3D surface plot, **MPSPlots** makes it simple to generate publication-quality visualizations quickly.

----

Testing and Development
***********************

If you want to contribute to the project or test it locally, follow these steps to set up your development environment:

1. Clone the repository:

   .. code:: console

      git clone https://github.com/MartinPdeS/MPSPlots.git
      cd MPSPlots

2. Install dependencies:

   .. code:: console

      pip install -r requirements/requirements.txt

3. Run the tests with coverage:

   .. code:: console

      coverage run --source=MPSPlots --module pytest --verbose tests
      coverage report --show-missing

These commands will ensure that you have all the necessary dependencies and will run the tests, providing you with a detailed report on code coverage and any potential issues.

----

Documentation
*************

Detailed documentation for **MPSPlots** is available `here <https://martinpdes.github.io/MPSPlots/>`_, where you'll find a comprehensive guide to the library's usage, examples, and API references.
Whether you're a beginner or an advanced user, the documentation provides clear instructions and examples to help you get the most out of the library.

----

Contributing
************

**MPSPlots** is an open-source project under continuous development, and contributions are welcome! Whether it's bug fixes, new features, or improvements to documentation, any help is appreciated. If you're interested in collaborating, please feel free to reach out to the author.

If you'd like to contribute:

1. Fork the repository and create your feature branch:

   .. code:: console

      git checkout -b feature-branch

2. Commit your changes and push your branch:

   .. code:: console

      git commit -m "Add new feature"
      git push origin feature-branch

3. Create a Pull Request on GitHub.

----

Contact Information
*******************

As of 2023, **MPSPlots** is actively maintained and open to collaboration.
If you're interested in contributing or have any questions, don't hesitate to reach out.
The author, `Martin Poinsinet de Sivry-Houle <https://github.com/MartinPdeS>`_, can be contacted via:

- **Email**: `martin.poinsinet-de-sivry@polymtl.ca <mailto:martin.poinsinet-de-sivry@polymtl.ca?subject=MPSPlots>`_

The project continues to evolve, and your contributions are encouraged!


----

.. |python| image:: https://img.shields.io/pypi/pyversions/mpsplots.svg
   :alt: Python
   :target: https://www.python.org/

.. |PyPi| image:: https://badge.fury.io/py/MPSPlots.svg
   :alt: PyPi package
   :target: https://pypi.org/project/MPSPlots/

.. |docs| image:: https://github.com/martinpdes/mpsplots/actions/workflows/deploy_documentation.yml/badge.svg
   :target: https://martinpdes.github.io/MPSPlots/
   :alt: Documentation Status

.. |ci/cd| image:: https://github.com/martinpdes/mpsplots/actions/workflows/deploy_coverage.yml/badge.svg
   :target: https://martinpdes.github.io/MPSPlots/actions
   :alt: Unittest Status

.. |coverage| image:: https://raw.githubusercontent.com/MartinPdeS/MPSPlots/python-coverage-comment-action-data/badge.svg
   :alt: Unittest coverage
   :target: https://github.com/MartinPdeS/MPSPlots/actions

.. |PyPi_download| image:: https://img.shields.io/pypi/dm/MPSPlots.svg
   :alt: PyPi version
   :target: https://pypistats.org/packages/mpsplots

.. |anaconda| image:: https://anaconda.org/martinpdes/mpsplots/badges/version.svg
   :alt: Anaconda version
   :target: https://anaconda.org/martinpdes/mpsplots

.. |anaconda_download| image:: https://anaconda.org/martinpdes/mpsplots/badges/downloads.svg
   :alt: Anaconda downloads
   :target: https://anaconda.org/martinpdes/mpsplots
