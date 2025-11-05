"""
classifier

Usage:
    classifier.py sort-videos --directory=<directory> [--pattern=<pattern>] [--ignore-folders=<ignore_folders>]  [--recursive] [--dry-run] [--verbose]
    classifier.py list-music-metadata  --directory=<directory> [--pattern=<pattern>] [--ignore-folders=<ignore_folders>]  [--recursive] [--dry-run] [--verbose]
    classifier.py (-h | --help)

Commands:
    sort-videos                 Sort video files into folders based on date pattern in file names.
    list-music-metadata         List metadata of music files in the specified directory.
    
Options:
    -h --help                   Show this help message and exit.
    --directory=<directory>     The directory path where renaming operations will be performed.
    --pattern=<pattern>         The pattern to search for in file names or content.
    --recursive                 Perform renaming operations recursively in nested directories
    --ignore-folders=<ignore_folders>   Comma-separated list of folder names to ignore during renaming [default: ''].
    --dry-run                   Perform a dry run without actually making changes
    --verbose                   Enable verbose mode for debugging

Examples:

    python mediaclassifier/mediaclassifier.py sort-videos --directory=/home/ekeko/Videos --verbose
    python mediaclassifier/mediaclassifier.py list-music-metadata --directory=/home/ekeko/workspace/music --recursive --dry-run --verbose

        
"""

import docopt
import os
import re
import logging
from mutagen import File as MutagenFile

class Classifier:
    def __init__(self, args):
        self.directory = args.get('--directory', '')
        self.pattern = args.get('--pattern', '')
        ignore_folders = args.get('--ignore-folders', '')
        self.ignore_folders = ignore_folders.split(',') if ignore_folders else []
        self.recursive = args.get('--recursive', False)
        self.dry_run = args.get('--dry-run', False)
        self.verbose = args.get('--verbose', False)

        # Logger setup
        self.logger = logging.getLogger("mediaclassifier")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

    def sort_videos(self):
        self.logger.debug("Start of method: sort_videos")
        date_pattern = re.compile(r'(\d{4})(\d{2})(\d{2})_\d{6}\.(mp4|avi|mkv|mov)$', re.IGNORECASE)
        for root, dirs, files in os.walk(self.directory):
            # Skip ignored folders
            dirs[:] = [d for d in dirs if d not in self.ignore_folders]

            for file in files:
                if file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                    if self.pattern and self.pattern not in file:
                        continue

                    match = date_pattern.match(file)
                    if match:
                        year, month, day = match.group(1), match.group(2), match.group(3)
                        new_folder = os.path.join(self.directory, year, month, day)
                        new_path = os.path.join(new_folder, file)
                    else:
                        new_folder = os.path.join(self.directory, 'SortedVideos')
                        new_path = os.path.join(new_folder, file)

                    old_path = os.path.join(root, file)

                    if not os.path.exists(new_folder):
                        if not self.dry_run:
                            os.makedirs(new_folder)
                        else:
                            self.logger.info(f"[Dry Run] Would create directory: {new_folder}")

                        self.logger.debug(f"Created directory: {new_folder}")

                    self.logger.info(f"Moving '{old_path}' to '{new_path}'")

                    if not self.dry_run:
                        os.rename(old_path, new_path)

            if not self.recursive:
                break

    def list_music_metadata(self):
        self.logger.debug("Start of method: read_music_metadata")

        for root, dirs, files in os.walk(self.directory):
            dirs[:] = [d for d in dirs if d not in self.ignore_folders]
            for file in files:
                if file.lower().endswith(('.mp3', '.flac')):
                    music_path = os.path.join(root, file)
                    self.logger.info(f"Reading metadata for: {music_path}")
                    try:
                        audio = MutagenFile(music_path, easy=True)
                        if audio is not None:
                            for key, value in audio.items():
                                self.logger.info(f"  {key}: {value}")
                        else:
                            self.logger.warning("  No metadata found or unsupported file format.")
                    except Exception as e:
                        self.logger.error(f"  Error reading metadata: {e}")
            if not self.recursive:
                break

def main():
    logging.getLogger("mediaclassifier").debug("Start of method: main")
    arguments = docopt.docopt(__doc__)
    print(arguments)
    classifier = Classifier(arguments)
    match arguments:
        case {'sort-videos': True}:
            classifier.sort_videos()
        case {'list-music-metadata': True}:
            classifier.list_music_metadata()



if __name__ == "__main__":
    main()