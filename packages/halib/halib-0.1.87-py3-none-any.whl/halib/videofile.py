from enum import Enum

import cv2
import enlighten
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from tube_dl import Youtube, Playlist

from halib.system import filesys
from halib.filetype import textfile


class VideoResolution(Enum):
    VR480p = '720x480'
    VR576p = '1280x720'
    VR720p_hd = '1280x720'
    VR1080p_full_hd = '1920x1080 '
    VR4K_uhd = '3840x2160'
    VR8K_uhd = '7680x4320'

    def __str__(self):
        return '%s' % self.value


def get_video_resolution_size(video_resolution):
    separator = 'x'
    resolution_str = str(video_resolution)
    info_arr = resolution_str.split(separator)
    width, height = int(info_arr[0]), int(info_arr[1])
    return width, height


def get_videos_by_resolution(directory, video_resolution,
                             video_ext='mp4', include_better=True):
    video_paths = filesys.filter_files_by_extension(directory, video_ext)
    filtered_video_paths = []
    for path in video_paths:
        vid = cv2.VideoCapture(path)
        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        valid = False
        video_width, video_height = get_video_resolution_size(video_resolution)
        if not include_better:
            if width == video_width and height == video_height:
                valid = True
        else:
            if width >= video_width and height >= video_height:
                valid = True

        if valid:
            filtered_video_paths.append(path)
    return filtered_video_paths


# time in seconds
def trim_video(source, destination, start_time, end_time):
    ffmpeg_extract_subclip(source, start_time, end_time, targetname=destination)


progress_bar = None


def on_progress(bytes_done, total_bytes):
    global progress_bar
    if progress_bar is None:
        progress_bar = enlighten.get_manager().counter(total=20, desc="Downloading", unit="byte", color="blue")

    progress_bar.total = total_bytes
    progress_bar.count = bytes_done
    progress_bar.update(incr=0)
    # print(bytes_done)
    if bytes_done >= total_bytes:
        progress_bar.close()
        progress_bar = None


def get_youtube_url(full_url_or_video_code):
    if 'youtube' in full_url_or_video_code:
        url = full_url_or_video_code
    else:
        url = f'https://youtube.com/watch?v={full_url_or_video_code}'
    return url


def download_yt_video(full_url_or_video_code, save_folder='./',
                      report_progress=False, video_idx='1', total_video='1'):
    url = get_youtube_url(full_url_or_video_code)
    filesys.make_dir(save_folder)
    filesys.change_current_dir(save_folder)
    try:
        yt = Youtube(url)
        title_en = yt.title.encode('ascii', 'ignore')
        file_download = yt.formats.first()
        if report_progress:
            print(f'\n[{video_idx}/{total_video}][DOWNLOAD]{title_en}')
            file_download.download(onprogress=on_progress, skip_existing=True)
    except TypeError:
        print(f'[ERROR] download {url}')


def download_playlist(playlist_url, save_folder='./',
                      report_progress=False,
                      start_pattern=None):
    print(f'[DOWNLOAD PLAYLIST] {playlist_url}')
    pl = Playlist(playlist_url).videos
    total_video = len(pl)
    should_start = False
    url = None
    count = 0
    for idx, code in enumerate(pl):
        try:
            url = f'https://youtube.com/watch?v={code}'
            yt = Youtube(url)
            count += 1
            if start_pattern is None:
                should_start = True
            elif start_pattern in yt.title:
                should_start = True
            if should_start:
                download_yt_video(url, save_folder, report_progress,
                                  video_idx=str(count),
                                  total_video=str(total_video))

        except TypeError:
            print(f'[ERROR] download {url}')
    enlighten.get_manager().stop()


# Pntt https://www.youtube.com/playlist?list=PLYaaU301HUe06Zlf3qv9q2dnVulj35gOb
# Format line: playlist_save_folder_path [SPACE] playlist_url
def download_multiple_playlist_in_files(text_file, report_progress=False):
    playlists = textfile.read_line_by_line(text_file)
    for folder_plUrl in playlists:
        folder = folder_plUrl.split()[0]
        plUrl = folder_plUrl.split()[1]
        download_playlist(plUrl, save_folder=folder, report_progress=report_progress)

# test code
# pl = 'https://youtube.com/playlist?list=PLYaaU301HUe03PabLEGbMGB8nhHgq58Zr'
# download_playlist(pl, './test', report_progress=True)
