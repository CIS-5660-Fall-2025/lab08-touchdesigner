# Rebuilding and validating CHRONOFOLD

The submitted `chronofold.toe` is ready to open. Python is only needed if you
want to regenerate the editable network or export a new set of comparisons.
The source code targets TouchDesigner **2025.33230**, including that build's
Constant CHOP sequence parameters and Limit TOP parameter names.

## Build

In a new TouchDesigner project, open **Dialogs → Textport and DATs** (Alt+T).
Run the following with an absolute path to this repository:

```python
import runpy
builder = runpy.run_path('/absolute/path/to/lab08-touchdesigner/scripts/build_slitscan.py')
effect = builder['build']()
effect.op('out1').openViewer()
```

The builder creates `/project1/chronofold`. It refuses to replace an existing
component with that name. It does not delete the default project, access a
camera, open a network service, or save automatically. The generated `.toe`
contains native operators and expressions; the Python files are not needed
when opening the submitted project.

The source contains six animated Circle TOPs, a Constant TOP background, a
Composite TOP, and an Out TOP. The outer effect contains the history buffer,
grayscale ramp, Limit TOP, shared frame-count CHOP, and Time Machine output.
There are 21 operators inside the `chronofold` component in total.

## Capture and validation

With playback running, allow at least the configured number of history frames
to cook. Then run:

```python
checks = runpy.run_path('/absolute/path/to/lab08-touchdesigner/scripts/capture_results.py')
report = checks['capture']('/absolute/path/to/a/capture/directory')
```

The helper checks for operator and script errors, a nonempty source, matching
history depth, zero-distortion identity, and a measurable change in every
preset. It freezes the history during the comparison so all variants read the
same buffered animation. It restores the controls and the buffer's active state
afterward, including when a check fails. The PNGs come directly from TOP outputs.

`validation.json` records what was actually measured. A failed run records its
failure and never sets `runtime_verified` to `true`. The supplied reports are
from the final network and from reopening the saved project. Visual inspection
and an actual screenshot of the network editor complement these checks.

## Save

Use **File → Save As** to choose a new `.toe` path. Alternatively:

```python
checks['save_project']('/absolute/path/to/a/new_project.toe')
```

The helper refuses to overwrite an existing file. TouchDesigner's default
incremental-save preferences may create a numbered companion file; the
un-numbered `chronofold.toe` in this repository is a complete copy and was
verified by reopening it.

## Tuning

- Start with `Amount = 0` to compare the undistorted source.
- Increase `Amount` to introduce progressively older frames.
- Use the horizontal or vertical direction with position quantization to
  reproduce the lesson's spatial stepping.
- Use a radial ramp with value quantization to form concentric time bands.
- After changing `Historyframes`, let the buffer refill before judging it.
- The time map uses RGBA16F to avoid limiting a smooth ramp to 256 gray levels;
  the image history uses RGBA8 to keep its memory footprint modest.
