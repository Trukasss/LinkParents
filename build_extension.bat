set blender="C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
set current_dir=%~dp0
if exist dist rd /s /q dist
mkdir dist
%blender% --command extension build --source-dir "%current_dir%src" --output-dir "%current_dir%dist"