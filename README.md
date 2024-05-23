# create_subtitles
This set of tools downloads videos, transcribe audio in videos, translates the subtitles and saves them in SRT format. Thus it can help you to study foreign languages.


# Requirements

- Python 3

- Better to install a separate environment

```
python -m venv /path/to/env/name
```

- `ffmpeg` needs to be installed and path set

- Python packages need installed

```python
pip install -r requirements.txt
```


# Execute

- Edit `run_transcribe_server.bat and `run_translate_subtitles_server.bat` to point to correct location of the `activate.bat` batch file installed by the above Python

- Copy videos to transcribe and translate to `./downloads` folder

- Double click these two batch files in Explorer to start them