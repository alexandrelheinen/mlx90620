% Copyright (C) 2015-2026 Alexandre Loeblein Heinen
% Copyright (C) 2015-2026 Clyvian Ribeiro Borges
function cfg = serialSettings()
  % SERIALSETTINGS Return default serial port and baud for the Arduino link.
  %
  %   cfg = mlx90620.serialSettings()
  %
  %   Override the port with environment variable MLX90620_PORT
  %   (e.g. setenv('MLX90620_PORT','/dev/ttyACM0')).

  cfg.baud = 9600;
  cfg.port = getenv('MLX90620_PORT');
  if isempty(cfg.port)
    if ispc
      cfg.port = 'COM3';
    else
      cfg.port = '/dev/ttyACM0';
    end
  end
end
