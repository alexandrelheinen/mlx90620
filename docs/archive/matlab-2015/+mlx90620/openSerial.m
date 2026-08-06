% Copyright (C) 2015-2026 Alexandre Loeblein Heinen
% Copyright (C) 2015-2026 Clyvian Ribeiro Borges
function s = openSerial()
  % OPENSERIAL Open a serialport connection to the Arduino firmware.
  %
  %   s = mlx90620.openSerial()
  %
  %   Requires MATLAB R2019b+ (serialport). Baud and port come from
  %   mlx90620.serialSettings().

  cfg = mlx90620.serialSettings();
  s = serialport(cfg.port, cfg.baud);
  configureTerminator(s, "LF");
  % Give the Uno time to reset after the USB/CDC open.
  pause(1.5);
end
