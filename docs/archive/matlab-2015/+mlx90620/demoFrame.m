% Copyright (C) 2015-2026 Alexandre Loeblein Heinen
% Copyright (C) 2015-2026 Clyvian Ribeiro Borges
function frame = demoFrame(rows, cols, t)
  % DEMOFRAME Synthetic 16x4-style thermal frame for hardware-free UI demos.
  %
  %   frame = mlx90620.demoFrame()
  %   frame = mlx90620.demoFrame(rows, cols, t)
  %
  %   When t is omitted, uses seconds since an arbitrary epoch so successive
  %   calls animate slowly.

  if nargin < 1 || isempty(rows)
    rows = 16;
  end
  if nargin < 2 || isempty(cols)
    cols = 4;
  end
  if nargin < 3 || isempty(t)
    t = now * 24 * 3600;
  end

  [X, Y] = meshgrid(1:cols, 1:rows);
  % Warm blob drifting across a cooler background (~20-35  degC).
  cx = 1.5 + 1.5 * sin(0.4 * t);
  cy = 8 + 4 * cos(0.25 * t);
  frame = 22 + 10 * exp(-((X - cx).^2 + ((Y - cy) / 3).^2) / 4);
end
