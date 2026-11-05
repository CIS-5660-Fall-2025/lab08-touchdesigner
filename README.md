# CHRONOFOLD

**CIS 5660 — Lab 08: TouchDesigner**

Jingyu Fu

A slit-scan effect made from six animated arcs. Instead of a camera feed, the
input is generated with Circle TOPs, so the project runs without external media.

## Results

| Horizontal scan | Horizontal scan with steps |
| --- | --- |
| ![Horizontal scan](screenshots/horizontal_smooth.png) | ![Stepped horizontal scan](screenshots/horizontal_stepped.png) |

| Vertical scan with steps | Radial scan |
| --- | --- |
| ![Stepped vertical scan](screenshots/vertical_stepped.png) | ![Radial scan](screenshots/radial_bands.png) |

The smooth ramp bends the arcs continuously. Adding steps breaks them into
separate slices. A radial ramp makes those time differences spread outward
from the center.

## How it works

```text
Animated arcs → Texture 3D ─────┐
                              ├→ Time Machine → Out
Ramp → Limit ──────────────────┘
```

Texture 3D stores the last 120 frames. Time Machine uses the grayscale ramp to
choose which frame to show at each pixel: darker areas show older frames,
while lighter areas show more recent ones. Limit quantizes the ramp to create
the stepped versions. A Constant CHOP keeps the cache size and time offsets
linked to the same frame count.

## Open and adjust

Open [`chronofold.toe`](chronofold.toe) in TouchDesigner and let it play for a
couple of seconds to fill the history. Right-click `out1` and select **View**
for a larger preview.

To change settings, go up one level with **U**, select `chronofold`, press **P**,
and open the **Slit Scan** parameter page.

- **Scan direction:** horizontal, vertical, or radial.
- **Time map style / Map divisions:** smooth or stepped, with adjustable slice size.
- **History frames / Time distortion:** adjust how far back the effect samples.
- **Animation speed / Reverse time direction:** change the motion and the order of time.

Built with TouchDesigner **2025.33230** at **768 × 768**.

Based on the [course slit-scan tutorial](https://youtu.be/fz_PxG5KoNE), with a
procedural input and additional scan patterns.
