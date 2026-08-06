% Realtime acquisition loop for the MLX90620 GUIDE UI.
% CentraleSupélec Projet de Conception — 2014/2015 Seq. 8
% Alexandre Loeblein Heinen | Clyvian Ribeiro Borges
%
% Expects GUIDE `handles` in the caller workspace. Reads 64 temperatures per
% frame from Serial (see docs/BUILD.md) and updates the raw/filtered axes.

%% Device initialisation
clc;
com = 'COM3';  % Override for your OS, e.g. '/dev/ttyACM0' on Linux.
set(handles.dispositif, 'String', strcat('Arduino Uno - ', {' '}, com));
s = serial(com); %#ok<*SERIAL>  % Legacy API; serialport migration is planned.
fopen(s);
pause(1);

%% Frame buffers (sensor is 16x4 in "wide" / vertical orientation)
cols = 4;
rows = 16;
image = zeros(rows, cols);

% Reserved mosaic buffer (unused in realtime mode; kept for UI parity).
numIm = 3;
globalImage = cell(numIm);
for i = 1:numIm
  for j = 1:numIm
    globalImage{i, j} = image;
  end
end

%% Read loop — continues while the Stop button remains enabled
while strcmp(get(handles.pushbutton2, 'Enable'), 'on')
  i = 1;
  while i <= rows
    j = 1;
    while j <= cols
      while s.BytesAvailable == 0
      end
      pixel = str2double(fscanf(s));
      image(rows - i + 1, j) = pixel;
      j = j + 1;
    end
    i = i + 1;
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
end

saveas(gcf, strcat('camera_', datestr(now, 'dd.mm.yy_HH.MM.SS'), '.png'));
fclose(s);
delete(s);
clear s;
