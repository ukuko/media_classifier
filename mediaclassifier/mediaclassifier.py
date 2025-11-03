"""
classifier

Usage:
    classifier.py sort-videos --directory=<directory> [--pattern=<pattern>] [--ignore-folders=<ignore_folders>]  [--recursive] [--dry-run] [--verbose]
    classifier.py (-h | --help)

Options:
    -h --help                   Show this help message and exit.
    --directory=<directory>     The directory path where renaming operations will be performed.
    --pattern=<pattern>         The pattern to search for in file names or content.
    --recursive                 Perform renaming operations recursively in nested directories
    --ignore-folders=<ignore_folders>   Comma-separated list of folder names to ignore during renaming [default: ''].
    --dry-run                   Perform a dry run without actually making changes
    --verbose                   Enable verbose mode for debugging

"""

import docopt
import os
import re
import logging

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
    
def main():
    logging.getLogger("mediaclassifier").debug("Start of method: main")
    arguments = docopt.docopt(__doc__)
    print(arguments)
    classifier = Classifier(arguments)
    if arguments['sort-videos']:
        classifier.sort_videos()

if __name__ == "__main__":
    main()