from astropy.io import fits
import numpy as np

path = r"/home/dylan-wolf/Projects/NASA/MAGNETAR_pipeline/data/SOFIA_HAWC_PLUS_Files/data/SOFIA/HAWC_PLUS/OC6K/20181002_F513/raw/r3/data/si/20181002/2018-10-02_HA_F513_159_CAL_0601191_HAWE_HWPE_RAW.fits"

# Parse FITS, extract arrays/metadata, perform sanity plots & stats, export to a light data format (e.g., Parquet or HDF5) for faster re-loads.

def load_l0_fits(path: str):
    hdul = fits.open(path, memmap=True)
    print([hdu.name for hdu in hdul])

    cfg = hdul["Configuration"].data
    ts = hdul['Timestream'].data

    print([(i, h.name) for i, h in enumerate(hdul)])

    # Typical places to look:
    print(repr(hdul[0].header))  # Primary header
    print(repr(hdul['Timestream'].header))

    for name in hdul['Timestream'].columns.names:
        if "hwp" in str(name):
            print(name)
        elif "HWP" in str(name):
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
    R0, R1, T0, T1 = (
        sq1[:, :, 0:32], # Reference Array 0: Measures telescope background (right-hand reference). These are shielded from the sky and see a blank reference field
        sq1[:, :, 32:64], # Reference Array 1: Measures telescope background (left-hand reference).
        sq1[:, :, 64:96], # Transmission 0: Science array, one polarization. True on sky detectors.
        sq1[:, :, 96:128], # Transmission 1: Science array, orthogonal polarization
    )

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

print(load_l0_fits(path))
summarize_l0(load_l0_fits(path))