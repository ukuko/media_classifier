"""
classifier

Usage:
    classifier.py sort-videos --directory=<directory> [--pattern=<pattern>] [--ignore-folders=<ignore_folders>]  [--recursive] [--dry-run] [--verbose]
    classifier.py list-music-metadata --directory=<directory> [--pattern=<pattern>] [--ignore-folders=<ignore_folders>]  [--recursive] [--dry-run] [--verbose]
    classifier.py export-music-metadata --directory=<directory> [--pattern=<pattern>] [--ignore-folders=<ignore_folders>] [--recursive] [--format=<format>] [--output=<output>] [--verbose]
    classifier.py (-h | --help)

Commands:
    sort-videos                 Sort video files into folders based on date pattern in file names.
    list-music-metadata         List metadata of music files in the specified directory.
    export-music-metadata       Export metadata of music files to CSV (default) or JSON.

Options:
    -h --help                   Show this help message and exit.
    --directory=<directory>     The directory path where operations will be performed.
    --pattern=<pattern>         The pattern to search for in file names or content.
    --recursive                 Perform operations recursively in nested directories
    --ignore-folders=<ignore_folders>   Comma-separated list of folder names to ignore [default: ''].
    --dry-run                   Perform a dry run without actually making changes
    --verbose                   Enable verbose mode for debugging
    --format=<format>           Export format: 'csv' or 'json' [default: 'csv']
    --output=<output>           Output file path [default: 'music_metadata.csv']

Examples:

    python mediaclassifier/mediaclassifier.py sort-videos --directory=/home/ekeko/Videos --verbose
    python mediaclassifier/mediaclassifier.py list-music-metadata --directory=/home/ekeko/workspace/music --recursive --dry-run --verbose
    python mediaclassifier/mediaclassifier.py export-music-metadata --directory=/home/ekeko/workspace/music --recursive --format=csv --output=metadata.csv --verbose

"""

import docopt
import os
import re
import logging
from mutagen import File as MutagenFile
import json
import csv

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

    def export_music_metadata(self, export_format='csv', output_path=None):
        self.logger.debug("Start of method: export_music_metadata")
        metadata_list = []

        for root, dirs, files in os.walk(self.directory):
            dirs[:] = [d for d in dirs if d not in self.ignore_folders]
            for file in files:
                if file.lower().endswith(('.mp3', '.flac')):
                    music_path = os.path.join(root, file)
                    try:
                        audio = MutagenFile(music_path, easy=True)
                        if audio is not None:
                            entry = {'file': music_path}
                            for key, value in audio.items():
                                entry[key] = value
                            metadata_list.append(entry)
                        else:
                            self.logger.warning(f"No metadata found for: {music_path}")
                    except Exception as e:
                        self.logger.error(f"Error reading metadata for {music_path}: {e}")
            if not self.recursive:
                break

        if not output_path:
            output_path = f"music_metadata.{export_format}"

        if export_format == 'json':
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata_list, f, ensure_ascii=False, indent=2)
                self.logger.info(f"Exported metadata to JSON: {output_path}")
            except Exception as e:
                self.logger.error(f"Error writing JSON: {e}")
        else:  # default to CSV
            try:
                # Collect all possible keys for CSV header
                all_keys = set()
                for entry in metadata_list:
                    all_keys.update(entry.keys())
                all_keys = sorted(all_keys)
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=all_keys)
                    writer.writeheader()
                    for entry in metadata_list:
                        writer.writerow(entry)
                self.logger.info(f"Exported metadata to CSV: {output_path}")
            except Exception as e:
                self.logger.error(f"Error writing CSV: {e}")

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
        case {'export-music-metadata': True}:
            export_format = arguments.get('--format') or 'csv'
            output_path = arguments.get('--output')
            classifier.export_music_metadata(export_format=export_format, output_path=output_path)



if __name__ == "__main__":
    main()