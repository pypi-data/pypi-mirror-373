Examples
========

The following examples present some common use cases that show how to run qupled and how to post-process the results.

Setup a scheme and analyze the output
-------------------------------------

This example sets up all the necessary objects to solve the RPA and ESA schemes and
shows how to access the information stored in the output files produced at the
end of the calculations

.. literalinclude:: ../examples/docs/solve_rpa_and_esa.py
   :language: python

A simple STLS solution
----------------------

This example sets up a simple STLS calculation and  plots some of the results 
that are produced once the calculation are completed. There are two ways to access
the results of the calculation: Directly from the object used to perform the calculation
or from the output file created at the end of the run. The example illustrates how
the static structure factor can be accessed with both these methods. Other quantities
can be accessed in the same way.

.. literalinclude:: ../examples/docs/solve_stls.py
   :language: python

Solving the classical IET schemes
----------------------------------

This example shows how to solve two classical STLS-IET schemes: the STLS-HNC and
the STLS-LCT schemes. The schemes are solved one after the other by simply
updating the properties of the solution object.

.. literalinclude:: ../examples/docs/solve_stls_iet.py
   :language: python

.. _solvingQuantumSchemes:

Solving the quantum schemes
---------------------------

This example shows how to solve the quantum dielectric schemes QSTLS and QSTLS-LCT. 
Since these schemes can have a relatively high computational cost, in this example 
we limit the number of matsubara frequencies to 16, we use 16 OMP threads to 
speed up the calculation and we employ a segregated approach to solve the two-dimensional 
integrals that appear in the schemes. 

.. literalinclude:: ../examples/docs/solve_quantum_schemes.py
   :language: python

Solving the VS schemes
----------------------

This example shows how to solve the classical VS-STLS scheme at finite temperature.
First the scheme is solved up to rs = 2, then the results are
plotted and then the calculation is resumed up to rs = 5. In the second
part of the calculation, the pre-computed value of the free energy integrand
available from the VS-STLS solution at rs = 2 is used in order to speed
up the calculation.

.. literalinclude:: ../examples/docs/solve_vsstls.py
   :language: python

This example shows how to solve the quantum version of the VS-STLS scheme.
Following the same logic of the previous example we first solve the scheme
up to rs = 1.0 and then we resume the calculation up to rs = 2.0 while using
the pre-compute values of the free energy integrand.

.. literalinclude:: ../examples/docs/solve_qvsstls.py
   :language: python
         
Define an initial guess
-----------------------

The following example shows how to define an initial guess for the STLS scheme. If 
an initial guess is not specified the code will use the default, namely zero static 
local field correction.

.. literalinclude:: ../examples/docs/initial_guess_stls.py
   :language: python

For other schemes the initial guess can be specified in a similar manner.
         
Speed-up the quantum schemes
----------------------------

The quantum schemes can have a significant computational cost. There are two strategies
that can be employed to speed up the calculations:

* *Parallelization*: qupled supports both multithreaded calculations with OpenMP and
  multiprocessors computations with MPI. OpenMP and MPI can be
  used concurrently by setting both the number of threads and the number of cores in the 
  input dataclasses. Use `threads` to set the number of OMP threads and `processes` to
  set the number of MPI processes.
 
* *Pre-computation*: The calculations for the quantum schemes can be made significantly
  faster if part of the calculation of the auxiliary density response can be skipped.
  Qupled will look into the database used to store the results to try to find the 
  necessary data to skip the full calculation of the auxiliary density response.

The following example shows the effect of pre-computation. The example first
computes the auxiliary density response for a given set of parameters and then
it uses the pre-computed data to speed up the calculation of the auxiliary density
response for a different set of parameters.

.. literalinclude:: ../examples/docs/fixed_adr.py
   :language: python