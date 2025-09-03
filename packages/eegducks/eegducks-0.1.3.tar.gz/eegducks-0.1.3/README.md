# eegducks 🦆

A beginner-friendly wrapper around MNE for quick EEG analysis.

## Example

```python
import eegducks as ed

# Specify Channel location file 
chan="/content/s3/ch.tsv"

# Import the eeg file
raw = eds.load("/content/s3/eeg.set", locinf=chan)


# Quick Plotting
eds.plot(raw)
eds.psdplt(raw, avg=True)

# Specify Events for Epochs
ev = "/content/s3/ev.tsv"
eds.epochs(raw, events_tsv=ev)


# Run an ICA
eds.ica(raw)
eds.psdplt(raw, avg=True)
