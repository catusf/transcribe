rem  -F --onedir  --add-data "./ffmpeg.exe:." --add-data "./ffprobe.exe:." --add-data "C:\Python312\envs\videosubs\Lib\site-packages\whisper\assets\:./whisper/assets/" 
pyinstaller --noconfirm --onedir --contents-directory "." --add-data "./downloads/README.txt:./downloads/" --add-data "./downloads/subs/README.txt:./downloads/subs/"  --add-data "./ffmpeg.exe:." --add-data "./ffprobe.exe:." --add-data "C:\Python312\envs\videosubs\Lib\site-packages\whisper\assets\:./whisper/assets/" transcribe.pyw

