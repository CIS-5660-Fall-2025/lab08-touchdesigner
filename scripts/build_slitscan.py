"""Build CHRONOFOLD in a new TouchDesigner project.

Built and runtime-checked in TouchDesigner 2025.33230.
Run inside TD's Textport, not with a standalone Python interpreter:

    import runpy
    tools = runpy.run_path('/absolute/path/to/scripts/build_slitscan.py')
    effect = tools['build']()

This creates nodes only. It does not save files, delete existing nodes, open
windows, access devices, install software, or change application preferences.
"""

RESOLUTION = 768
COMPONENT_NAME = 'chronofold'


def _par(node, name):
    parameter = getattr(node.par, name, None)
    if parameter is None:
        raise RuntimeError(f'{node.path}: required parameter {name!r} not found')
    return parameter


def _set(node, **values):
    for name, value in values.items():
        _par(node, name).val = value


def _expr(node, **expressions):
    for name, value in expressions.items():
        _par(node, name).expr = value


def _menu(node, name, token, label_prefix=None):
    """Check menu availability rather than silently use a different option."""
    parameter = _par(node, name)
    if token in parameter.menuNames:
        parameter.val = token
        return
    if label_prefix:
        matches = [i for i, label in enumerate(parameter.menuLabels)
                   if label.lower().startswith(label_prefix.lower())]
        if len(matches) == 1:
            parameter.menuIndex = matches[0]
            return
    raise RuntimeError(
        f'{node.path}.{name}: expected {token!r}; '
        f'available options: {list(zip(parameter.menuNames, parameter.menuLabels))}'
    )


def _node(parent, kind, name, x, y, comment=''):
    node = parent.create(kind, name)
    node.nodeX, node.nodeY = x, y
    node.comment = comment
    node.viewer = True
    if node.isTOP:
        _set(node, outputresolution='custom', resolutionw=RESOLUTION,
             resolutionh=RESOLUTION, format='rgba8fixed')
    return node


def _connect(source, destination, index=None):
    # Output connections append when the destination accepts multiple inputs.
    target = destination if index is None else destination.inputConnectors[index]
    source.outputConnectors[0].connect(target)


def _number(page, kind, name, label, default, low, high):
    parameter = getattr(page, kind)(name, label=label)[0]
    parameter.default = default
    parameter.val = default
    parameter.min, parameter.max = low, high
    parameter.normMin, parameter.normMax = low, high
    parameter.clampMin = parameter.clampMax = True


def _choice(page, name, label, names, labels):
    parameter = page.appendMenu(name, label=label)[0]
    parameter.menuNames = names
    parameter.menuLabels = labels
    parameter.default = names[0]
    parameter.val = names[0]


def _controls(effect):
    page = effect.appendCustomPage('Slit Scan')
    _choice(page, 'Scanmode', 'Scan direction',
            ['horizontal', 'vertical', 'radial'],
            ['Horizontal', 'Vertical', 'Radial'])
    _choice(page, 'Quantize', 'Time map style',
            ['smooth', 'position', 'value'],
            ['Smooth', 'Stepped positions (tutorial)', 'Stepped values'])
    _number(page, 'appendInt', 'Historyframes', 'History frames', 120, 2, 180)
    _number(page, 'appendFloat', 'Amount', 'Time distortion', 1.0, 0.0, 1.0)
    _number(page, 'appendInt', 'Steps', 'Map divisions', 18, 2, 96)
    _number(page, 'appendFloat', 'Speed', 'Animation speed', 1.0, 0.1, 2.5)
    reverse = page.appendToggle('Reverse', label='Reverse time direction')[0]
    reverse.default = reverse.val = False


def _source(effect):
    source = _node(effect, 'baseCOMP', 'source', -650, 200,
                   'Original procedural input: animated cyan, amber and ivory arcs.')
    background = _node(source, 'constantTOP', 'navy_background', -400, 250)
    _set(background, colorr=0.015, colorg=0.025, colorb=0.05, alpha=1)
    layers = [background]
    # Radius, border width, color, phase, rotation speed.
    shapes = [
        (0.32, 0.010, (0.12, 0.85, 0.95), 0.0, 42),
        (0.28, 0.008, (0.35, 0.63, 0.85), 0.7, -38),
        (0.24, 0.016, (1.00, 0.49, 0.16), 1.8, -57),
        (0.20, 0.007, (0.92, 0.94, 0.84), 2.7, 66),
        (0.15, 0.011, (0.12, 0.85, 0.95), 3.6, 76),
        (0.10, 0.014, (1.00, 0.49, 0.16), 5.0, -92),
    ]
    time = '(absTime.seconds * parent(2).par.Speed.eval())'
    for index, (radius, width, color, phase, spin) in enumerate(shapes):
        ring = _node(source, 'circleTOP', f'orbit_{index + 1}', -400,
                     90 - index * 130, 'An animated arc, generated with a native Circle TOP.')
        for parameter in ('radiusunit', 'centerunit', 'borderwidthunit'):
            _menu(ring, parameter, 'fraction')
        _set(ring, radiusx=radius, radiusy=radius * 0.72, fillalpha=0,
             fillcolorr=0, fillcolorg=0, fillcolorb=0,
             borderr=color[0], borderg=color[1], borderb=color[2],
             borderalpha=1, borderwidth=width, bgalpha=0,
             bgcolorr=0, bgcolorg=0, bgcolorb=0,
             beginarcangle=0, endarcangle=290 + index * 8,
             antialias=True, multrgbbyalpha=True)
        _expr(ring,
              centerx=f'0.12 * math.sin({time} * 1.21 + {phase})',
              centery=f'0.10 * math.cos({time} * 1.43 + {phase})',
              rotate=f'{spin} * {time} + {phase * 40}')
        layers.append(ring)
    composite = _node(source, 'compositeTOP', 'combine_orbits', -80, 80)
    _set(composite, operand='add')
    for layer in layers:
        _connect(layer, composite)
    output = _node(source, 'outTOP', 'out1', 170, 80)
    _connect(composite, output)
    _set(source, opviewer='out1')
    return source


def build(parent_path='/project1'):
    """Create an inspectable native TOP network; refuse to replace prior work."""
    import td

    parent = td.op(parent_path)
    if parent is None or not parent.isCOMP:
        raise RuntimeError(f'A parent component is required: {parent_path}')
    if parent.op(COMPONENT_NAME) is not None:
        raise RuntimeError(f'{parent_path}/{COMPONENT_NAME} already exists; nothing changed.')

    effect = _node(parent, 'baseCOMP', COMPONENT_NAME, 0, 0,
                   'CHRONOFOLD | CIS 5660 Lab 08 | editable native TOP slit-scan study')
    _controls(effect)
    _source(effect)

    source_out = _node(effect, 'selectTOP', 'source_image', -420, 200,
                       'Live input image, before any temporal distortion.')
    _set(source_out, top='source/out1')

    frames = _node(effect, 'constantCHOP', 'history_frames', -420, 430,
                   'One shared frame-count channel, following the tutorial reference pattern.')
    _set(frames, const0name='frames')
    _expr(frames, const0value='parent().par.Historyframes.eval()')

    history = _node(effect, 'texture3dTOP', 'frame_history', -150, 200,
                    'Ring buffer. At 768 x 768 RGBA8, 120 slices use about 270 MiB.')
    _set(history, type='texture3d', active=True, step=1, prefill=False)
    _expr(history, cachesize="int(op('history_frames')['frames'][0])")
    _connect(source_out, history)

    keys = _node(effect, 'tableDAT', 'ramp_keys', -650, -210)
    keys.clear()
    keys.appendRow(['pos', 'r', 'g', 'b', 'a'])
    keys.appendRow([0, 0, 0, 0, 1])
    keys.appendRow([1, 1, 1, 1, 1])

    ramp = _node(effect, 'rampTOP', 'scan_ramp', -420, -90,
                 'Brightness chooses time: black is older; white is the current frame.')
    _set(ramp, dat='ramp_keys', interp='linear', extendleft='hold', extendright='hold',
         format='rgba16float')
    _expr(ramp, type='parent().par.Scanmode.eval()')

    quantize = _node(effect, 'limitTOP', 'quantize_map', -150, -90,
                     'Position ceiling reproduces the lesson; value ceiling gives concentric radial bands.')
    _set(quantize, mintype='clamp', maxtype='clamp', min=0, max=1,
         format='rgba16float')
    _expr(quantize,
          quantpos="'ceiling' if parent().par.Quantize.eval() == 'position' else 'off'",
          quantvalue="'ceiling' if parent().par.Quantize.eval() == 'value' else 'off'",
          posstep='1.0 / parent().par.Steps.eval()',
          vstep='1.0 / parent().par.Steps.eval()')
    _connect(ramp, quantize)

    time_map = _node(effect, 'nullTOP', 'time_map', 90, -90,
                     'Inspect this grayscale map alongside the final output.')
    _set(time_map, format='rgba16float')
    _connect(quantize, time_map)

    machine = _node(effect, 'timemachineTOP', 'slit_scan', 350, 200,
                    'Input 0: history texture. Input 1: grayscale time map. No spatial displacement.')
    _menu(machine, 'blackoffsetunit', 'indices')
    _menu(machine, 'whiteoffsetunit', 'indices')
    _set(machine, samplemode='depthoffset', sampleunits='natural', wcoord=0)
    span = "(int(op('history_frames')['frames'][0]) - 1) * parent().par.Amount.eval()"
    _expr(machine,
          blackoffset=f'0 if parent().par.Reverse.eval() else -({span})',
          whiteoffset=f'-({span}) if parent().par.Reverse.eval() else 0')
    _connect(history, machine, 0)
    _connect(time_map, machine, 1)

    final = _node(effect, 'outTOP', 'out1', 610, 200,
                  'Final output. Allow History frames to accumulate after opening or resizing the cache.')
    _connect(machine, final)
    _set(effect, opviewer='out1')
    instructions = _node(effect, 'textDAT', 'READ_ME', 100, 430)
    instructions.text = (
        'CHRONOFOLD / a slit-scan study\n\n'
        'Select the chronofold component and open its Slit Scan parameter page.\n'
        'Try Horizontal + Smooth, Vertical + Stepped positions, and Radial + Stepped values.\n'
        'Time distortion = 0 is the unwarped input. Reverse swaps oldest/newest ends.\n'
        'Wait for History frames after startup or a cache-size change.\n'
        'Input animation uses Circle TOPs; all media is generated inside this project.\n'
        'Tutorial: https://youtu.be/fz_PxG5KoNE\n'
    )
    effect.store('lab08_builder', 'chronofold-v1')
    for node in effect.children:
        node.nodeWidth = 150
        if node.isTOP or node.isCOMP:
            node.nodeHeight = 125
    final.nodeWidth = final.nodeHeight = 240
    instructions.viewer = False
    print(f'Built {effect.path}. Let the history fill, then inspect the output.')
    return effect


if __name__ == '__main__':
    raise SystemExit('Run build() inside TouchDesigner. This file is not a standalone renderer.')
