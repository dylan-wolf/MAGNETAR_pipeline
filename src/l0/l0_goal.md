Goal here is:

 * Read L0 FITS: parse <code>CONFIGURATION</code> and <code>TIMESTREAM</code>. Detector samples are in SQ1Feedback with shape (41 rows $\times$ 128 cols) per sample; split to R/T arrays (R0/R1/T0/T1 index ranges are in headers). Also load timestamps, HWP encoder, chopper/nod, and astrometry.



* Group by AOR, filter, HWP angle: The AOR ID is embedded in headers/filenames (e.g., Fxxx_HA_POL_06_0119_1_*).

