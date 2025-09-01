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