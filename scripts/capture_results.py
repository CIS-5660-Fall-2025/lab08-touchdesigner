"""Inspect and capture actual TouchDesigner output after the history is warm.

This helper must run in TouchDesigner. It does not synthesize screenshots or
claim that unexecuted checks have passed. Network-editor screenshots are taken
separately from the application UI after permission to use the foreground.
"""

import json
from pathlib import Path


PRESETS = [
    ('horizontal_smooth', 'horizontal', 'smooth'),
    ('horizontal_stepped', 'horizontal', 'position'),
    ('vertical_stepped', 'vertical', 'position'),
    ('radial_bands', 'radial', 'value'),
]


def capture(output_dir, effect_path='/project1/chronofold'):
    """Write four actual TOP captures plus numeric validation evidence.

    Run only after at least History frames have cooked. All image variants use
    the same frozen history, making comparisons meaningful. Parameter values
    and the history's active state are restored even when a check fails.
    """
    import td
    import numpy as np

    effect = td.op(effect_path)
    if effect is None:
        raise RuntimeError(f'Missing effect: {effect_path}')
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    final = effect.op('out1')
    history = effect.op('frame_history')
    source = effect.op('source_image')
    time_map = effect.op('time_map')
    names = ('Scanmode', 'Quantize', 'Amount', 'Reverse')
    original = {name: effect.par[name].eval() for name in names}
    original_active = history.par.active.eval()
    report = {'runtime_verified': False, 'effect': effect_path, 'presets': {}}

    try:
        final.cook(force=True)
        report['operator_errors'] = effect.errors(recurse=True)
        report['script_errors'] = effect.scriptErrors(recurse=True)
        report['warnings'] = effect.warnings(recurse=True)
        if report['operator_errors'] or report['script_errors']:
            raise RuntimeError('The network reports errors; inspect validation.json.')

        source_pixels = source.numpyArray(delayed=False).copy()
        report['resolution'] = [source.width, source.height]
        report['history_depth'] = history.depth
        report['history_frames'] = int(effect.par.Historyframes.eval())
        if history.depth != report['history_frames']:
            raise RuntimeError('The history texture depth does not match the frame control.')
        if not np.isfinite(source_pixels).all() or source_pixels[:, :, :3].std() < 0.02:
            raise RuntimeError('The source is empty, invalid, or nearly constant.')
        history.par.active = False
        source.save(str(output_dir / 'source.png'))

        # At zero time span, both offsets select the current buffered image.
        effect.par.Amount = 0
        final.cook(force=True)
        zero = final.numpyArray(delayed=False)
        zero_error = float(np.abs(zero[:, :, :3] - source_pixels[:, :, :3]).mean())
        report['zero_amount_mean_error'] = zero_error
        if zero_error > 2 / 255:
            raise RuntimeError('Zero distortion does not match the source; check offset units.')

        effect.par.Amount = 1
        effect.par.Reverse = False
        for filename, mode, quantization in PRESETS:
            effect.par.Scanmode = mode
            effect.par.Quantize = quantization
            final.cook(force=True)
            pixels = final.numpyArray(delayed=False)
            mask = time_map.numpyArray(delayed=False)[:, :, 0]
            error = float(np.abs(pixels[:, :, :3] - source_pixels[:, :, :3]).mean())
            report['presets'][filename] = {
                'scan_mode': mode,
                'quantization': quantization,
                'mean_difference_from_source': error,
                'time_map_min': float(mask.min()),
                'time_map_max': float(mask.max()),
            }
            if not np.isfinite(pixels).all():
                raise RuntimeError(f'{filename}: nonfinite pixel values')
            if float(mask.max() - mask.min()) < 0.5:
                raise RuntimeError(f'{filename}: time map does not span enough history')
            if error < 0.002:
                raise RuntimeError(f'{filename}: no measurable slit-scan effect; warm the history first')
            final.save(str(output_dir / f'{filename}.png'))
            time_map.save(str(output_dir / f'{filename}_map.png'))
        report['runtime_verified'] = True
    except Exception as error:
        report['failure'] = str(error)
        raise
    finally:
        for name, value in original.items():
            effect.par[name].val = value
        history.par.active = original_active
        final.cook(force=True)
        (output_dir / 'validation.json').write_text(
            json.dumps(report, indent=2), encoding='utf-8')
    print(f'Captured actual TOP images in {output_dir}. Visual review is still required.')
    return report


def save_project(path):
    """Save a new .toe only when explicitly invoked; never overwrite a file."""
    import td

    destination = Path(path).resolve()
    if destination.suffix.lower() != '.toe':
        raise ValueError('The project filename must end in .toe')
    if destination.exists():
        raise FileExistsError(destination)
    if not td.project.save(str(destination)):
        raise RuntimeError('TouchDesigner did not save the project')
    if not destination.is_file() or destination.stat().st_size == 0:
        raise RuntimeError('The saved project is missing or empty')
    return str(destination)
