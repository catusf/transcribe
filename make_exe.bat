rem  -F
pyinstaller --onedir --add-data "C:\Python312\envs\videosubs\Lib\site-packages\whisper\assets\:./whisper/assets/" transcribe.py

