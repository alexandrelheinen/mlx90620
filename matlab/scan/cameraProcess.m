% Copyright (C) 2015-2026 Alexandre Loeblein Heinen
% Copyright (C) 2015-2026 Clyvian Ribeiro Borges
% Scan / mosaic acquisition loop for the MLX90620 GUIDE UI.
% CentraleSupelec Projet de Conception - 2014/2015 Seq. 8
% Alexandre Loeblein Heinen | Clyvian Ribeiro Borges
%
% Waits for scan markers <= -300 (see docs/BUILD.md), then reads 64 temperatures
% and assembles a mosaic from servo pose indices.
%
% Demo mode: setenv('MLX90620_DEMO','1') synthesises a small mosaic.

%% Device initialisation
clc;
cols = 4;
rows = 16;
image = zeros(rows, cols);
numIm1 = 1;
numIm2 = 4;
globalImage = cell(numIm1, numIm2);
for i = 1:numIm1
  for j = 1:numIm2
    globalImage{i, j} = image;
  end
end

demo = mlx90620.useDemoMode();
s = [];
demoCol = 0;

if demo
  set(handles.dispositif, 'String', 'Demo mode (synthetic mosaic)');
else
  cfg = mlx90620.serialSettings();
  set(handles.dispositif, 'String', strcat('Arduino Uno - ', {' '}, cfg.port));
  s = mlx90620.openSerial();
end

%% Read loop - continues while the Stop button remains enabled
while strcmp(get(handles.pushbutton2, 'Enable'), 'on')
  if demo
    r = 0;
    c = demoCol;
    set(handles.temp, 'String', strcat(num2str(r), 'x', num2str(c)));
    image = mlx90620.demoFrame(rows, cols) + c;
    demoCol = mod(demoCol + 1, numIm2);
  else
    i = 1;
    flag = 0;  % 0 = waiting for marker; 1 = reading temperatures
    r = 0;
    c = 0;

    while i <= rows
      j = 1;
      while j <= cols
        pixel = mlx90620.readNumericLine(s);

        if pixel <= -300 && flag == 0
          ind = abs(pixel + 300);
          c = mod(ind, 10);       % column index from marker
          r = floor(ind / 10);    % row index from marker
          set(handles.temp, 'String', strcat(num2str(r), 'x', num2str(c)));
          flag = 1;
        elseif flag == 1
          image(rows - i + 1, j) = pixel;
          j = j + 1;
        end
      end
      i = i + 1;
    end
  end

  globalImage{numIm1 - r, numIm2 - c} = image;

  % Redraw only after the last mosaic tile arrives.
  if r == (numIm1 - 1) && c == (numIm2 - 1)
    matrice = cell2mat(globalImage);
    axes(handles.axes1);
    imagesc(matrice);
    caxis([15, 40]);
    colorbar;
    title('Original image');

    n = round(str2double(get(handles.edit1, 'String')));
    rad = round(str2double(get(handles.edit2, 'String')));
    imageProc = mlx90620.imageProcess(matrice, n, rad);
    axes(handles.axes2);
    imagesc(imageProc);
    caxis([15, 40]);
    colorbar;
    title('Filtered image');
  end
  pause(0.1);
end

if ~isempty(s)
  clear s;
end
