
#  Copyright (C) 2025 Y Hsu <yh202109@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public license as published by
#  the Free software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details
#
#  You should have received a copy of the GNU General Public license
#  along with this program. If not, see <https://www.gnu.org/license/>


import os
import json
import pandas as pd
import time
import numpy as np
import pypdf 
import hashlib

class LsrTree:
    def __init__(self, path="", outfmt="list", with_counts=False, count_str="", with_file_label=False, label_str=""):
        """
        Initialize the LsrTree object.

        Args:
            path (str): The path to the directory to list files from. Defaults to an empty string.
            outfmt (str): The output format for listing files. Must be one of 'list', 'json', 'string', 'dataframe', 'tree'. Defaults to 'list'.
            with_counts (bool): Whether to include the counts of files in the tree structure. Defaults to False.
            with_file_label (bool): Whether to include the label of known files in the dataframe output. Defaults to False.
            count_str (str): The string to use for search for the count of files. Defaults to an empty string.
            label_str (str): The string to use for label files. Defaults to an empty string.
        """
        if path and path.endswith('/'):
            path = path[:-1]
        self.path = path
        self.outfmt = outfmt
        self.with_counts = with_counts
        self.count_str = count_str

    def list_files(self):
        """
        List files in the specified directory based on the output format.

        Returns:
            list or str or pd.DataFrame: The list of files, JSON string, or DataFrame based on the output format.

        Examples:
            >>> lsr = LsrTree("/path/to/directory", outfmt="list")
            >>> lsr.list_files()
            ['file1.txt', 'file2.txt', 'file3.txt']
        """
        if not os.path.exists(self.path):
            print(f"Path '{self.path}' does not exist.")
            return

        if not os.listdir(self.path):
            print(f"Path '{self.path}' is an empty folder.")
            return []

        assert self.outfmt in ["list", "json", "string", "dataframe", "tree"], "Invalid output format. Must be one of 'list', 'json', 'string', 'tree', or 'dataframe'."

        if self.outfmt == "json":
            return self.list_files_json()
        elif self.outfmt == "list":
            return self.list_files_list()
        elif self.outfmt == "dataframe":
            return self.list_files_dataframe()
        elif self.outfmt == 'tree':
            return self.list_files_tree()
        else:
            return self.list_files_string()

    def list_files_json(self):
        """
        List files in the specified directory and return the result as a JSON string.

        Returns:
            str: The JSON string representing the file list.
        """
        data = {}
        idx = 0
        for s0, d0, f0 in sorted(os.walk(self.path)):
            if s0.startswith(self.path):
                s1 = s0[len(self.path):] if len(s0) > len(self.path) else ""
            else:
                s1 = s0 
            n1 = s1.count(os.sep)
            data[idx] = {"path": s1, "level": n1, "folders": d0, "files": f0}
            idx = idx + 1
        return json.dumps(data)

    def list_files_list(self):
        """
        List files in the specified directory and return the result as a list.

        Returns:
            list: The list of files.
        """
        files = []
        for s0, d0, f0 in sorted(os.walk(self.path)):
            if s0.startswith(self.path):
                s1 = s0[len(self.path):] if len(s0) > len(self.path) else ""
            else:
                s1 = s0 
            for f1 in sorted(f0):
                files.append(os.path.join(s1, f1))
            if len(f0) == 0 and len(d0) == 0:
                files.append(s1 + "/(((empty folder)))")
        return files

    @staticmethod
    def get_md5(file_path):
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None


    def list_files_dataframe(self):
        """
        List files in the specified directory and return the result as a pandas DataFrame.

        Returns:
            pd.DataFrame: The DataFrame representing the file list.
        """
        data = []
        for s0, d0, f0 in sorted(os.walk(self.path)):
            if s0.startswith(self.path):
                s1 = s0[len(self.path):] if len(s0) > len(self.path) else ""
            else:
                s1 = s0 
            level = s1.count(os.sep)
            if level == 0:
                s1 = "."
            if len(f0) > 0:
                for f1 in sorted(f0):
                    file_path = os.path.join(s0, f1)
                    file_size = os.path.getsize(file_path)
                    file_modified = time.ctime(os.path.getmtime(file_path))
                    file_created = time.ctime(os.path.getctime(file_path))
                    file_type = f1.split(".")[-1]
                    num_pages = None
                    num_columns = None
                    num_rows = None
                    file_md5 = self.get_md5(file_path)
                    if file_type == "xlsx":
                        try:
                            excel_file = pd.ExcelFile(file_path)
                            num_pages = len(excel_file.sheet_names)
                            first_sheet = excel_file.sheet_names[0]
                            sheet = excel_file.parse(first_sheet)
                            num_columns = sheet.shape[1]
                            num_rows = sheet.shape[0]
                        except pd.errors.EmptyDataError:
                            num_pages = 0
                            num_columns = 0
                            num_rows = 0
                    elif file_type == "sas7bdat":
                        try:
                            sas_file = pd.read_sas(file_path)
                            num_columns = sas_file.shape[1]
                            num_rows = sas_file.shape[0]
                        except pd.errors.EmptyDataError:
                            num_columns = 0
                            num_rows = 0
                    elif file_type == "csv":
                        try:
                            csv_file = pd.read_csv(file_path)
                            num_columns = csv_file.shape[1]
                            num_rows = csv_file.shape[0]
                        except pd.errors.EmptyDataError:
                            num_columns = 0
                            num_rows = 0
                    elif file_type == "pdf":
                        with open(file_path, "rb") as f:
                            pdf = pypdf.PdfReader(f, strict=False)
                            num_pages = pdf.get_num_pages()

                    data.append((s1, level + 1, "file", f1, str(file_size), file_modified, file_created, file_type, str(num_pages), str(num_columns), str(num_rows), file_md5))
            elif len(d0) == 0:
                data.append((s1, level, "folder", "<<<((( Empty Folder )))>>>", None, None, None, None, None, None, None))
        df = pd.DataFrame(data, columns=["path", "level", "type", "file", "size_in_bytes", "modified", "created", "file_type", "N_page", "N_column", "N_row", "md5"])
        return df

    def list_files_string(self):
        """
        List files in the specified directory using the default output format.

        Returns:
            str: The file list as a string.
        """
        out0 = []
        for s0, d0, f0 in sorted(os.walk(self.path)):
            if s0.startswith(self.path):
                s1 = s0[len(self.path):] if len(s0) > len(self.path) else ""
            else:
                s1 = s0 
            level = s1.count(os.sep)
            if level == 0:
                s1 = s0
            indent = "... " * (level)
            out0.append(f"{indent}{os.path.basename(s1)}/")
            subindent = "... " * (level + 1)
            for f1 in sorted(f0):
                out0.append(f"{subindent}{f1}")
            if len(f0) == 0 and len(d0) == 0:
                out0.append(f"{subindent}(((empty folder)))") 

        return "\n".join(out0)

    def list_files_tree(self):
        """
        List files in the specified directory and return the result as a tree structure.

        Returns:
            str: The tree structure representing the file list.
        """
        pre = ['', '    ', '│   ', '├── ', '└── ', '  ']
        data = []
        dir_path = os.path.dirname(self.path)

        for s0, d0, f0 in sorted(os.walk(self.path)):
            if s0.startswith(dir_path):
                s1 = s0[len(dir_path):] if len(s0) > len(dir_path) else ""
            else:
                s1 = s0 
            if s1 and s1.startswith('/'):
                s1 = s1[1:] 
            level = s1.count(os.sep)
            if len(d0) + len(f0) > 0:
                if self.with_counts:
                    data.append((os.path.dirname(s1), level, "folder", os.path.basename(s1), f"{pre[5]}............ [Count: F={len(f0)}; D={len(d0)}]"))
                else:
                    data.append((os.path.dirname(s1), level, "folder", os.path.basename(s1), ""))
                for index, f1 in enumerate(sorted(f0)):
                    data.append((s1, level + 1, "file", f1, ""))
                for index, d1 in enumerate(sorted(d0)):
                    data.append((s1, level + 1, "folder", d1, ""))
            else:
                if self.with_counts:
                    data.append((os.path.dirname(s1), level, "folder", os.path.basename(s1), f"{pre[5]}............ [Count: Empty Folder]"))
                else:
                    data.append((os.path.dirname(s1), level, "folder", os.path.basename(s1), ""))

        colnames = ["path", "level", "type", "file", "property"]
        df0 = pd.DataFrame(data, columns=colnames)
        df0['row_index'] = df0.index

        df = df0.groupby(df0.columns.difference(['property', 'row_index']).tolist(), sort=False).agg({'row_index': 'max', 'property': lambda x: ''.join(x)}).reset_index().sort_values('row_index')
        prelst = pd.DataFrame([['' for _ in range(df['level'].max())] for _ in range(len(df))])
        prelst = pd.concat([prelst, df], axis=1).sort_values('row_index')
        prelst.reset_index(drop=True, inplace=True)
        prelst['row_index'] = prelst.index

        for index, row in prelst.iterrows():
            if row['level'] > 0:
                prelst.loc[index, :(row['level'] - 1)] = [pre[1]] * (row['level'])

        folder_paths = prelst[prelst['type'] == 'folder'][['path', 'file', 'level']].apply(lambda row: (os.path.join(row['path'], row['file']), row['level']), axis=1)
        for folder_path, level in folder_paths:
            index_set = prelst[prelst['path'] == folder_path]['row_index']

            if not index_set.empty:
                min_row_index = index_set.min()
                max_row_index = index_set.max()
                prelst.loc[(min_row_index):(max_row_index), level] = [pre[2]] * (max_row_index - min_row_index + 1)
                prelst.loc[index_set, level] = [pre[3]] * len(index_set)
                prelst.loc[max_row_index, level] = pre[4]

        prelst['file'] = prelst.apply(lambda row: row['file'] + '/' + row['property'] if row['type'] == 'folder' else row['file'], axis=1)

        prelst = prelst.loc[:, :'file']
        prelst_joined = prelst.apply(lambda row: ''.join(row), axis=1)
        return prelst_joined

if __name__ == "__main__":
    #lsr = LsrTree("mtbp3/data/test_lsr", outfmt="list")
    #print(lsr.list_files())
    pass


