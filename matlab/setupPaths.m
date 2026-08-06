% Copyright (C) 2015-2026 Alexandre Loeblein Heinen
% Copyright (C) 2015-2026 Clyvian Ribeiro Borges
function setupPaths()
  % SETUPPATHS Add the MATLAB package root to the path.
  %
  %   Call once per MATLAB session before opening the realtime or scan UIs:
  %
  %       cd matlab
  %       setupPaths
  %       edit realtime/interface.m

  thisDir = fileparts(mfilename('fullpath'));
  addpath(thisDir);
end
