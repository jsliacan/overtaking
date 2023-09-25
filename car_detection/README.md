## Obtain a video

1. Go to YouTube, get a URL of a video and download it via some website like [https://en.savefrom.net](https://en.savefrom.net). 
2. On Fedora, I use Shotcut to crop out a very short section of the video, e.g. 5sec. Can only export as MP4 IIRC.
3. Use FFMPEG to convert to AVI `ffmpeg -i traffic-opencv.mp4 -vcodec copy -acodec copy traffic-opencv.avi`
4. Move it to `../data` folder (relative to the location of this README)

## Run detection script

Needs `cars.xml` haar cascade file. Make sure you refer to the right video in the script itself (`detect.py`).

```python
python detect.py
```