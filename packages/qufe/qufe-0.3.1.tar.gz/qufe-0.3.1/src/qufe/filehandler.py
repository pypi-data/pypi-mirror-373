import os
import re
from datetime import datetime
import pickle
from pathlib import Path
from typing import Iterable, Callable
import unicodedata

from . import base as qb
from . import texthandler as qth

qb_ts = qb.TS()


class FileHandler:
    """
    A comprehensive file handling utility class providing various file operations,
    directory management, and data persistence functionality.
    """
    
    def __init__(self):
        self.path_temp_data = './temp/data'

    @staticmethod
    def get_file_name(folder_path):
        """
        Get all file names from a directory recursively.
        
        Args:
            folder_path (str): Path to the directory to search
            
        Returns:
            list: List of file names found in the directory
        """

        # f_list = list()
        # for r_, d_, f_ in os.walk(folder_path):
        #     if len(f_):
        #         for n_ in f_:
        #             f_list += [n_]
        # return f_list

        return [n_ for r_, d_, f_ in os.walk(folder_path) for n_ in f_ if len(f_)]

    @staticmethod
    def get_tree(folder_path: str, normalize: bool = False):
        """
        Get all file paths from a directory recursively.
        
        Args:
            folder_path (str): Path to the directory to search
            normalize (bool): Whether to apply Unicode normalization
            
        Returns:
            list: List of full file paths found in the directory
        """

        # if not folder_path.endswith('/'):
        #     folder_path += '/'

        # f_tree = tuple()
        # for r_, d_, f_ in os.walk(folder_path):
        #     if len(f_):
        #         for n_ in f_:
        #             f_path = os.path.join(r_, n_)
        #             f_path = f_path.replace('\\', '/')
        #             f_tree += (f_path,)
        # return f_tree

        r = [os.path.join(r_, n_).replace('\\', '/') for r_, d_, f_ in os.walk(folder_path) for n_ in f_ if len(f_)]
        if normalize:
            return [unicodedata.normalize('NFC', foo) for foo in r]
        else:
            return r

    @staticmethod
    def get_latest_by_pattern(directory, pattern):
        """Deprecated method. Use get_latest_file instead."""
        print('Method name changed to get_latest_file. (Parameter changed too.)')
        raise NotImplementedError

    @staticmethod
    def get_datetime_from_date_pattern(pattern: str, filename: str) -> datetime:
        """
        Extract datetime from filename using a regex pattern.
        
        Args:
            pattern (str): Regex pattern to match datetime parts
            filename (str): Filename to extract datetime from
            
        Returns:
            datetime: Extracted datetime object or None if no match
        """
        match = re.match(pattern, filename)
        result = None
        if match:
            parts = list(map(int, match.groups()))
            if len(parts) == 3:
                year, month, day = parts
                result = datetime(year, month, day)
            elif len(parts) == 5:
                year, month, day, hour, minute = parts
                result = datetime(year, month, day, hour, minute)
            elif len(parts) == 6:
                year, month, day, hour, minute, second = parts
                result = datetime(year, month, day, hour, minute, second)
            else:
                raise ValueError(f"Unsupported number of datetime parts: {len(parts)}")
        return result
    
    @staticmethod
    def get_int_from_timestamp_pattern(pattern: str, filename: str) -> int:
        """
        Extract integer timestamp from filename using a regex pattern.
        
        Args:
            pattern (str): Regex pattern to match timestamp
            filename (str): Filename to extract timestamp from
            
        Returns:
            int: Extracted timestamp or None if no match
        """
        match = re.match(pattern, filename)
        result = None
        if match:
            result = int(match.group(1))
        return result
    
    @staticmethod
    def get_latest_file(directory, extract_fn, pattern, analysis: bool = False):
        """
        Find the latest file in a directory based on a datetime/timestamp pattern.
        
        Args:
            directory (str): Directory path to search
            extract_fn (Callable): Function to extract datetime/timestamp from filename
            pattern (str): Regex pattern for filename matching
            analysis (bool): Whether to print analysis information
            
        Returns:
            tuple: (latest_file_path, timestamp_latest, files)
            
        Example 1.:
            from qufe import filehandler as qfh
            
            f_path = './temp/data/'
            pattern = r'page_data_(\d{10}).pickle'
            extract_fn = qfh.FileHandler.get_int_from_timestamp_pattern
            
            (latest_file, timestamp_latest, files) = qfh.FileHandler.get_latest_file(
                f_path, extract_fn, pattern)
            print(latest_file)

        Example 2.:
            if,
                pattern = r"Receipt_(\d{4})_(\d{2})_(\d{2})\.pickle"
            then,
                Receipt_2024_10_15.pickle
                Receipt_2025_01_20.pickle
                Receipt_2025_03_25.pickle
            2025_03_25 is the latest.
        """
        latest_file = None
        timestamp_latest = None
        prev_ts = None
        ts_diff = ''
        files = list()
        
        # Check files in directory
        for filename in sorted(os.listdir(directory)):
            timestamp = extract_fn(pattern, filename)
            if timestamp is not None:
                timestamp = qb_ts.timestamp_to_datetime(timestamp)
                
                # Analysis output
                if analysis:
                    if prev_ts is not None:
                        ts_diff = timestamp - prev_ts
                    prev_ts = timestamp
                    print(f'{filename} - {qb_ts.get_ts_formatted(timestamp)} (Diff.: {ts_diff})')
                    files.append(filename)
                
                # Check if this is the latest
                if (timestamp_latest is None) or (timestamp > timestamp_latest):
                    timestamp_latest = timestamp
                    latest_file = filename
        
        if not latest_file:
            raise FileNotFoundError('No matching files found.')
        
        # Return path + filename
        latest_file_path = os.path.join(directory, latest_file)
        print(f'Latest File Name: {latest_file}')
        return (latest_file_path, timestamp_latest, files)

    @staticmethod
    def load_pickle(pkl, rb: bool = True):
        """
        Load data from a pickle file.
        
        Args:
            pkl (str): Path to pickle file
            rb (bool): Whether to open in binary mode
            
        Returns:
            object: Loaded data from pickle file
        """
        mode = 'rb' if rb else 'r'
        with open(pkl, mode) as f_:
            pkl = pickle.load(f_)
        return pkl

    @staticmethod
    def pickle_to_txt(input_pickle_name: str, output_txt_name: str):
        """Deprecated method. Use iterable_to_txt_file instead."""
        print('Method name changed to "iterable_to_txt_file()"')
        raise NotImplementedError

    def extract_iterable(self, itrb: Iterable, depth=0) -> list:
        """
        Flatten nested dictionaries or iterables with proper indentation.
        
        Args:
            itrb (Iterable): The iterable to flatten
            depth (int): Current indentation depth
            
        Returns:
            list: Flattened representation with indentation
        """
        extracted = list()
        
        # Handle dictionaries
        if isinstance(itrb, dict):
            for (k, v) in itrb.items():
                extracted.append(f'{"    " * depth}{k}')
                extracted.extend(self.extract_iterable(v, depth + 1))
        
        # Handle lists/tuples/sets
        elif isinstance(itrb, (list, tuple, set)):
            for v in itrb:
                extracted.extend(self.extract_iterable(v, depth + 1))
                if depth < 1:
                    extracted.append('\n')
        
        # Handle scalar values
        else:
            extracted.append(f'{"    " * depth}{itrb}')
        
        return extracted

    @staticmethod
    def list_to_txt_file(lines: list, file_name: str) -> None:
        """Deprecated method. Use iterable_to_txt_file instead."""
        print('Method name changed to "iterable_to_txt_file()"')
        raise NotImplementedError

    def make_path(self, path: str) -> str:
        """
        Create directory if it doesn't exist.
        
        Args:
            path (str): Path to create
            
        Returns:
            str: Created path
        """
        if (not path) or (not isinstance(path, str)):
            path = self.path_temp_data
        os.makedirs(path, exist_ok=True)
        return path

    def make_file_path(self, path: str, file_name: str) -> str:
        """
        Create full file path by joining directory and filename.
        
        Args:
            path (str): Directory path
            file_name (str): File name
            
        Returns:
            str: Full file path
        """
        path_made = self.make_path(path)
        return os.path.join(path_made, file_name)

    def _save_file(self, path: str, file_name: str, save_func: Callable[[str], None]) -> None:
        """
        Helper function to save files with error handling.
        
        Args:
            path (str): Directory path
            file_name (str): File name
            save_func (Callable): Function to perform the actual save operation
        """
        try:
            file_path = self.make_file_path(path, file_name)
            save_func(file_path)
            print('Save to: ', file_path)
        except Exception as e:
            print(f'Error occurred while creating file: {e}')        

    def iterable_to_txt_file(self, itrb: Iterable, file_name: str, path: str = '') -> None:
        """
        Save iterable data to a text file.
        
        Args:
            itrb (Iterable): Data to save
            file_name (str): Output file name
            path (str): Output directory path
        """
        def save_func(file_path: str) -> None:
            with open(file_path, 'w', encoding='utf-8') as f_:
                for itr in itrb:
                    f_.write(f'{itr}\n')
        
        self._save_file(path, file_name, save_func)

    def pickle_temp_data(self, data, file_name: str, path: str = '') -> None:
        """
        Save data to a pickle file.
        
        Args:
            data: Data to save
            file_name (str): Output file name
            path (str): Output directory path
        """
        def save_func(file_path: str) -> None:            
            with open(file_path, 'wb') as f_:
                pickle.dump(data, f_)
        
        self._save_file(path, file_name, save_func)

    def build_tree(self, path):
        """
        Build a nested dictionary representation of directory structure.
        
        Args:
            path (str): Directory path to build tree from
            
        Returns:
            list: Nested structure representation
        """
        items = []
    
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            if os.path.isdir(full_path):
                items.append({name: self.build_tree(full_path)})
            else:
                items.append(name)
    
        # Sort files and folders by name
        def sort_key(item):
            if isinstance(item, str):
                return item.lower()
            elif isinstance(item, dict):
                return list(item.keys())[0].lower()
            return ''
    
        return sorted(items, key=sort_key)

    def tree_to_dict(self, start_path):
        """
        Convert directory tree to dictionary format.
        
        Args:
            start_path (str): Starting directory path
            
        Returns:
            dict: Dictionary representation of directory tree
        """
        return {os.path.basename(os.path.normpath(start_path)): self.build_tree(start_path)}
    
    def get_contents(self, base_path: str, print_tree: bool = False) -> dict:
        """
        Extract text file contents from directory structure.
        
        Args:
            base_path (str): Base directory path
            print_tree (bool): Whether to print the directory tree
            
        Returns:
            dict: Dictionary containing file contents
        """
        # Generate tree structure using full path
        ttd = self.tree_to_dict(base_path)
        if print_tree:
            qth.print_dict(ttd)

        # Create path for _get_contents (remove last folder component)
        if base_path.endswith('/'):
            base_path = base_path.rstrip('/')
        base_path = f'{"/".join(base_path.split("/")[:-1])}'

        return self._get_contents(ttd, base_path)
    
    def _get_contents(self, d_: dict, path_: str) -> dict:
        """
        Recursively extract text file contents from dictionary structure.
        
        Args:
            d_ (dict): Directory structure dictionary
            path_ (str): Current path
            
        Returns:
            dict: Dictionary containing file contents
        """
        if isinstance(d_, dict):
            txt_container = dict()
            for (k0, v0) in d_.items():
                if k0 not in txt_container.keys():
                    txt_container[k0] = dict()
                if isinstance(v0, list):
                    for v1 in v0:
                        if isinstance(v1, str):
                            if v1.endswith('.txt'):
                                with open(f'{path_}/{k0}/{v1}', 'r') as f:
                                    txt_container[k0].update({
                                        v1: [line.rstrip().replace('\t', '    ') for line in f if len(line)]
                                    })
                        elif isinstance(v1, dict):
                            txt_container[k0].update(self._get_contents(v1, f'{path_}/{k0}'))
                elif isinstance(v0, dict):
                    txt_container[k0].update(self._get_contents(v0, f'{path_}/{k0}'))
                else:
                    raise NotImplementedError("Unsupported file type")
            return txt_container
        else:
            raise NotImplementedError("Input must be a dictionary")

    @staticmethod
    def sanitize_filename(name: str, replacement: str = "_") -> str:
        """
        Sanitize filename by removing invalid characters.
        
        Args:
            name (str): Original filename
            replacement (str): Character to replace invalid characters with
            
        Returns:
            str: Sanitized filename
        """
        # Remove characters not supported by Windows file system
        invalid_chars = r'[\\/*?:"<>|]'
        sanitized = re.sub(invalid_chars, replacement, name).strip()
        return sanitized if sanitized else "untitled"

    @staticmethod
    def get_unique_filename(base_dir: Path, base_name: str, extension: str = ".csv") -> Path:
        """
        Generate unique filename in given directory to avoid conflicts.
        
        Args:
            base_dir (Path): Base directory path
            base_name (str): Base filename without extension
            extension (str): File extension
            
        Returns:
            Path: Unique file path
            
        Example:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            for (key, df) in container.items():
                base_name = FileHandler.sanitize_filename(key)
                file_path = FileHandler.get_unique_filename(output_dir, base_name)
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
        """
        counter = 0
        candidate = base_dir / f"{base_name}{extension}"
        while candidate.exists():
            counter += 1
            candidate = base_dir / f"{base_name}_{counter}{extension}"
        return candidate

    @staticmethod
    def copy_files_by_extension(
            source_dir: str,
            dest_dir: str,
            extension: str,
            flatten: bool = True,
            preserve_structure: bool = False,
            verbose: bool = True) -> tuple:
        """
        Copy all files with specific extension from source directory to destination.

        Args:
            source_dir (str): Source directory path to search files
            dest_dir (str): Destination directory path to copy files
            extension (str): File extension to search (e.g., '.db', 'db', '*.db')
            flatten (bool): If True, copy all files to dest_dir root without subdirectories
            preserve_structure (bool): If True, preserve source directory structure in destination
            verbose (bool): If True, print copy progress

        Returns:
            tuple: (copied_count, failed_files, copied_files)
                - copied_count (int): Number of successfully copied files
                - failed_files (list): List of tuples (source_path, error_message) for failed copies
                - copied_files (list): List of tuples (source_path, dest_path) for successful copies

        Example:
            from qufe import filehandler as qfh

            fh = qfh.FileHandler()

            # Copy all files with the specified extension from the source folder to the destination folder
            source = '/source_folder'
            dest = '/dest_folder/data'

            copied, failed, files = fh.copy_files_by_extension(
                source_dir=source,
                dest_dir=dest,
                extension='.db',
                flatten=True
            )

            print(f"Successfully copied: {copied} files")
            if failed:
                print(f"Failed to copy: {len(failed)} files")
        """
        from pathlib import Path
        import shutil

        # Normalize extension format
        if not extension.startswith('.'):
            extension = f'.{extension}'
        if extension.startswith('*.'):
            extension = extension[1:]

        # Convert to Path objects
        source_path = Path(source_dir)
        dest_path = Path(dest_dir)

        # Validate source directory
        if not source_path.exists():
            raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

        # Create destination directory
        dest_path.mkdir(parents=True, exist_ok=True)

        # Initialize counters and lists
        copied_count = 0
        failed_files = []
        copied_files = []

        # Search pattern for files
        pattern = f'*{extension}'

        # Find all matching files recursively
        for source_file in source_path.rglob(pattern):
            try:
                if flatten:
                    # Copy to destination root with unique filename
                    dest_file_path = dest_path / source_file.name
                    dest_file_path = FileHandler._get_unique_path(dest_file_path)
                elif preserve_structure:
                    # Preserve relative directory structure
                    relative_path = source_file.relative_to(source_path)
                    dest_file_path = dest_path / relative_path
                    dest_file_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # Default: flatten structure
                    dest_file_path = dest_path / source_file.name
                    dest_file_path = FileHandler._get_unique_path(dest_file_path)

                # Copy file
                shutil.copy2(source_file, dest_file_path)

                copied_count += 1
                copied_files.append((str(source_file), str(dest_file_path)))

                if verbose:
                    print(f"복사 완료: {source_file.name} -> {dest_file_path}")

            except Exception as e:
                failed_files.append((str(source_file), str(e)))
                if verbose:
                    print(f"복사 실패: {source_file.name} - 오류: {e}")

        if verbose:
            print(f"\n총 {copied_count}개의 {extension} 파일이 복사되었습니다.")
            if failed_files:
                print(f"{len(failed_files)}개의 파일 복사에 실패했습니다.")

        return copied_count, failed_files, copied_files


    @staticmethod
    def _get_unique_path(file_path: Path) -> Path:
        """
        Generate unique file path by adding suffix if file already exists.

        Args:
            file_path (Path): Original file path

        Returns:
            Path: Unique file path
        """
        if not file_path.exists():
            return file_path

        stem = file_path.stem
        suffix = file_path.suffix
        parent = file_path.parent

        counter = 1
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1


    @staticmethod
    def batch_copy_files(copy_tasks: list, verbose: bool = True) -> dict:
        """
        Execute multiple file copy tasks with different extensions or directories.

        Args:
            copy_tasks (list): List of dictionaries with copy task parameters
                Each dict should have: source_dir, dest_dir, extension, and optional flatten/preserve_structure
            verbose (bool): If True, print progress for each task

        Returns:
            dict: Results for each task with statistics

        Example:
            tasks = [
                {
                    'source_dir': '/source_folder_a',
                    'dest_dir': '/dest_folder/data_a',
                    'extension': '.db',
                    'flatten': True
                },
                {
                    'source_dir': '/source_folder_b',
                    'dest_dir': '/dest_folder/data_b',
                    'extension': '.csv',
                    'flatten': True
                }
            ]

            results = FileHandler.batch_copy_files(tasks)

            for i, task in enumerate(tasks):
                print(f"Task {i+1}: Copied {results[i]['copied_count']} {task['extension']} files")
        """
        results = {}

        for i, task in enumerate(copy_tasks):
            if verbose:
                print(f"\n작업 {i+1}/{len(copy_tasks)} 시작:")
                print(f"  소스: {task['source_dir']}")
                print(f"  대상: {task['dest_dir']}")
                print(f"  확장자: {task['extension']}")
                print("-" * 50)

            # Extract parameters with defaults
            source_dir = task['source_dir']
            dest_dir = task['dest_dir']
            extension = task['extension']
            flatten = task.get('flatten', True)
            preserve_structure = task.get('preserve_structure', False)

            # Execute copy task
            copied, failed, files = FileHandler.copy_files_by_extension(
                source_dir=source_dir,
                dest_dir=dest_dir,
                extension=extension,
                flatten=flatten,
                preserve_structure=preserve_structure,
                verbose=verbose
            )

            # Store results
            results[i] = {
                'task': task,
                'copied_count': copied,
                'failed_files': failed,
                'copied_files': files,
                'success_rate': copied / (copied + len(failed)) * 100 if (copied + len(failed)) > 0 else 0
            }

        if verbose:
            print("\n" + "=" * 50)
            print("전체 작업 요약:")
            total_copied = sum(r['copied_count'] for r in results.values())
            total_failed = sum(len(r['failed_files']) for r in results.values())
            print(f"  총 복사된 파일: {total_copied}개")
            print(f"  총 실패한 파일: {total_failed}개")
            if (total_copied + total_failed) > 0:
                print(f"  전체 성공률: {total_copied / (total_copied + total_failed) * 100:.1f}%")

        return results


class PathFinder:
    """
    Interactive directory exploration utility for step-by-step folder traversal.
    Useful when you don't know the folder structure and want to explore gradually
    without overwhelming output from os.walk.
    """
    
    def __init__(self, start_path='.'):
        self.current_path = os.path.abspath(start_path)
    
    def go_up_n_level(self, n_level: int = 1, set_current: bool = True):
        """
        Navigate up directory levels.
        
        Args:
            n_level (int): Number of levels to go up
            set_current (bool): Whether to update current_path or just return new path
            
        Returns:
            str: New path if set_current is False
        """
        new_path = self.current_path
        for _ in range(n_level):
            new_path = os.path.abspath(os.path.join(new_path, os.pardir))
        
        if set_current:
            self.current_path = new_path
        else:
            return new_path

    def get_one_depth(self, input_path: str = '') -> tuple:
        """
        Get directories and files at one depth level using os.scandir.
        
        Args:
            input_path (str): Path to scan (uses current_path if empty)
            
        Returns:
            tuple: (path, directories, files)
        """
        if not len(input_path):
            input_path = self.current_path
        
        try:
            with os.scandir(input_path) as entries:
                dirs = list()
                files = list()
                for entry in entries:
                    if entry.is_dir():
                        dirs.append(entry.name)
                    elif entry.is_file():
                        files.append(entry.name)
                return input_path, dirs, files
        except FileNotFoundError:
            return None, [], []

    @staticmethod
    def print_each(label: str, items: list) -> None:
        """
        Print list items with numbering and formatting.
        
        Args:
            label (str): Label for the items
            items (list): Items to print
        """
        if len(items):
            if isinstance(items, list):
                lgh = len(items)
                for k, v in enumerate(sorted(items)):
                    print(f'{label} ({k + 1:0{len(str(lgh))}}/{lgh}): {v}')
            else:
                print(f'{label}: {items}')
            print('')

    def print_result(self, result: tuple) -> None:
        """
        Print formatted result from get_one_depth.
        
        Args:
            result (tuple): Result tuple from get_one_depth
        """
        (root, dirs, files) = result
        self.print_each("Root:", root)
        self.print_each("Sub directories:", dirs)
        self.print_each("Files:", files)
