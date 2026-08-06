% Copyright (C) 2015-2026 Alexandre Loeblein Heinen
% Copyright (C) 2015-2026 Clyvian Ribeiro Borges
% Realtime acquisition loop that also writes filtered frames to PNG files.
% CentraleSupelec Projet de Conception - 2014/2015 Seq. 8
% Alexandre Loeblein Heinen | Clyvian Ribeiro Borges
%
% Demo mode: setenv('MLX90620_DEMO','1')

%% Device initialisation
clc;
cols = 4;
rows = 16;
image = zeros(rows, cols);
demo = mlx90620.useDemoMode();
s = [];

if demo
  set(handles.dispositif, 'String', 'Demo mode (synthetic frames)');
else
  cfg = mlx90620.serialSettings();
  set(handles.dispositif, 'String', strcat('Arduino Uno - ', {' '}, cfg.port));
  s = mlx90620.openSerial();
end

%% Read loop with per-frame PNG export of the filtered axis
while strcmp(get(handles.pushbutton2, 'Enable'), 'on')
  if demo
    image = mlx90620.demoFrame(rows, cols);
  else
    i = 1;
    while i <= rows
      j = 1;
      while j <= cols
        pixel = mlx90620.readNumericLine(s);
        image(rows - i + 1, j) = pixel;
        j = j + 1;
      end
      i = i + 1;
    end
  end

  axes(handles.axes1);
  imagesc(image);
  caxis([15, 40]);
  colorbar;
  title('Original image');

  n = round(str2double(get(handles.edit1, 'String')));
  r = round(str2double(get(handles.edit2, 'String')));
  imageProc = mlx90620.imageProcess(image, n, r);
  axes(handles.axes2);
  imagesc(imageProc);
  caxis([15, 40]);
  colorbar;
  title('Filtered image');
  pause(0.1);

  F = getframe(handles.axes2);
  Frame = frame2im(F);
  imwrite(Frame, strcat('filtre_', datestr(now, 'dd.mm.yy_HH.MM.SS.FFF'), '.png'));
end

saveas(gcf, strcat('camera_', datestr(now, 'dd.mm.yy_HH.MM.SS'), '.png'));
if ~isempty(s)
  clear s;
end
