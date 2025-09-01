Differences with the LAL implementation
---------------------------------------

The table summarizes some bugs that have been fixed and some improvements introduced in phenomxpy.

We can introduce those fixes in a `modified version of lalsuite <https://git.ligo.org/cecilio.garcia-quiros/lalsuite/-/tree/debug-phent?ref_type=heads>`_ by activating the LALDict options in the column Name.

.. list-table:: Features and Fixes
   :header-rows: 1
   :widths: 20 20 60

   * - Name
     - Model
     - Description
   * - BugPNAmp (BPN)
     - THM
     - Bug in 33 mode 2.5PN amplitude coefficient: ``-0.086`` → ``-0.86``.
   * - BugPI (BPI)
     - TPHM 
     
       NNLO, MSA
     - Missed initialization of ``powers_of_pi``, affecting the L coefficients.
   * - BugWigner5 (BW5)
     - TPHM
     - Bug in Wigner coefficients d503, d507: ``52.2`` → ``52.5``
   * - BugGammaIntegration 
   
       (BGI)
     - TPHM 
     
       Numerical
     - When adding the gamma offset, the first element of the array was skipped,

       causing a discontinuity at the beginning of the waveform.
   * - PhenomT
   
       Analytical
        
       Derivative (AD)
     - T*
     - Replace numerical derivative for computing ansatz coefficients 
     
       with analytical ones.
   * - NewTimeArray (NTA)
     - T*
     - Builds time array as ``tmin + i * dt``.

       Ensures waveforms with different ``fmin`` agree in overlapping regions

       up to machine precision.
   * - NewRDtimes (NRDT)
     - TP, TPHM 
     
       NNLO, MSA
     - The ringdown attachement started exactly at t=0, but the PN 
       
       time array might not ended exactly at t=0.
   * - RefAngles (RA)
     - TP, TPHM 
        
       NNLO, MSA
     - The angles at reference time (alphaJtoI, ...) where computed from 
        
       the closest point in the time array to tref. Now it uses exactly tref.
   

Remaining differences:

- The numerical solving of tmin and tref introduces some error. One can pass tmin, tref from lal to phenomxpy and get much better agreement.
- The high pass filter used for the FFT (taken from gwsignal) can also introduce some small error. In phenomxpy one can set ``high_pass_filter_lal`` = ``True``.

.. warning::
    
    If you build the time array for LAL using the epoch, bear in mind that this only has precision up to nanoseconds. The option `use_exact_epoch` (EP) uses the epoch up to machine precision by storing tmin in the f0 argument of LALCOMPLEX16TimeSeries and read it from there.