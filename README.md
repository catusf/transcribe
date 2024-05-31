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

# Non-windows installations

- `requirements.txt` conatains 2 packages that are not available on non-Windows machines, please remove these two lines

    - `wxPython`

    - `Gooey`

# Execute

- First, copy videos to transcribe and translate to `./downloads/` folder

## Console 

- Run `transcribe.py` 

## GUI (on Windows only) 

- Run `transcribe.pyw` 

## Output

- The output will be in `./downloads/subs/` folder
