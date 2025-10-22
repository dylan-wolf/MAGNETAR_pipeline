from astropy.io import fits
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

path = r"/home/dylan-wolf/Projects/NASA/MAGNETAR_pipeline/data/SOFIA_HAWC_PLUS_Files/data/SOFIA/HAWC_PLUS/OC6K/20181002_F513/raw/r3/data/si/20181002/2018-10-02_HA_F513_159_CAL_0601191_HAWE_HWPE_RAW.fits"

import matplotlib.pyplot as plt
# Parse FITS, extract arrays/metadata, perform sanity plots & stats, export to a light data format (e.g., Parquet or HDF5) for faster re-loads.

def load_l0_fits(path: str):
    hdul = fits.open(path, memmap=True)
    print([hdu.name for hdu in hdul])

    cfg = hdul["Configuration"].data
    ts = hdul['Timestream'].data
    prime = hdul['Primary'].data
    for p in cfg:
        print(str(p))
    print(cfg,"\n\n\n\n\n")
    print(cfg)

    print([(i, h.name) for i, h in enumerate(hdul)])

    # Typical places to look:
    print(repr(hdul[0].header))  # Primary header
    print("END---------------------------------------------------------")
    print(repr(hdul['Timestream'].header))

    for name in hdul['Timestream'].columns.names:
        if "hwp" in str(name):
            print(name)
        elif "HWP" in str(name):
            print(name)
        elif "Hwp" in str(name):
            print(name)


    def uniq_count(x):
        return len(np.unique(np.asarray(x)))
    print("fastHwpCounts uniques:", uniq_count(ts['fastHwpCounts'])) # fast encoder is inactive for this sample
    print("hwpCounts uniques:", uniq_count(ts['hwpCounts'])) # single stepped angle for this sample
    print("hwpA std, hwpB std:", np.std(ts['hwpA']), np.std(ts['hwpB'])) # constant angle for this sample

    # Should expect constant s for fixed angle subscan. So, we must calculate the angle for this file another way.

    # We will use the analog hwpA/hwpB mean to get the constant angel then snap to the nearest HWSPEQ.

    sq1 = ts["SQ1Feedback"]
    nsamp = sq1.shape[0]

    # To process level 0:
    #
    # Treat R0 + R1 as noise model.
    #
    # Subtract their common signal from T0 + T1 to correct for drifts.
    #
    # Combine T0/T1 at each HWP angle to extract Stokes I, Q, U.

    # --- Split into subarrays ---
    # The first 64 channels (R0, R1) are reference (“dark”) bolometers (A detector that measures the power of incoming electromagnetic radiation by converting it into heat.);
    # the last 64 channels (T0, T1) are the on-sky science bolometers, divided by polarization.
    # Sizes are referenced on p. 5 of HAWC+ DRP User's Manual
    R0, R1, T0, T1 = (
        sq1[:, :, 0:32], # Reference Array 0: Measures telescope background (right-hand reference). These are shielded from the sky and see a blank reference field
        sq1[:, :, 32:64], # Reference Array 1: Measures telescope background (left-hand reference).
        sq1[:, :, 64:96], # Transmission 0: Science array, one polarization. True on sky detectors.
        sq1[:, :, 96:128], # Transmission 1: Science array, orthogonal polarization
    )

    # If SOFIA provides T1 then why cant HAWC use T1: "Each array was designed to have two 32x40 subarrays, for four total detectors (R0, R1, T0, and T1), but T1 is
    # not currently available for HAWC." p.4 HAWC+ User's Manual

    # T1 is viewed as being too noisy and cannot be used. It is maintained for bookkeeping purposes.

    # Data later will throw away bad channels (e.g., T1), combine R0 + T0 for polarization, and merge R0, R1, T0 for total-intensity imaging?

    #print(hdul.info())
    print(ts.columns.names)


    # --- Ancillary columns (may vary by release) ---
    time = _get_first_valid(ts, ["MCETime", "TIME", "UTIME", "Timestamp"])
    hwp  = _get_first_valid(ts, ["hwpCounts","HWP_ANGLE", "HWPEncoder", "HWP_POS"]) # Need to fix this. fastHwpCounts?
    ra   = _get_first_valid(ts, ["RA", "TELRA"])
    dec  = _get_first_valid(ts, ["DEC", "TELDEC"])

    A = ts['hwpA']
    B = ts['hwpB']

    #HWPSEQ = ts['HWPSEQ']

    theta_deg_raw = np.degrees(np.arctan2(B.mean(), A.mean()))
    #nearest = min(HWPSEQ, key=lambda a: abs((a - theta_deg_raw) % 180 - 90))

    #print("NEAREST: ", nearest)

    hdul.close()

    demodulate(ts)

    return {
        "nsamp": nsamp,
        "arrays": {"R0": R0, "R1": R1, "T0": T0, "T1": T1},
        "time": time,
        "hwp": hwp,
        "ra": ra,
        "dec": dec,
        "meta": {"path": path},
    }

def _get_first_valid(ts, candidates):
    for c in candidates:
        if c in ts.columns.names:
            return ts[c]
    return None

def summarize_l0(data):
    """Print quick info about the L0 file."""
    print(f"Samples: {data['nsamp']}")
    for k, v in data["arrays"].items():
        print(f"{k}: shape={v.shape}")
    if data["hwp"] is not None:
        print("HWP range:", np.nanmin(data["hwp"]), "→", np.nanmax(data["hwp"]))


def demodulate(data):
    '''
    This function will demodulate raw time stream with either a square or sine wave form.
    Prior to this a number of filtering steps must be performed to identify good data.
    Raw data is filtered with a box high-pass filter with a time constant of one over the chop frequency.
    Then, any data taken during telescope movement (line-of-sight rewinds, for example, or tracking errors) is flagged for removal. In square wave demodulation, samples are then tagged as being in the high-chop state, low-chop state, or in between (not used). For each complete chop cycle within a single nod position at a single HWP angle, the pipeline computes the average of the signal in the high-chop state and subtracts it from the average of the signal in the low-chop state. Incomplete chop cycles at the end of a nod or HWP position are discarded. The sine-wave demodulation proceeds similarly, except that the data are weighted by a sine wave instead of being considered either purely high or purely low state.
    During demodulation, the data is also corrected for the phase delay in the readout of each pixel, relative to the chopper signal. For square wave demodulation, the phase delay time is multiplied by the sample frequency to calculate the delay in data samples for each individual pixel. The data is then shifted by that many samples before demodulating. For sine wave demodulation, the phase delay time is multiplied with 2𝜋 times the chop frequency to get the phase shift of the demodulating wave-form in radians.
    Alongside the chop-subtracted flux, the pipeline calculates the error on the raw data during demodulation. It does so by taking the mean of all data samples at the same chop phase, nod position, HWP angle, and detector pixel, then calculates the variance of each raw data point with respect to the appropriate mean. The square root of this value gives the standard deviation of the raw flux. The pipeline will propagate these calculated error estimates throughout the rest of the data reduction steps.
    The result of the demodulation process is a chop-subtracted, time-averaged flux value and associated variance for each nod position, HWP angle, and detector pixel. The output is stored in a new FITS table, in the extension called DEMODULATED DATA, which replaces the TIMESTREAM data extension. The CONFIGURATION extension is left unmodified.
    :param data:
    :return:
    '''

    Timestamp = data['Timestamp']
    crioTTLChopOut = data['crioTTLChopOut']
    sofiaChops = data['sofiaChops']
    crioAnalogChopOut = data['crioAnalogChopOut']

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(Timestamp, sofiaChops, crioTTLChopOut)

    plt.show()



print(load_l0_fits(path))
summarize_l0(load_l0_fits(path))