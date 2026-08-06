% Copyright (C) 2015-2026 Alexandre Loeblein Heinen
% Copyright (C) 2015-2026 Clyvian Ribeiro Borges
function value = readNumericLine(s)
  % READNUMERICLINE Read one terminator-delimited line and parse as double.
  %
  %   value = mlx90620.readNumericLine(s)
  %
  %   s must be a serialport object configured with LF terminators.

  value = str2double(readline(s));
end
