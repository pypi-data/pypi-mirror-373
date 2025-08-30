import logging
import threading
import time
from collections.abc import Iterable
from queue import Queue

import ffmpeg
import numpy as np
from tqdm import tqdm

# Configure the logger to output to the console
_logger = logging.getLogger(__name__)
_logger.propagate = False
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("FFPipe (%(levelname)s): %(message)s"))
_logger.addHandler(handler)


class FFPipe:
    """
    A wrapper for FFmpeg that enables real-time video frame processing using piping.

    FFPipe writes the input streams to a pipe and buffers them in a queue. The frames are then read and processed and
    the result frames are pushed to the pipe and written to the output stream (audio is written to the output as is):

    input -> ffmpeg pipe (stdout) -> input buffer -> read and process -> output buffer -> ffmpeg pipe (stdin) -> output

    In order to define your own pipeline, you need to subclass FFPipe and implement the `process_frame()`/`process_batch()` method.

    You can also use FFPipe directly as the pipeline and instead of implementing the `process_frame()`/`process_batch()`
    methods, initialize a FFPipe instance and call the `start()` method and read frames in a while loop. Refer to the
    docs for more info.

    Args:
        input (str):
            Path to the source video. Anything compatible with FFmpeg can be used as input.
        output (str):
            Path to the output video. Anything compatible with FFmpeg can be used as output. Note that if the output
            needs a format to be set (just like in a typical ffmpeg command) it should be set in the
            `output_args` too. This means that the control over the output format and all other required args
            is in the hands of the user.
        input_args (dict):
            FFmpeg options for the input in the form of a dictionary. e.g, {"ss": 10} to start from the 10th second.
        output_args (dict):
            FFmpeg options for the output in the form of a dictionary. e.g, `{"vcodec": "libx264"}` to set the video codec.
        global_args (list):
            FFmpeg global options in the form of list. e.g, `["-report"]`.
        video_filters (dict):
            FFmpeg filters to apply to the input video stream. The filters are applied in the order they are given.
            Pass a dict of dicts like e.g, `{"scale": {"width": 1280, "height": 720}}`.
        audio_filters (dict):
            FFmpeg filters to apply to the input audio stream. The filters are applied in the order they are given.
            Pass a dict of dicts like e.g, `{"equalizer": {"f": 1000, "width_type": "q", "width": 100}}`.
        buffer_size (int):
            Size of the internal frame buffer queue. Set to -1 for an unbounded buffer.
        buffers_timeout (int):
            Timeout for reading frames from the input/output buffers.
        pipe_thread_queue_size (int):
            Value of `thread_queue_size` for the pipe input. The default value is 1024 as opposed to the default 8 in
            ffmpeg to avoid warning from ffmpeg.
        log_level (str):
            Logging level for the FFPipe operations. For ffmpeg's log level, use `ffmpeg_log_level`.
        ffmpeg_log_level (str):
            FFmpeg logging level. All values supported by FFmpeg are accepted. The default is `warning`.
        on_write_error (str):
            Action to take when an error occurs while writing to the output stream. Options are "ignore", "raise".
        progress_bar (bool):
            Whether to show a progress bar during processing. Set to False to disable the progress bar.
        **kwargs:
            Additional keyword arguments. Solely for future compatibility.
    """

    logger = _logger

    def __init__(
        self,
        input: str,
        output: str,
        input_args: dict = None,
        output_args: dict = None,
        global_args: list = None,
        video_filters: dict = None,
        audio_filters: dict = None,
        buffer_size: int = -1,
        buffers_timeout: int = 30,
        pipe_thread_queue_size: int = 1024,
        log_level: str = "warning",
        ffmpeg_log_level: str = "warning",
        on_write_error: str = "ignore",
        ffmpeg_error_tail_size: int = 10,
        progress_bar: bool = True,
        print_media_info: bool = True,
        **kwargs,
    ):
        self.input = input
        self.output = output
        self.input_args = input_args or {}
        self.output_args = output_args or {}
        self.global_args = ["-hide_banner", "-loglevel", ffmpeg_log_level] + (global_args or [])
        self.video_filters = video_filters
        self.audio_filters = audio_filters
        self.buffer_size = buffer_size
        self.buffers_timeout = buffers_timeout
        self.pipe_thread_queue_size = pipe_thread_queue_size
        self.log_level = log_level.upper()
        self.on_write_error = on_write_error.lower()
        self.ffmpeg_error_tail_size = ffmpeg_error_tail_size
        self.tqdm_disable = not progress_bar
        self.processing_running = True
        self.reader_running = True
        self.writer_running = True
        self.end_of_buffer = False

        # Handle unrecognized keyword arguments
        if kwargs:
            self.logger.warning(f"Unrecognized keyword arguments: {kwargs}")

        # State dictionary for storing the state of the pipeline. This helps to do conditional processing.
        self.state = {}

        # Set the logging level of the FFPipe's logger. (ffmpeg's log level is set as `ffmpeg_loglevel`)
        self.logger.setLevel(self.log_level)

        # Queues for input/output frames buffering
        self.input_buffer = Queue(maxsize=self.buffer_size)
        self.output_buffer = Queue()

        # Extract video properties
        self._extract_streams_info()

        # Print the media information
        if print_media_info:
            self.print_media_info()

        # Initialize FFmpeg processes
        self._initialize_ffmpeg_processes()

    def _extract_streams_info(self):
        """
        Extract audio and video properties using ffprobe. Video stream is required, audio stream is optional.
        """
        self.logger.info("Extracting source info...")
        try:
            probe = ffmpeg.probe(self.input, hide_banner=None)

            # Find video stream - required
            video_streams = [s for s in probe["streams"] if s["codec_type"] == "video"]
            if not video_streams:
                raise ValueError("No video stream found in the input. FFPipe requires a video stream.")
            self.video_info = video_streams[0]

            # Find audio stream - optional
            audio_streams = [s for s in probe["streams"] if s["codec_type"] == "audio"]
            self.has_audio = len(audio_streams) > 0
            self.audio_info = audio_streams[0] if self.has_audio else None

        except ffmpeg.Error as e:
            raise RuntimeError(f"Error extracting video properties: {e.stderr}") from None

    def print_media_info(self):
        """
        Print details of the video and audio streams in a formatted way.
        """
        # Create a separator line for visual clarity
        separator = "─" * 60

        # Print video information with improved formatting
        print(f"\n{separator}")
        print("📹 Video Info:")
        print(f"{separator}")
        print(f"  • Resolution:   {self.video_info.get('width', 'N/A')}×{self.video_info.get('height', 'N/A')}")
        print(f"  • Frame rate:   {self.video_info.get('r_frame_rate', 'N/A')}")
        print(f"  • Codec:        {self.video_info.get('codec_name', 'N/A')}")
        print(f"  • Duration:     {self.video_info.get('duration', 'N/A')} seconds")
        print(f"  • Total frames: {self.video_info.get('nb_frames', 'N/A')}")
        print(f"  • Bitrate:      {self.video_info.get('bit_rate', 'N/A')} bps")

        # Print audio information with improved formatting
        print(f"\n{separator}")
        print("🔊 Audio Info:")
        print(f"{separator}")
        print(f"  • Codec:        {self.audio_info.get('codec_name', 'N/A') if self.audio_info else 'N/A'}")
        print(f"  • Channels:     {self.audio_info.get('channels', 'N/A') if self.audio_info else 'N/A'}")
        print(f"  • Sample rate:  {self.audio_info.get('sample_rate', 'N/A') if self.audio_info else 'N/A'} Hz")
        print(f"  • Bitrate:      {self.audio_info.get('bit_rate', 'N/A') if self.audio_info else 'N/A'} bps")
        print(f"{separator}\n")

    def validate_args(self):
        """
        Validate the input/output/filter/global args. Subclasses can override this method to add custom validation logic.
        """
        if "vf" in self.input_args or "af" in self.input_args:
            raise ValueError("Filters 'vf' or 'af' must be passed as `video_filters` or `audio_filters`!")
        if "r" in self.input_args:
            raise ValueError("Frame rate 'r' must not be passed with the input args!")
        if "s" in self.input_args:
            raise ValueError("Frame size 's' must not be passed with the input args!")

    @staticmethod
    def _determine_batch_size(batch_size: int = None):
        if batch_size is not None and (not isinstance(batch_size, int) or batch_size < 0):
            raise ValueError(f"The `batch_size` must be a valid integer, got {batch_size}!")
        return 1 if batch_size in (0, 1, None) else batch_size

    def _initialize_ffmpeg_processes(self):
        """
        Create FFmpeg processes for streaming, processing, and output.
        """
        # Validate the args
        self.validate_args()

        video = ffmpeg.input(self.input, **self.input_args).video
        # Add filters if given
        if self.video_filters:
            for filter_name, filter_parameters in self.video_filters.items():
                video = video.filter(filter_name, **filter_parameters)

        # Input process that streams from input -> pipe
        self.input2pipe = video.output(
            "pipe:v",
            format="rawvideo",
            pix_fmt="bgr24",
        ).global_args(*self.global_args)

        # Get audio and apply filters if given
        audio = ffmpeg.input(self.input, **self.input_args).audio if self.has_audio else None
        if self.has_audio and self.audio_filters:
            for filter_name, filter_parameters in self.audio_filters.items():
                audio = audio.filter(filter_name, **filter_parameters)

        # Input process that reads the processed frames from the pipe
        processed_video = ffmpeg.input(
            "pipe:v",
            format="rawvideo",
            pix_fmt="bgr24",
            s=f"{self.video_info['width']}x{self.video_info['height']}",
            r=self.video_info["r_frame_rate"],
            thread_queue_size=self.pipe_thread_queue_size,
        )

        # Output process that streams from pipe -> output
        if self.has_audio:
            # Output process with both video and audio
            self.pipe2output = (
                ffmpeg.output(audio, processed_video, self.output, **self.output_args)
                .global_args(*self.global_args)
                .overwrite_output()
            )
        else:
            # Output process with only video
            self.pipe2output = (
                ffmpeg.output(processed_video, self.output, **self.output_args)
                .global_args(*self.global_args)
                .overwrite_output()
            )

    def _input_reader(self):
        """
        A background process to continuously read frames from the FFmpeg input process (FFmpeg's stdout) and buffer them.
        Detects the end of the stream and signals the processing loop to stop. This function is triggered in a separate
        thread in the `start()` method.
        """
        try:
            while self.reader_running:
                frame_bytes = self.input2pipe.stdout.read(self.video_info["width"] * self.video_info["height"] * 3)

                if not frame_bytes:  # End of stream
                    self.logger.info("End of stream; No more frames to push to the buffer...")
                    self.input_buffer.put(None)
                    break

                frame = np.frombuffer(frame_bytes, np.uint8).reshape((
                    self.video_info["height"],
                    self.video_info["width"],
                    3,
                ))
                self.input_buffer.put(frame, block=True)

        except Exception as e:
            self.logger.error(f"Error reading frames or the stream ended: {e}")
            self.input_buffer.put(None)  # Signal the processing loop that the stream ended

    def _output_writer(self):
        """
        A background process to continuously read from the output buffer and write them to the FFmpeg's output process
        (FFmpeg's stdin). This method is triggered in a separate thread in the `start()` method.
        """
        while self.writer_running:
            frame = self.output_buffer.get()
            if frame is None:
                self.logger.info("Finished writing all the processed frames to the output...")
                self.writer_running = False
                break
            try:
                self.pipe2output.stdin.write(frame.astype(np.uint8).tobytes())
            except Exception as e:
                if hasattr(self.pipe2output, "stderr") and self.pipe2output.stderr:
                    ffmpeg_err = self.pipe2output.stderr.read().decode(errors="ignore")
                    err_message = " ".join(ffmpeg_err.split("\n")[-self.ffmpeg_error_tail_size:])
                    self.logger.error(
                        f"Error writing the frame to the output stream! Cause: {e}.\n"
                        f"FFmpeg error output:\n{err_message}\n"
                        "If you're seeing this error continuously, something's seriously wrong!\n"
                    )
                    if self.on_write_error == "raise":
                        self.processing_running = False
                        self.reader_running = False
                        self.writer_running = False
                        raise RuntimeError(f"Error writing to output stream: {err_message}")

    def start(self):
        """
        Start the FFmpeg processes and begin streaming.
        """
        self.logger.info("Starting the input stream (input -> pipe) thread...")
        self.input2pipe = self.input2pipe.run_async(pipe_stdout=True)
        self.logger.info("Starting the output stream (pipe -> output) thread...")
        self.pipe2output = self.pipe2output.run_async(pipe_stdin=True, pipe_stderr=True)

        # Start the thread responsible for reading and writing the frames
        threading.Thread(target=self._input_reader, daemon=True).start()
        threading.Thread(target=self._output_writer, daemon=True).start()

    def _next_frame(self) -> np.ndarray:
        """
        Retrieve the next frame from the input buffer. The output frame is a np.ndarray with shape (height, width, 3).
        """
        frame = self.input_buffer.get(timeout=self.buffers_timeout)
        if frame is None:
            self.logger.info("No more frames to read from the buffer...")
        return frame

    def read(self, batch_size: int = None) -> np.ndarray:
        """
        Retrieve the next frame/batch from the buffer.

        Args:
            batch_size (int): Number of frames to retrieve from the buffer. If None, it retrieves a single frame without
            the batch dimension (a single frame array).

        Returns:
            np.ndarray: A single frame (h, w, 3) or an array of frames (N, h, w, c) depending on the batch size.
        """
        batch_size = self._determine_batch_size(batch_size)

        if batch_size == 1:
            return self._next_frame()
        else:
            batch = []
            for _ in range(batch_size):
                frame = self._next_frame()
                if frame is None:
                    self.end_of_buffer = True
                    break
                batch.append(frame)

            return np.stack(batch)

    def write(self, data: np.ndarray):
        """
        Write a single frame or a batch of frames to the output buffer. The buffer is then read by the output writer.
        """
        # Batch mode
        if isinstance(data, np.ndarray) and len(data.shape) == 4:
            for frame in data:
                self.output_buffer.put(frame)
        # Single frame mode
        else:
            self.output_buffer.put(data)

    def process_frame(self, frame: np.ndarray, **kwargs) -> np.ndarray:
        """
        Process a single frame using the user-defined processing function. Subclasses must override this method.

        Args:
            frame (np.ndarray): A single video frame as a numpy array with shape (height, width, 3).
            **kwargs: Optional keyword arguments so that subclasses can override this method flixibly.

        Returns:
            np.ndarray: The processed frame.
        """
        raise NotImplementedError("The `process_frame` method must be implemented!")

    def process_batch(self, batch: np.ndarray, **kwargs) -> np.ndarray | Iterable[np.ndarray]:
        """
        Process a batch of frames using the user-defined processing function. Subclasses can override this method.

        Args:
            batch (np.ndarray): A batch of video frames as a numpy array with shape (batch_size, height, width, 3).
            **kwargs: Optional keyword arguments so that subclasses can override this method flixibly.

        Returns:
            np.ndarray | Iterable[np.ndarray]: The processed batch of frames.
        """
        raise NotImplementedError("The `process_batch` method must be implemented when `batch_size > 1`!")

    def run(self, batch_size: int = None, **process_kwargs):
        """
        Start the processing and streaming loop. This method reads frames from the buffer, processes them, and pushes
        the processed frames to the output stream.

        Args:
            batch_size (int): Number of frames to process in a batch. If None, it processes a single frame at a time.
            **process_kwargs: Optional keyword arguments to pass to the `process_frame`/`process_batch` method.
        """
        batch_size = self._determine_batch_size(batch_size)
        # Determine the processing function based on the batch size
        process_fn = self.process_batch if batch_size > 1 else self.process_frame

        # Start the FFmpeg processes and buffer handler threads
        self.start()

        progress_bar = tqdm(
            total=int(self.video_info.get("nb_frames", 0)),
            desc="Processing frames: ",
            unit=" frames",
            ascii=" #",
            ncols=120,
            disable=self.tqdm_disable,
        )

        self.logger.info("Starting the processing loop...")
        while self.processing_running:
            # Get the next frame/batch from the queue
            data = self.read(batch_size=batch_size)

            if data is None:
                break

            # Process the frame/batch
            processed_data = process_fn(data, **process_kwargs)

            # Update progress bar
            progress_bar.update(data.shape[0] if len(data.shape) == 4 else 1)

            # Push the processed frame/batch to the output stream
            self.write(processed_data)

            # Stop the loop if the end of the buffer is reached
            if self.end_of_buffer:
                # Signal the output writer to stop
                self.write(None)
                break

        # Close the progress bar
        progress_bar.close()
        # Stop gracefully
        self.stop(gracefully=True)

    def stop(self, gracefully: bool = False):
        """
        Stop all FFmpeg processes.

        Args:
            gracefully (bool): If True, wait for the writer thread to finish writing all the frames before stopping.
        """
        self.logger.info("Stopping processes...")

        self.reader_running = False
        self.processing_running = False

        if gracefully:
            self.logger.info("Waiting for the writer to finish writing all the frames...")
            while self.writer_running and not self.output_buffer.empty():
                time.sleep(0.1)
        else:
            self.writer_running = False

        try:
            self.pipe2output.stdin.close()
            # Wait for input and output processes to finish
            self.input2pipe.wait()
            self.pipe2output.wait()
            self.logger.info("Done!")
        except Exception as e:
            self.logger.error(f"Error stopping FFmpeg processes: {e}")
