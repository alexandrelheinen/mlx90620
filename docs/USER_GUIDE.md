# User guide (English)

> Translation of the 2015 French operator note [`docs/archive/mode_demploi.pdf`](archive/mode_demploi.pdf),
> updated for the current repository paths and tooling.

## Prerequisites

1. Build and upload firmware with PlatformIO (see [`BUILD.md`](BUILD.md)):
   - Realtime: `pio run -d firmware/examples/realtime -t upload`
   - Scan: `pio run -d firmware/examples/scan -t upload`
2. MATLAB with Image Processing Toolbox.
3. From the `matlab/` folder, run `setupPaths` (or open a UI — openers add the package root).

Arduino IDE users: copy `firmware/lib/MLX90620` and `firmware/external/I2Cmaster` into the
IDE libraries folder (historically `C:/Program Files/Arduino/libraries` on Windows).

## Realtime mode

1. Upload the **realtime** sketch to the Uno.  
2. Open `matlab/realtime/interface.m` (GUIDE UI; companion `interface.fig`).  
3. Set **Expansion factor** and **Median radius** for filtering.  
4. Press **Start** (`Marche` on the original French figure) to open the serial link and
   display frames: left = raw temperatures, right = filtered.  
5. Press **Stop** (`Arrêt`) before closing the window.

## Scan mode (balayage)

1. Upload the **scan** sketch.  
2. Open `matlab/scan/interface.m`.  
3. The UI is equivalent to realtime, plus a label showing the current mosaic tile
   coordinates (`row x col`).  
4. Start/Stop behave as in realtime.

## Serial port

Default ports come from `mlx90620.serialSettings`:

| OS | Default |
|----|---------|
| Windows | `COM3` |
| Linux / macOS | `/dev/ttyACM0` |

Override without editing scripts:

```matlab
setenv('MLX90620_PORT', 'COM5')          % Windows example
setenv('MLX90620_PORT', '/dev/ttyUSB0')  % Linux example
```

## Demo mode (no hardware)

```matlab
setenv('MLX90620_DEMO', '1')
```

Start the UI as usual; acquisition loops feed synthetic frames so filtering/UI can be
exercised without an Arduino.

## Important warnings (from the original guide)

1. **Never close the GUIDE window before Stop.** Closing while the serial session is
   active can leave the port busy until MATLAB is restarted and the board is reset.  
2. Prefer Stop → then close.  
3. If the wrong COM port is selected, set `MLX90620_PORT` (or historically edit the
   port string in `cameraProcess.m` — no longer required).

## Filter parameters

Typical values used during the 2015 evaluation were expansion \(n = 4\) and median
radius \(m = 4\) (sometimes \(m = 6\) for demo figures). Adjust live from the UI fields.
