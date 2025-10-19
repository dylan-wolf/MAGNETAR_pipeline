# Timestream Data

## Column Headers

### TES / SQUID readout (detector signals)

| Column           | Meaning                                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------------------------- |
| **SQ1Feedback**  | Feedback signal to the first-stage SQUIDs, proportional to bolometer current (raw detector timestream). |
| **FluxJumps**    | Count of detected flux quantum jumps in SQUID feedback (used for correction).                           |
| **FrameCounter** | Sequential frame index within the observation.                                                          |
| **crioFrameNum** | Frame number from the CompactRIO DAQ system (used for synchronization).                                 |

---

### HWP (Half-Wave Plate) encoder data

| Column                     | Meaning                                                                     |
| -------------------------- | --------------------------------------------------------------------------- |
| **hwpA**, **hwpB**         | Analog encoder channels (quadrature outputs) for slow HWP position readout. |
| **hwpCounts**              | Counts or derived position from HWP encoder (coarse angle).                 |
| **fastHwpA**, **fastHwpB** | High-speed encoder channels (for continuous HWP rotation).                  |
| **fastHwpCounts**          | High-rate counter for the fast HWP readout.                                 |

---

### Optical modulation (chopper) signals

| Column                             | Meaning                                                                  |
| ---------------------------------- | ------------------------------------------------------------------------ |
| **A2a**, **A2b**, **B2a**, **B2b** | TTL analog inputs monitoring chopper blade encoder (quadrature signals). |
| **chop1**, **chop2**               | Derived chopper signals (position or phase).                             |
| **crioTTLChopOut**                 | Digital TTL signal from the chopper controller (for synchronization).    |
| **sofiaChopR**, **sofiaChopS**     | SOFIA telescope chop reference and sync pulses.                          |
| **sofiaChopSync**                  | Combined sync pulse used to align chopper/telescope phases.              |
| **ai22**, **ai23**                 | Additional analog inputs (may record chopper reference voltages).        |
| **crioAnalogChopOut**              | Analog signal output of chopper control from the CompactRIO.             |

---

### Timing / synchronization

| Column             | Meaning                                                                 |
| ------------------ | ----------------------------------------------------------------------- |
| **irigUpdateDiff** | Difference between IRIG-B GPS timing updates (checks timing stability). |
| **Timestamp**      | UTC timestamp of each frame (usually seconds since reference epoch).    |

---

### Telescope pointing (world & local coordinates)

| Column                     | Meaning                                                                         |
| -------------------------- | ------------------------------------------------------------------------------- |
| **RA**, **DEC**            | Right Ascension and Declination of telescope boresight (deg).                   |
| **AZ**, **EL**             | Azimuth and Elevation (deg).                                                    |
| **AZ_Error**, **EL_Error** | Pointing errors in Azimuth/Elevation (arcsec).                                  |
| **SIBS_VPA**               | SOFIA Instrument Bearing System — Vertical Position Angle (orientation on sky). |
| **Chop_VPA**               | Chopper vertical position angle.                                                |
| **LON**, **LAT**           | Geographic longitude and latitude of the aircraft (deg).                        |
| **LST**                    | Local Sidereal Time (hr).                                                       |
| **LOS**                    | Line-of-sight coordinate (telescope pointing relative to aircraft).             |
| **XEL**                    | Cross-elevation coordinate.                                                     |
| **TABS_VPA**               | Telescope Assembly Bearing System vertical position angle.                      |

---

###  Aircraft attitude / motion

| Column                                | Meaning                                                  |
| ------------------------------------- | -------------------------------------------------------- |
| **PITCH**, **ROLL**                   | Aircraft pitch and roll angles (deg).                    |
| **NOD_OFF**                           | Telescope nod offset (arcsec).                           |
| **NonSiderealRA**, **NonSiderealDec** | RA/Dec for non-sidereal tracking (e.g., moving targets). |

---

### Environmental and system flags

| Column                 | Meaning                                                          |
| ---------------------- | ---------------------------------------------------------------- |
| **Flag**               | Data validity / status bit mask (bad frames, sync errors, etc.). |
| **PWV**                | Precipitable water vapor estimate (mm).                          |
| **NodPositionReached** | Boolean or integer flag marking nod position completion.         |

---

### Tracking & centroiding

| Column                                               | Meaning                                           |
| ---------------------------------------------------- | ------------------------------------------------- |
| **TrackErrAoi3**, **TrackErrAoi4**, **TrackErrAoi5** | Tracking errors for Areas of Interest (AOIs) 3–5. |
| **CentroidAoi**                                      | Centroid position for AOI used in tracking loop.  |
| **CentroidWorkPhase**                                | Tracking control phase indicator.                 |
| **CentroidExpMsec**                                  | Exposure time for centroiding camera (ms).        |

---

## Data Type Information
Run:

```python
from astropy.io import fits
hdul = fits.open(path)
hdul['Timestream_Data'].columns.info()
```

To get the exact units and data types, often revealing, e.g., `[deg]`, `[ms]`, `[count]`, etc.