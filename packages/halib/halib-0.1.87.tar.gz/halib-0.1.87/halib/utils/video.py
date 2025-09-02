import os
import cv2
from ..filetype import csvfile
from ..system import filesys as fs


class VideoUtils:

    @staticmethod
    def _default_meta_extractor(video_path):
        """Default video metadata extractor function."""
        # Open the video file
        cap = cv2.VideoCapture(video_path)

        # Check if the video was opened successfully
        if not cap.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return None

        # Get the frame count
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Get the FPS
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Release the video capture object
        cap.release()

        meta_dict = {
            "video_path": video_path,
            "frame_count": frame_count,
            "fps": fps
        }
        return meta_dict

    @staticmethod
    def get_video_meta_dict(video_path, meta_dict_extractor_func=None):
        assert os.path.exists(video_path), f"Video file {video_path} does not exist"
        if meta_dict_extractor_func and callable(meta_dict_extractor_func):
            assert meta_dict_extractor_func.__code__.co_argcount == 1, "meta_dict_extractor_func must take exactly one argument (video_path)"
            meta_dict = meta_dict_extractor_func(video_path)
            assert isinstance(meta_dict, dict), "meta_dict_extractor_func must return a dictionary"
            assert 'video_path' in meta_dict, "meta_dict must contain 'video_path'"
        else:
            meta_dict = VideoUtils._default_meta_extractor(video_path=video_path)
        return  meta_dict
    @staticmethod
    def get_video_dir_meta_df(video_dir, video_exts=['.mp4', '.avi', '.mov', '.mkv'], search_recursive=False, csv_outfile=None):
        assert os.path.exists(video_dir), f"Video directory {video_dir} does not exist"
        video_files = fs.filter_files_by_extension(video_dir, video_exts, recursive=search_recursive)
        assert len(video_files) > 0, f"No video files found in {video_dir} with extensions {video_exts}"
        video_meta_list = []
        for vfile in video_files:
            meta_dict = VideoUtils.get_video_meta_dict(vfile)
            if meta_dict:
                video_meta_list.append(meta_dict)
        dfmk = csvfile.DFCreator()
        columns = list(video_meta_list[0].keys())
        assert len(columns) > 0, "No video metadata found"
        assert 'video_path' in columns, "video_path column not found in video metadata"
        # move video_path to the first column
        columns.remove('video_path')
        columns.insert(0, 'video_path')
        dfmk.create_table("video_meta", columns)
        rows = [[meta[col] for col in columns] for meta in video_meta_list]
        dfmk.insert_rows("video_meta", rows)
        dfmk.fill_table_from_row_pool("video_meta")

        if csv_outfile:
            dfmk["video_meta"].to_csv(csv_outfile, index=False, sep=";")
        return dfmk["video_meta"].copy()





