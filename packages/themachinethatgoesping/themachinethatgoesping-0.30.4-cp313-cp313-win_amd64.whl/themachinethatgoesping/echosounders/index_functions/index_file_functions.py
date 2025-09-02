# This file is authored by Peter Urban, Ghent University, and is subject to the MPL-2.0 license.
# SPDX-License-Identifier: MPL-2.0

import os
from pathlib import Path
import pickle
from collections import defaultdict
from typing import List, Dict, Union
from tqdm.auto import tqdm
from themachinethatgoesping.echosounders import filetemplates      # This is the filereader module for .all/.wcd files

def print_index_file_statistics(
    index_paths: List[str]) :

    Buffers = defaultdict(int)

    for fcp in tqdm(index_paths.values(), delay=1):
        if not os.path.exists(fcp):
            continue
        
        # load the index file
        index = filetemplates.Fileindex.from_file(fcp)
        
        for k,p1,p2 in index.get_index_buffer_header():
            Buffers[k] += p2-p1
            
        for k,p1,p2 in index.get_index_buffer_header():
            Buffers["- Combined -"] += p2-p1

        Buffers["- Source files -"] += index.get_file_size()
        #index.print()

    for k,v in Buffers.items():
        if not k.startswith('-'):
            print(f"{k}: {round(v/1024/1024,2)} 'MB' / {round(100*v/Buffers['- Source files -'],2)} %" )
            
    for k,v in Buffers.items():
        if k.startswith('-'):
            print(f"{k}: {round(v/1024/1024,2)} 'MB' / {round(100*v/Buffers['- Source files -'],2)} %" )

def remove_name_from_index(
    index_paths: List[str],
    name: str) -> None:

    for fcp in tqdm(index_paths.values(), delay=1):
        if not os.path.exists(fcp):
            continue
            
        # load the index file
        index = filetemplates.Fileindex.from_file(fcp)
        index.remove_from_index(name)
        index.update_file(fcp)