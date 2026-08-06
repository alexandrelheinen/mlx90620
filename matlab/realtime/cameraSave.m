% Realtime acquisition loop that also writes filtered frames to PNG files.
% CentraleSupélec Projet de Conception — 2014/2015 Seq. 8
% Alexandre Loeblein Heinen | Clyvian Ribeiro Borges

%% Device initialisation
clc;
com = 'COM3';
set(handles.dispositif, 'String', strcat('Arduino Uno - ', {' '}, com));
s = serial(com); %#ok<*SERIAL>
fopen(s);
pause(1);

%% Frame buffers
cols = 4;
rows = 16;
image = zeros(rows, cols);

numIm = 3;
globalImage = cell(numIm);
for i = 1:numIm
  for j = 1:numIm
    globalImage{i, j} = image;
  end
end

%% Read loop with per-frame PNG export of the filtered axis
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

  F = getframe(handles.axes2);
  Frame = frame2im(F);
  imwrite(Frame, strcat('filtre_', datestr(now, 'dd.mm.yy_HH.MM.SS.FFF'), '.png'));
end

saveas(gcf, strcat('camera_', datestr(now, 'dd.mm.yy_HH.MM.SS'), '.png'));
fclose(s);
delete(s);
clear s;
