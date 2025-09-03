# eegducks 🦆

A beginner-friendly wrapper around MNE for quick EEG analysis.

## Example

```python
import eegducks as ed

raw = ed.load_and_preprocess("subject1_raw.fif")
ica = ed.run_ica(raw)
epochs = ed.make_epochs(raw)
ed.plot_bands(epochs)
