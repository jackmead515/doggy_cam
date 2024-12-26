import subprocess
import json
import os


def ffprobe_frame_times(video_file):
    """
    Fetches the timestamps (offset from the start of the video) of each frame in the video
    """
    cmd = f'/usr/bin/ffprobe -select_streams 0 -show_entries packet=pts_time:stream=codec_type "{video_file}" -print_format json'
    output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = json.loads(output.stdout)
    output = [float(p['pts_time']) for p in output['packets']]
    return output


def fetch_timestamps(video_files):
    """
    Fetches the timestamps of each frame for each video file.
    """
    frame_times = {}

    for video_file in video_files:
        timestamps = ffprobe_frame_times(video_file)
        video_start_time = float(os.path.basename(video_file).split('_')[1].split('.')[0])
        times = []

        for timestamp in timestamps:
            times.append(video_start_time + timestamp)

        frame_times[video_file] = sorted(times)
    
    return frame_times