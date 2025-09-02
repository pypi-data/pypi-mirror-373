# This file is authored by Peter Urban, Ghent University, and is subject to the MPL-2.0 license.
# SPDX-License-Identifier: MPL-2.0

import os
from pathlib import Path
import pickle
from collections import defaultdict
from typing import List, Dict, Union

def get_index_path(
    file_path: Union[str, Path], 
    index_root: Union[str, Path, None] = None, 
    index_file_ending: str = '.tmtgp.index', 
    create_dir: bool = True) -> Path:
    """Return the path to the index file for a given folder path

    Parameters
    ----------
    file_path : str or Path
        The path to the file that is indexed
    index_root : str or Path, optional
        The path to the root folder containing all index files. If None, the index file will be in the same folder as the data files
    index_name : str, optional
        The name of the index file
    create_dir : bool, optional
        If true: create a subdirectory, by default True

    Returns
    -------
    Path
        The path to the index file
    """
    
    if index_root is None:
        return str(Path(file_path + index_file_ending))
            
    index_file = Path(os.path.abspath(index_root))
    file_path = Path(os.path.abspath(file_path))
    root_path = 'root_' + file_path.parts[0]
    root_path = root_path.replace(':', '')

    index_file = Path(str(index_file.joinpath(root_path, *file_path.parts[1:])) + index_file_ending)
    
    if create_dir:
        os.makedirs(index_file.parent, exist_ok=True)
    
    return str(index_file)


def get_index_paths(
    file_paths: List[str], 
    index_file_ending: str = '.tmtgp.index', 
    index_root: str = 'index', 
    update_index: Dict[str, str] = None, 
    verbose: bool = False, 
    create_dir: bool = True) -> Dict[str, str]:
    """Load index files for a given list of file paths

    Parameters
    ----------
    file_paths : list of str
        The list of file paths to load index files for
    index_name : str, optional
        The name of the index file, by default 'tmtgp.index'
    index_root : str, optional
        The path to the root folder containing all index files, by default 'index'
    update_index : dict, optional
        A dictionary to update with the loaded index data, by default None
    verbose : bool, optional
        If true: print verbose output, by default False
    create_dir : bool, optional
        If true: create a subdirectory, by default True

    Returns
    -------
    dict
        A dictionary containing the loaded index index data
    """
    
    if update_index is None:
        index_paths = {}
    else:
        index_paths = update_index
        
    loaded_index_index_files = set()
    
    # look for existing files in each folder
    for fp in file_paths:
        try:
            folder_path, file = os.path.split(fp)
            
            index_file = get_index_path(fp, index_root, index_file_ending, create_dir=create_dir)            
            
            if index_file in loaded_index_index_files:
                continue
                
            loaded_index_index_files.add(index_file)
            index_paths[fp] = index_file
        except Exception as e:
            raise e
            pass
            
    return index_paths
