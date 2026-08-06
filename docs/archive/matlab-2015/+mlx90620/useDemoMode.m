% Copyright (C) 2015-2026 Alexandre Loeblein Heinen
% Copyright (C) 2015-2026 Clyvian Ribeiro Borges
function enabled = useDemoMode()
  % USEDEMOMODE True when acquisition should use synthetic frames.
  %
  %   Enabled when environment variable MLX90620_DEMO is "1" / "true" / "yes"
  %   (case-insensitive). Useful for CI-free UI checks without hardware.

  flag = lower(strtrim(getenv('MLX90620_DEMO')));
  enabled = any(strcmp(flag, {'1', 'true', 'yes', 'on'}));
end
