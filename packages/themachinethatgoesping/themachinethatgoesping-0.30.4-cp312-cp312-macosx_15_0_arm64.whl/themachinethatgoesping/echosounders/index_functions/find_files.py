# This file is authored by Peter Urban, Ghent University, and is subject to the MPL-2.0 license.
# SPDX-License-Identifier: MPL-2.0

import os
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Union
import hashlib
from tqdm.auto import tqdm
import numpy as np


def get_hash(file_name: str, max_read_size_mb: Union[int, None] = 5) -> str:
    """
    Calculate the SHA256 hash of a file.

    Parameters
    ----------
    file_name : str
        The path to the file to be hashed.
    max_read_size_mb : Union[int, None], optional
        The maximum size of the file to be read in MB. If the file size is greater than this value,
        the file will be read in chunks and bytes will be skipped in between, by default 5.

    Returns
    -------
    str
        The SHA256 hash of the file.
    """
    skip_bytes = 0

    # If max_read_size_mb is not None, check if the file size is greater than max_read_size_mb.
    # If it is, read the file in n_steps chunks and skip bytes in between.
    if max_read_size_mb is not None:
        size_mb = os.stat(file_name).st_size / 1024 / 1024
        if size_mb > max_read_size_mb:
            n_steps = max_read_size_mb //( 4096/1024/1024)
            skip_bytes = int(1024*1024*(size_mb / n_steps)) - 4096

    bytes_read = 0

    # Calculate the SHA256 hash of the file.
    hash_sha256 = hashlib.sha256()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
            if skip_bytes > 0:
                f.seek(skip_bytes, os.SEEK_CUR)
            bytes_read += 4096

    return hash_sha256.hexdigest()


def group_by_hash(file_paths: List[str], hash_read_size_mb: Union[int, None] = 5) -> Dict[str, List[str]]:
    """
    Groups a list of file paths by their hash value.

    Parameters
    ----------
    file_paths : List[str]
        A list of file paths to group by hash value.
    hash_read_size_mb : Union[int, None], optional
        The number of megabytes to read from each file when calculating its hash value. If None, the entire file will be read. By default, 5.

    Returns
    -------
    Dict[str, List[str]]
        A dictionary where the keys are hash values and the values are lists of file paths that have that hash value.
    """
    # Create a defaultdict to store the file paths by hash value
    fdict = defaultdict(list)

    # Iterate over each file path and add it to the corresponding hash value in the defaultdict
    for file in file_paths:
        fdict[get_hash(file,hash_read_size_mb)].append(file)

    return fdict


def remove_duplicates(file_paths: List[str], hash_read_size_mb: Union[int, None] = 5, verbose: bool = True) -> List[str]:
    """
    Remove duplicate files from a list of file paths.

    Parameters
    ----------
    file_paths : List[str]
        A list of file paths.
    hash_read_size_mb : Union[int, None], optional
        The size of the chunk to read from the file for hashing. If None, the entire file is read. By default, 5.
    verbose : bool, optional
        Whether to print the number of removed duplicates. By default, True.

    Returns
    -------
    List[str]
        A list of file paths with duplicates removed.
    """
    # Create a dictionary to group files by their basename
    fdict = defaultdict(list)
    # Create a dictionary to count the number of files per folder
    number_files_per_folder = defaultdict(int)
    # Create a list to store the new file paths
    new_file_paths = []

    # Group files by their basename and count the number of files per folder
    for file in file_paths:
        fdict[os.path.basename(file)].append(file)
        number_files_per_folder[os.path.dirname(file)] += 1

    # Iterate over the files grouped by their basename
    for f_name,f_paths  in tqdm(fdict.items(),desc='removing duplicates', delay=3):
        # If there are multiple files with the same basename
        if len(f_paths) > 1:
            # Group the files by their hash
            files_per_hash = group_by_hash(f_paths,hash_read_size_mb)
            # Iterate over the files grouped by their hash
            for ff_hash, ff_files in files_per_hash.items():
                # Get the number of files in each file's folder
                nf = [number_files_per_folder[os.path.dirname(f)] for f in ff_files]
                # Append the file with the highest number of files in its folder to the new file paths list
                new_file_paths.append(ff_files[np.argmax(nf)])
        # If there is only one file with the basename
        else:
            # Append the file to the new file paths list
            new_file_paths.append(f_paths[0])

    # Print the number of removed duplicates if verbose is True
    if verbose:
        print(f"Removed {len(file_paths) - len(new_file_paths)} duplicate files")

    # Return the new file paths list
    return new_file_paths



def find_files(
    folders: Union[str, List[str]], 
    endings: Union[str, List[str]], 
    followlinks: bool = False,
    remove_duplicated_files: bool = True, 
    verbose: bool = True) -> List[str]:
    """
    Recursively searches for files with the given endings in the specified folders.

    Parameters
    ----------
    folders : Union[str, List[str]]
        The folders to search for files.
    endings : Union[str, List[str]]
        The file endings to match.
    followlinks : bool, optional
        If True, follows symbolic links. Defaults to False.
    remove_duplicated_files : bool, optional
        If True, removes any duplicate files found (comparing first file name then hash). Defaults to True.
    verbose : bool, optional
        If True, prints progress messages indicating how many files were found and how many duplicates were removed (if applicable). Defaults to True.

    Returns
    -------
    List[str]
        A list of file paths (as strings) that match the specified endings and are found in the specified folders.
    """
    # initialize an empty list to store file paths
    file_paths = []

    # convert folders to list if it is a string or a pathlib.Path object
    if isinstance(folders, (str, Path)):
        folders = [folders]

    # convert endings to list if it is a string
    if isinstance(endings, str):
        endings = [endings]
    
    # iterate over each folder and ending to search for files
    for folder in folders:
        for r,d,f in os.walk(folder, followlinks=followlinks):
            for file in f:
                for ending in endings:
                    if file.endswith(ending):
                        file_paths.append(os.path.join(r,file))

    # convert the file paths to strings
    file_paths = [str(f) for f in file_paths]

    # remove duplicated files if specified
    if remove_duplicated_files:
        file_paths_deduplicated = remove_duplicates(file_paths, verbose=False)
        if verbose:
            # print progress message indicating how many files were found and how many duplicates were removed
            if len(file_paths_deduplicated) < len(file_paths):
                print(f"Found {len(file_paths_deduplicated)} files + {len(file_paths) - len(file_paths_deduplicated)} duplicates (discarded)")
            else:
                print(f"Found {len(file_paths_deduplicated)} files")
        return file_paths_deduplicated

    # if not removing duplicated files, simply print progress message indicating how many files were found
    if verbose:
        print(f"Found {len(file_paths)} files")

    return file_paths
    
def find_folders_with_files(
    folders: Union[str, List[str]], 
    endings: Union[str, List[str]], 
    followlinks: bool = False,
    verbose: bool = True) -> List[str]:
    """
    Find folders that contain files with specified endings.

    Args:
        folders (Union[str, List[str]]): Path or list of paths to search for files.
        endings (Union[str, List[str]]): File endings to filter files.
        followlinks (bool, optional): Whether to follow symbolic links. Defaults to False.
        verbose (bool, optional): Whether to display progress information. Defaults to True.

    Returns:
        List[str]: List of folders that contain files with specified endings.
    """

    file_paths = find_files(folders,endings,remove_duplicated_files=False,followlinks=followlinks,verbose=verbose)

    folders_with_files = list(set([os.path.dirname(f) for f in file_paths]))

    return folders_with_files


    