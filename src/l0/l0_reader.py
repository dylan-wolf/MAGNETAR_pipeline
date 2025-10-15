from astropy.io import fits
import numpy as np

path = r"/home/dylan-wolf/Projects/NASA/MAGNETAR_pipeline/data/SOFIA_HAWC_PLUS_Files/data/SOFIA/HAWC_PLUS/OC6K/20181002_F513/raw/r3/data/si/20181002/2018-10-02_HA_F513_159_CAL_0601191_HAWE_HWPE_RAW.fits"

hdul = fits.open(path, memmap=True)
print([hdu.name for hdu in hdul])