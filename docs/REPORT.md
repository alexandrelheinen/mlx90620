# Design of a Thermal Camera — Project Report (English)

> **About this document**
>
> English translation and modernization of the original French project report submitted
> for the Supélec / CentraleSupélec *Projet de Conception* evaluation on **12 June 2015**.
> The source PDF is preserved at [`docs/archive/rapport.pdf`](archive/rapport.pdf).
> Paths, library API names, and tooling notes below reflect the **2026** repository layout
> (`firmware/`, `matlab/`, PlatformIO, CI). Sensor maths and serial framing match the 2015 design.

**Authors:** Alexandre Loeblein Heinen, Clyvian Ribeiro Borges  
**Series / group / pair:** Series A, Group 6, Binôme 66  
**Supervisor:** José Picheral  
**Campus:** Gif-sur-Yvette

---

## 1. Introduction

This project analyses and brings up a thermal-camera system. Any body emits infrared
radiation whose spectrum depends on temperature. A thermal camera measures that radiation
in a chosen IR band and maps it to temperatures.

ISO 20473:2007 defines the mid-infrared band as wavelengths between **3 µm and 6 µm**;
that is the band of interest here.

The camera uses an opto-mechanical assembly built around a **Melexis MLX90620** 16×4
infrared array (with on-chip amplification, filtering, and ADC). Two hobby servos can
scan the sensor across a scene so successive frames form a larger mosaic, with a small
time offset between tiles.

The report describes the components, the software developed on Arduino and MATLAB, the
results obtained in realtime and scan modes, and perspectives for later work.

---

## 2. Components

### 2.1 MLX90620

The MLX90620 combines:

- a **16×4** IR array (MLX90670 die),
- a **256-byte EEPROM** (24AA02) holding factory calibration coefficients,
- a **PTAT** sensor (“proportional to absolute temperature”) for ambient temperature.

Factory calibration in EEPROM supports ambient calculation, offset cancellation,
per-pixel sensitivity, emissivity compensation, and object-temperature computation.
Sensor RAM and EEPROM are accessed over **I2C**.

| Parameter | MLX90620 |
|-----------|----------|
| Ambient temperature | −40 to 85 °C |
| Object temperature | −50 to 300 °C |
| Supply | 2.6 V |
| Current | 5–9 mA |
| Refresh | 0.5–64 Hz (project uses a subset) |

### 2.2 Arduino Uno

The Arduino Uno (ATmega328P, 16 MHz, 32 KB flash, 2 KB SRAM) drives I2C to the sensor,
optionally positions servos, computes temperatures, and streams results over USB serial
to the host PC.

### 2.3 Servo motors

Standard hobby servos (≈4–6 V) are positioned from PWM pulses on digital pins. Command
current is negligible; motor current can be hundreds of mA and should not overload the Uno
5 V rail in a durable setup.

### 2.4 Assembly

Servos are commanded from digital pins (**9** pan, **11** tilt in the scan example). The
MLX90620 sits on the Uno I2C bus (A4/A5). Because the sensor prefers **2.6 V** while the
Uno provides 3.3 V, the 2015 rig inserted a **1N4007** diode (~0.6 V drop) in series with
the 3.3 V rail. See the archived PDF for the original wiring figures and prototype photos.

---

## 3. Work performed

### 3.1 MLX90620 library

A dedicated Arduino library (`firmware/lib/MLX90620`) encapsulates bring-up and maths:

1. Read the 256-byte EEPROM calibration dump.  
2. Derive coefficient variables in microcontroller RAM.  
3. Program the oscillator trimming value from EEPROM.  
4. Configure the refresh rate.

I2C reads follow the usual pattern: address slave → send command/parameters → read
response → stop. EEPROM slave address and RAM/register slave address differ (two devices
on the bus).

**Registers of interest** (command `0x02` with start address / step / count):

| Register | Address | Role |
|----------|---------|------|
| Config | 0x92 | Configuration / brown-out flag |
| PTAT | 0x90 | Ambient raw |
| CPIX | 0x91 | Thermal-gradient compensation pixel |
| IR RAM | 0x00, 64 reads | 16×4 frame |

**Ambient temperature** (datasheet quadratic in PTAT):

\[
T_a = \frac{-K_{T1} + \sqrt{K_{T1}^2 - 4 K_{T2}[V_{TH} - PTAT]}}{2 K_{T2}} + 25^\circ C
\]

**Object temperature** per pixel: offset compensation, TGC using CPIX, emissivity
compensation, then Planck-style inversion with per-pixel \(\alpha_{ij}\) (see datasheet
and library comments in `MLX90620.cpp`). Results are transmitted as 64 ASCII lines over
serial (`transmitTemperatures` / `transmitScanFrame`).

> Historical note: the 2015 report describes a procedural API
> (`read_EEPROM_MLX90620`, `calculate_TA`, …). The modern tree exposes the same behaviour
> through the `MLX90620` class (`begin`, `update`, `transmitTemperatures`, …).

### 3.2 Arduino firmware

Firmware responsibilities:

- initialise serial, I2C, sensor, and (scan mode) servos;
- acquire frames and compute temperatures;
- stream data for MATLAB;
- in scan mode, step servos and emit a pose marker before each frame.

**Scan framing.** Before each 64-value frame, firmware sends an “impossible” temperature
marker \(c = -(300 + 10\,i + j)\) with \(c \le -300\). MATLAB recovers pose indices as
\(C = -(c+300)\), column \(= C \bmod 10\), row \(= \lfloor C/10 \rfloor\).

Examples live under `firmware/examples/realtime` and `firmware/examples/scan`.

### 3.3 MATLAB

MATLAB receives serial temperatures, reshapes them to 16×4 (or a mosaic), filters, and
displays results in GUIDE UIs.

Observed noise is largely **salt-and-pepper**. A median filter preserves edges better than
a linear blur, but is weak on a raw 16×4 grid. The pipeline therefore:

1. **Upscales** by integer factor \(n\) via Kronecker replication (`kron`);  
2. Applies a median filter of window \([m, m]\) (`medfilt2`).

\[
T' = F_m(E_n(T)), \quad E_n(T) = T \otimes \mathbf{1}_{n\times n}
\]

Shared helper: `mlx90620.imageProcess`. UIs: `matlab/realtime` and `matlab/scan`.

---

## 4. Results

### 4.1 Realtime

With expansion \(n = 4\) and median radius \(m = 6\) (report figures; preferred tuning
during design was often \(n = 4\), \(m = 4\)), a side view of a hand shows clearer contours
after filtering, and temporal sequences of a waving palm become readable.

### 4.2 Scan (balayage)

The MLX90620 is better suited to single-pose realtime imaging than to large mosaics.
Scan tests (e.g. facing a person) did not yield a sharp assembled image; mechanical FOV
stepping, thermal gradients from motors/electronics, and assembly registration remain
difficult. Filtering still reduced outliers in the UI.

---

## 5. Conclusions and outlook

The primary deliverable was a reusable MLX90620 library so later groups could call a
small API instead of re-deriving I2C and datasheet maths. Image quality remains sensitive
to thermal equilibrium; gradients from on-sensor electronics or servos, optical
contamination, missing decoupling, and supply noise all affect measurements. A recurring
“dead line” of cold pixels was observed at the bottom of frames.

**Future work suggested in 2015 (still relevant):**

- optical/geometry model for efficient non-gappy scan steps (FOV ≈ 60° × 16.4°);
- optionally move heavy maths to MATLAB and stream raw registers if AVR CPU becomes
  limiting;
- improve power integrity for the sensor rail.

---

## 6. Bibliography (from original report)

1. ISO 20473:2007 — Optics and photonics — Spectral bands.  
2. Melexis — MLX90620 16×4 Far Infrared Array datasheet.  
3. Arduino / community documentation for Uno and MLX90620 forum bring-up threads.  
4. Weisstein, E. W. — Kronecker Product (MathWorld).  
5. MathWorks — MATLAB GUI documentation.

EEPROM address maps for \(T_a\) and \(T_{ij}\) coefficients appear in the PDF annexes
(Figures 10–11).

---

## Modernization notes (2026)

| 2015 | 2026 |
|------|------|
| `arduino/libraries/…`, French folder names | `firmware/lib`, `firmware/examples/{realtime,scan}` |
| Procedural helpers + incomplete class | Coherent `MLX90620` C++ API |
| Manual Arduino IDE copy | PlatformIO projects + CI hex artifacts |
| MATLAB GUIDE + Image Processing Toolbox | Python host (`python/`) with PySide6 + pyqtgraph |
| French README / PDF-only docs | English README, BUILD, CONTRIBUTING, AGENTS, this report |

Serial framing (9600 baud, 64 lines/frame, scan markers ≤ −300) is unchanged; see
[`BUILD.md`](BUILD.md). The MATLAB sources are preserved under
[`archive/matlab-2015/`](archive/matlab-2015/).
