% Copyright (C) 2015-2026 Alexandre Loeblein Heinen
% Copyright (C) 2015-2026 Clyvian Ribeiro Borges
function y = imageProcess(x, n, r)
  % IMAGEPROCESS Upscale and median-filter a thermal frame.
  %
  %   y = mlx90620.imageProcess(x, n, r) scales image x by integer factor n
  %   using kron replication, then applies a median filter of window [r r].
  %   Requires the Image Processing Toolbox (medfilt2).

  y = kron(double(x), ones(n));
  y = medfilt2(y, [r, r]);
end
