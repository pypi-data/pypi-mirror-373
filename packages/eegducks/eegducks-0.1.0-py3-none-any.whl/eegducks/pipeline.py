import mne
import os
import numpy as np
import pandas as pd # Import pandas

def select_event_id(event_dict, event_id=None):
    if event_id is None:
        # pick first event in dictionary as default
        return list(event_dict.values())[0]
    elif isinstance(event_id, str):
        return event_dict[event_id]
    else:
        return event_id



def load(filepath, l_freq=1, h_freq=30, preload=True, ref="average", plot=True, locinf=None):
    """
    Load EEG file, apply bandpass filter, set reference, and optionally plot.

    Parameters
    ----------
    filepath : str
        Path to EEG file (.fif, .edf, .bdf, .vhdr, .cnt, .set).
    l_freq : float, optional
        Low cutoff frequency (Hz) for bandpass filter.
    h_freq : float, optional
        High cutoff frequency (Hz) for bandpass filter.
    preload : bool, optional
        Whether to preload data into memory.
    ref : str, optional
        Reference type ("average" or specific channel).
    plot : bool, optional
        Whether to show raw data preview.

    Returns
    -------
    raw : mne.io.Raw
        Preprocessed raw EEG data.
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".fif":
        raw = mne.io.read_raw_fif(filepath, preload=preload)
    elif ext in [".edf", ".bdf"]:
        raw = mne.io.read_raw_edf(filepath, preload=preload)
    elif ext == ".vhdr":
        raw = mne.io.read_raw_brainvision(filepath, preload=preload)
    elif ext == ".cnt":
        raw = mne.io.read_raw_cnt(filepath, preload=preload)
    elif ext == ".set":
        raw = mne.io.read_raw_eeglab(filepath, preload=preload)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    print(raw.info)

    raw.filter(l_freq, h_freq)
    raw.set_eeg_reference(ref, projection=True)

    # --- Apply notch filter at 60 Hz if needed ---
    psd = raw.compute_psd(fmax=60).get_data()
    freqs = raw.info['sfreq'] * np.arange(psd.shape[1]) / psd.shape[1]

    # Simple heuristic: if mean power > threshold above 50 Hz, notch
    if psd.shape[1] > 50:
        power_high = psd[:, freqs > 50].mean()
        if power_high > 1e-12:  # adjust threshold if needed
            raw.notch_filter(60)
            print("Applied 60 Hz notch filter due to high power above 50 Hz")


    # Load EEG data into MNE with channel location and renaming.
    #
    # Parameters
    # ----------
    # filepath : str
    #     Path to the EEG data file (.set, .edf, .bdf, .fif, .tsv, etc.).
    # locinf : str or None
    #     Path to channel location file (e.g., .locs or .tsv).
    #     If None, montage handling will be skipped.
    #
    # Returns
    # -------
    # raw : mne.io.Raw
    #     Preprocessed MNE Raw object.

    # Only set montage if coordinates exist
   


    montage = None  # initialize

    # 2. If channel location file is given, apply montage and renaming
    if locinf:
      if locinf.endswith(".tsv"):
        import pandas as pd
        chan_df = pd.read_csv(locinf, sep="\t")
        newchan = chan_df['name'].tolist()  # BIDS column
        oldchan = raw.info['ch_names']
        chandict = {oldchan[i]: newchan[i] for i in range(min(len(oldchan), len(newchan)))}
        raw.rename_channels(chandict)

        # Build montage if xyz coordinates exist
        if all(col in chan_df.columns for col in ['x', 'y', 'z']):
            pos = chan_df[['x', 'y', 'z']].values / 100  # mm → m
            montage = mne.channels.make_dig_montage(ch_pos=dict(zip(newchan, pos)), coord_frame='head')
            raw.set_montage(montage, on_missing='ignore')
      else:
        montage = mne.channels.read_custom_montage(locinf)

        try:
          newchan = np.loadtxt(locinf, dtype=str, usecols=3)
          oldchan = raw.info["ch_names"]
          # Map only matching number of channels
          chandict = {oldchan[i]: newchan[i] for i in range(min(len(oldchan), len(newchan)))}
          raw.rename_channels(chandict)
        except Exception as e:
          print(f"⚠️ Could not rename channels from {locinf}: {e}")
          # Only set montage if it exists
      if montage is not None:
        raw.set_montage(montage, on_missing="ignore")

    # # Optional: EOG channels
    # chan_types_dict = {"EOG1": "eog", "EOG2": "eog"}
    # raw.set_channel_types(chan_types_dict, on_unit_change="ignore")

    return raw


def plot(raw, dur=5, n_chan=20):
    """Plot raw EEG."""
    raw.plot(n_channels=n_chan, duration=dur)

def psdplt(raw, picks="eeg", avg=False):
    """Plot PSD; set avg=True for average across channels."""
    raw.compute_psd().plot(picks=picks, average=avg)


def ica(raw, n_components=15, montage=None):
    """Fit ICA and plot components safely."""
    from mne.preprocessing import ICA

    # Adjust n_components if too large
    n_comps = min(n_components, raw.info['nchan'])
    ica = ICA(n_components=n_comps, random_state=97)
    ica.fit(raw)

    # Plot safely
    if montage is not None:
        try:
            ica.plot_components()  # scalp topographies
        except Exception as e:
            print(f"⚠️ Could not plot topographies: {e}")
            ica.plot_sources(raw)  # fallback to time courses
    else:
        print("⚠️ Montage missing. Plotting ICA time courses instead.")
        ica.plot_sources(raw)

    return ica



def epochs(raw, event_id=2, tmin=-1, tmax=2, baseline=(-0.5, 0), reject=None, plot=True, events_tsv=None):
    """
    Create epochs from annotations.

    Parameters
    ----------
    raw : mne.io.Raw
        Preprocessed EEG data.
    event_id : int or dict
        Event ID(s) to extract epochs.
    tmin : float
        Start time before event (s).
    tmax : float
        End time after event (s).
    baseline : tuple
        Baseline correction window.
    reject : dict
        Rejection criteria.
    plot : bool
        Whether to plot epochs and PSD.

    Returns
    -------
    epochs : mne.Epochs
        Extracted epochs.
    """
    if events_tsv:
        events_df = pd.read_csv(events_tsv, sep='\t')
        sfreq = raw.info['sfreq']

        # Map string labels to integer event codes
        labels = events_df['value'].unique()
        label2code = {label: i+1 for i, label in enumerate(labels)}

        events_array = np.column_stack([
            (events_df['onset'] * sfreq).astype(int),
            np.zeros(len(events_df), dtype=int),  # previous sample placeholder
            events_df['value'].map(label2code).astype(int)       # event code
        ])

        events = events_array
        event_dict = label2code

    else:
      # fallback to annotations in EEG file
      events, event_dict = mne.events_from_annotations(raw)
      print(f"Events found: {events.shape}, {event_dict}")

    if not len(events):
        raise RuntimeError("No events found in raw data.")

    if len(events) > 0:
      eid = select_event_id(event_dict, event_id)

    epochs = mne.Epochs(raw, events, event_id=eid,
                        tmin=tmin, tmax=tmax,
                        baseline=baseline,
                        preload=True,
                        reject=reject)
    # epochs = mne.Epochs(raw, events, event_id=event_id,
    #                     tmin=tmin, tmax=tmax,
    #                     baseline=baseline, preload=True,
    #                     reject=reject)

    if plot:
        epochs.plot(n_epochs=4)
        epochs.compute_psd().plot(picks="eeg")

    return epochs


def pltbands(epochs, bands=None):
    """
    Plot EEG frequency bands topomap.

    Parameters
    ----------
    epochs : mne.Epochs
        Epochs object.
    bands : list of tuple, optional
        List of (fmin, fmax, label). Default includes Delta, Theta, Alpha, Beta, Gamma.
    """
    if bands is None:
        bands = [
            (1, 4, "Delta"),
            (4, 8, "Theta"),
            (8, 12, "Alpha"),
            (12, 30, "Beta"),
            (30, 45, "Gamma")  # or 30–80 if you want full gamma
        ]

    epochs.plot_psd_topomap(bands=bands, vlim="joint")
