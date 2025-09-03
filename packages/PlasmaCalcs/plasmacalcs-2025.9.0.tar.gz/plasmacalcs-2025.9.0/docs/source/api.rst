PlasmaCalcs API
===============

PlasmaCalcs provides a consistent interface for plasma calculations from any inputs.

These API docs are generated directly from the source code, and can also be seen by calling ``help(obj)`` on the corresponding objects (e.g., classes or functions) from Python, after importing PlasmaCalcs.


Core functionality, used by all PlasmaCalculator objects:

.. autosummary::
   :toctree: generated
   :template: custom_module_template.rst
   :recursive:

   PlasmaCalcs.plasma_calculator
   PlasmaCalcs.quantities
   PlasmaCalcs.dimensions
   PlasmaCalcs.units


Providing various types of PlasmaCalculators (if implementing another kind of input which is not yet recognized PlasmaCalcs, you will probably consider adding it inside ``hookups``):

.. autosummary::
   :toctree: generated
   :template: custom_module_template.rst
   :recursive:

   PlasmaCalcs.hookups
   PlasmaCalcs.addons
   PlasmaCalcs.other_calculators
   PlasmaCalcs.mhd
   PlasmaCalcs.multi_run_analysis


The remaining modules provide a variety of tools, settings, and miscellaneous helpful objects:

.. autosummary::
   :toctree: generated
   :template: custom_module_template.rst
   :recursive:

   PlasmaCalcs.tools
   PlasmaCalcs.plotting
   PlasmaCalcs.defaults
   PlasmaCalcs.errors
