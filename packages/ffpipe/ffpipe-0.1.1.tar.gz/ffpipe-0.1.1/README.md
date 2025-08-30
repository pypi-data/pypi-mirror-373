# FFPipe
**FFPipe** is a simple, yet robust tool that acts as a bridge between FFmpeg and Python, allowing you to process video frames in between. 
It is designed to be lightweight and easy to use, making it ideal for developers who want to manipulate video streams 
without diving deep into FFmpeg's complexities.
It is built on top of FFmpeg and uses its powerful capabilities to handle video streams, while providing a simple Python interface for processing frames.
(`ffpipe` uses the [`ffmpeg-python`](https://github.com/kkroening/ffmpeg-python) library under the hood)

## How It Works
![](ffpipe.png)

`ffpipe` leverages FFmpeg’s piping mechanism and seamlessly buffers, transforms, and streams frames, letting developers focus on
processing logic while FFmpeg handles the rest.

Designed for simplicity and flexibility, `ffpipe` requires only a subclass and a `process_frame`/`process_batch` method 
to define custom transformations. Its modular, state-aware architecture keeps video processing clean, efficient, and Pythonic.

The workflow is as follows:
1) The input stream is read and piped to ffmpeg's STDOUT
2) A reader thread reads the frames in the pipe and writes it to the buffer
3) A processing loop (invoked by the `run()` method):
   1) reads frames from the buffer
   2) processes them 
   3) pipes them back to ffmpeg's STDIN
4) The ffmpeg output process reads frames from the STDIN and writes them to the specified output.

## Installation
First things first, you need to install FFmpeg on your system. You can find the installation instructions for your platform
[here](https://ffmpeg.org/download.html). Make sure to add FFmpeg to your system's PATH so that it can be accessed from the command line.

Then you can install `ffpipe` using pip:
```bash
pip install ffpipe
```

## Usage
There are actually two ways to use `ffpipe`:
1. **Subclassing FFPipe**: You can subclass the `FFPipe` class and implement your own processing logic by overriding the `process_frame` or `process_batch` method and the `run()` method will take care of the rest.
2. **Using FFPipe directly**: You can use the `FFPipe` class directly and write your whole processing loop instead of calling the `run()` method (like in method 1).

#### Subclassing FFPipe
```python
import os
import cv2
import numpy as np
from ffpipe import FFPipe

class FrameFlipper(FFPipe):
    """A simple image processor that flips the image horizontally (1) or vertically (0) or both (-1)."""
    def __init__(self, flip_axis: int = 1, **kwargs):
        super().__init__(**kwargs)  # DO NOT FORGET THIS LINE!
        self.flip_axis = flip_axis

    def process_frame(self, frame: np.ndarray, **kwargs) -> np.ndarray:
        return cv2.flip(frame, self.flip_axis)

    # For efficient batch processing also implement `process_batch`, this is just an example
    def process_batch(self, batch: np.ndarray, **kwargs) -> np.ndarray:
        return np.stack([cv2.flip(frame, self.flip_axis) for frame in batch])

# Initialize and run the FrameFlipper
streamer = FrameFlipper(
    flip_axis=0,  # Flip vertically
    input="path/to/source/video.mp4",
    output="path/to/output/video.mp4",
    output_args={
        "vcodec": "libx264",
        "pix_fmt": "yuv420p",
    },
)

streamer.run(batch_size=1)  # Any batch_size > 1 calls the `process_batch` method instead.
```
As you can see, you just subclass the `FFPipe` class for your own image processor streamer and implement the `process_frame`
or `process_batch` method.

**Note**: The base `FFPipe` class takes in a couple of arguments and you should remember to override the `__init__`
method correctly as above (providing and passing the kwargs to the base constructor with `super().__init__(**kwargs)`)!

#### Using FFPipe Directly
```python
import cv2
from ffpipe import FFPipe

pipeline = FFPipe(
    input="path/to/source/video.mp4",
    output="path/to/output/video.mp4",
    output_args={
        "vcodec": "libx264",
        "pix_fmt": "yuv420p",
    },
)
pipeline.start()

while True:
    # batch_size = 1 -> np.ndarray(height, width, 3)
    # batch_size > 1 -> np.ndarray(batch_size, height, width, 3)
    frame = pipeline.read(batch_size=1)
    
    if frame is None:
        break
    
    # Do something with the frame
    processed_frame = cv2.flip(frame, 1)
    # Write the processed frame back to the pipeline
    pipeline.write(processed_frame)
    
    # End of stream check
    if pipeline.end_of_buffer:
        pipeline.write(None)
        break

# Gracefully stop the pipeline and ffmpeg processes
pipeline.stop(gracefully=True)
```
This way you might lose some of the benefits of `ffpipe` like the progress bar but you can have more control over the processing loop.

For more info, checkout the [tutorials](docs/tutorial.md).
### Customizing FFmpeg's Arguments
Under the hood, `ffpipe` adds an extra layer in your original ffmpeg pipeline and takes care of how the streams should be
piped for your Python app and back to ffmpeg. This means that you can take any existing ffmpeg command and leverage your
Python processing logic for it. So in order for `ffpipe` to work as expected, you must include all those args and filters
from your existing ffmpeg command in the `ffpipe`'s constructor.

You can customize FFPipe by passing FFmpeg-compatible arguments as dictionaries for input and output:
- `input_args`: Controls how FFmpeg reads the input (e.g., start and end timestamps, etc.).
- `output_args`: Controls how FFmpeg writes the streams to the output (e.g, output format, codec, etc.).
- Filters: Video/Audio filters are applied just before the input stream is piped for processing and can be set using below parameters.
  (so do not use `af` or `vf` in `input_args`!):
  - `video_filters`: A dict of video filters with named arguments.
  - `audio_filters`: A dict of audio filters with named arguments.
- `global_args`: A list of ffmpeg global args that are not tied to the input/output or a specific stream. e.g, ["-report"].
  Note that this is a simple list of strings as they should be passed to ffmpeg so the `-` prefix and the order are important.

```python
# Considering `CustomPipeline` subclasses `FFPipe`
pipe = CustomPipeline(
    input="input.mp4",
    output="output.mp4",
    input_args={"ss": "10"},  # Start from second 10
    output_args={"vcodec": "libx265", "crf": "28"},  # Change codec
    gloabal_args=["-report"],  # Enable ffmpeg logging to file
    video_filters={"hue": {"s": 0}},  # Convert to grayscale
    audio_filters={"bass": {"g": 10}, "treble": {"g": 5}}  # Boost sound
)
```
The above configuration corresponds to the following ffmpeg command while applying the custom processing logic defined in `CustomPipeline` in between:
```
ffmpeg -ss 10 -i input.mp4 \
       -vf "hue=s=0" \
       -af "bass=g=10,treble=g=5" \
       -vcodec libx265 -crf 28 \
       output.mp4
       -report
```

**Note**: If you want to use some crazy and complex args/filters, you must absolutely know what you're doing! Any wrong
arg or filter can mess up the whole pipeline which can be hard to debug (setting a proper `ffmpeg_log_level` is recommended for better verbosity).


## Limitations
- Since `ffpipe` decodes all frames in the pipeline, you cannot use any stream copying args for video, e.g, `-vcodec copy` (doesn't make sense anyway!).
- There is no support for Python-based processing of the audio stream in `ffpipe`; The audio is passed through as is. (Only ffmpeg args/filters can be applied to audio)
- `ffpipe` is limited to a single video stream (first video stream in the input media)!
- The pipe mechanism adds some latency that would make it unsuitable for ultra-low-latency scenarios.
- The video frame rate and the video size is determined internally and cannot be changed in the output. So do not use related args or filters for input (`-s`, `-r`).
- Slow processing logic (slower than the video FPS) causes accumulating latency or hiccups in realtime processing scenarios.
- The progress bar only counts the frames read and processed and does not verify if they're actually written to the output or not.
- The internal buffering mechanism does not have a limit by default which can cause memory issues with high resolution videos. Modify `buffer_size` if needed.
- FFmpeg's hardware acceleration probably does not work since `ffpipe` needs access to the raw frames.
- Complex filters requiring multiple inputs/outputs are not supported.
- The internal pipe commands do not accept additional args. The pipe works with `rawvideo` in `bgr24` pixel format with the native fps and video size. In certain cases the thread queue size warning might pop-up which can be set with `pipe_thread_queue_size`.