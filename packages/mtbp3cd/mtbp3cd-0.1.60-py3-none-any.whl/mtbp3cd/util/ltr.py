#  Copyright (C) 2023 Y Hsu <yh202109@gmail.com>
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

import numpy as np
import pandas as pd
import json

def color_str(input_str="", words=None, colors='red', exact=False):
    """
    Colorize specified words in a given string.
    Args:
        input_str (str): The input string in which words will be colorized.
        words (list or str): A list of words or a single word to be colorized in the input string.
        colors (list or str): A list of colors or a single color to be used for colorizing the words. 
                              Supported colors are 'red', 'green', 'yellow', 'blue', 'magenta', and 'cyan'.
    Returns:
        str: The input string with specified words colorized. If input_str is not a string, returns an error message.
             If words is empty or not found in the input string, returns the original input string.
    Raises:
        ValueError: If the length of colors list does not match the length of words list, colors will be repeated to match the length.
    Example:
        >>> color_str("Hello World", ["Hello", "World"], ["red", "blue"])
        '\x1b[31mHello\x1b[0m \x1b[34mWorld\x1b[0m'
    """
    if not isinstance(input_str, str):
        return "input_str must be a string"
    if isinstance(words, str):
        if words:
            words = [words]
        else:
            return input_str
    if isinstance(words, list) and words:
        words = [str(word) for word in words]
        if len(words) == 0:
            return input_str
    else:
        return input_str

    color_dic = {'red': 31, 'green': 32, 'yellow': 33, 'blue': 34, 'magenta': 35, 'cyan': 36}

    if isinstance(colors, str):
        if not colors or colors not in color_dic.keys():
            colors = 'red'  # default color
        colors = [colors.lower()]
    elif isinstance(colors, list):
        colors = [str(c).lower() for c in colors]
        colors = [c if c in color_dic.keys() and c else 'red' for c in colors]
    
    if len(colors) == len(words):
        colors = colors
    else:
        colors = colors * (len(words) // len(colors)) + colors[:len(words) % len(colors)]

    color_strs = [f"\x1b[{color_dic[c]}m" for c in colors]

    output_str = input_str
    if exact:
        for i, word in enumerate(words):
            if output_str.lower() == word.lower():
                output_str = color_strs[i] + output_str + "\x1b[0m"
                continue
    else:
        for i, word in enumerate(words):
            try:
                start = output_str.lower().index(word.lower())
                end = start + len(word)
            except ValueError:
                continue
            output_str = output_str[:start] + color_strs[i] + output_str[start:end] + "\x1b[0m" + output_str[end:]

    return output_str

class ListTree:
    def __init__(self, lst=[], label=[], infmt='path'):
        self.lst = lst
        self.label = label
        self.infmt = infmt
        self.df = pd.DataFrame()
        self.prelst = pd.DataFrame()
        self.tree = pd.DataFrame()
        if isinstance(self.label, str) and self.label == "last_section" and infmt=='dotspace':
            self.label = [str(item).split('.')[-1] if isinstance(item, str) and '.' in item else str(item) for item in self.lst]
    
    def __list_tree_df(self):
        if not isinstance(self.lst, list):
            print('Input should be a list.')
            self.df = pd.DataFrame()
            return
        
        if not self.lst:
            print('Input should be a nonempty list.')
            self.df = pd.DataFrame()
            return
        
        if len(self.lst) <= 1:
            self.df = pd.DataFrame(self.lst, columns=['lst'])
            return
        
        if self.infmt == 'dotspace':
            df0 = pd.DataFrame([[line.split(' ', 1)[0]]+[line] for line in self.lst], columns=['c1', 'property'])
            df0['property'] = df0['property'].apply(lambda x: x.split(' ', 1)[1] if '.pseudo' in x else x)
            df0['lst'] = df0['c1'].str.replace('.', '/')
            df0['lst'] = df0['lst'].apply(lambda x: '/'.join([part.zfill(3) for part in x.split('/')]))
            df0['lst'] = df0['lst'].apply(lambda x: x + '/' if df0['lst'].str.contains(x+'/').any() else x)
            df0 = df0.drop('c1', axis=1)
            df0 = df0.sort_values('lst').reset_index(drop=True)
        else:
            df0 = pd.DataFrame(self.lst, columns=['lst'])
            if len(self.label) > 0:
                df0['property'] = self.label
            else:
                df0['property'] = ''

        df0['lst'] = df0['lst'].str.replace('^/', '', regex=True)
        df0['type'] = df0['lst'].apply(lambda x: True if x.endswith('/') else False)
        
        for index, row in df0.iterrows():
            df0.loc[index, 't1'] = ""
            df0.loc[index, 't0'] = ""

            try:
                r0, r1 = row['lst'].rsplit('/', 1)
                if r1 == "":
                    if '/' in r0:
                        s0, s1 = r0.rsplit('/',1)
                        df0.loc[index, 't1'] = s0
                        df0.loc[index, 't0'] = s1
                    else:
                        df0.loc[index, 't1'] = ""
                        df0.loc[index, 't0'] = r0
                else:
                    df0.loc[index, 't1'] = r0
                    df0.loc[index, 't0'] = r1
            except Exception as e:
                df0.loc[index, 't1'] = ""
                df0.loc[index, 't0'] = row['lst']

        df0 = df0.sort_values(by=['lst']).reset_index(drop=True)
        df0['level'] = df0['lst'].str.count('/') + 1
        df0['level'] = df0['level'] - df0['type']
        
        if df0['level'].min() > 0:
            df0['level'] = df0['level'] - df0['level'].min() + 1
        
        df0['row_index'] = df0.index
        df0 = df0[['lst', 'type', 't1', 't0', 'level', 'row_index', 'property']]
        
        self.df = df0.groupby(df0.columns.difference(['property', 'row_index']).tolist(), sort=False).agg({'row_index': 'max', 'property': lambda x: ''.join(x)}).reset_index().sort_values('row_index')
    
    def __list_tree_pre(self, to_right=False):
        self.__list_tree_df()
        if self.df.empty:
            self.prelst = self.df
            return self.prelst
        
        max_level = self.df['level'].max()
        prelst = pd.DataFrame("", index=self.df.index, columns=range(max_level))
        prelst = pd.DataFrame([['' for _ in range(self.df['level'].max())] for _ in range(len(self.df))])
        prelst = pd.concat([prelst, self.df[['t0','property','t1','type','level','row_index']]], axis=1).sort_values('row_index')
        prelst.reset_index(drop=True, inplace=True)
        prelst['row_index'] = prelst.index
        
        if to_right:
            pre = ['', '    ', '   │', ' ──┤', ' ──┘', '  ']
        else:
            pre = ['', '    ', '│   ', '├── ', '└── ', '  ']
        
        t1_list = prelst[prelst['type'] == True][['t1','level','t0']]
        
        if t1_list.empty:
            self.prelst = self.df['lst']
            return self.prelst
        
        for index, row in prelst.iterrows():
            if row['level'] > 0:
                prelst.loc[index, :(row['level'] - 1)] = [pre[1]] * (row['level'])
        
        for index, row in t1_list.iterrows():
            index_set = prelst[prelst['t1'] == row['t1']+'/'+row['t0']]['row_index']
            
            if row['t1'] == "":
                index_set = prelst[prelst['t1'] == row['t0']]['row_index']
            else:
                index_set = prelst[prelst['t1'] == row['t1']+'/'+row['t0']]['row_index']
            
            if not index_set.empty:
                min_row_index = index_set.min()
                max_row_index = index_set.max()
                prelst.loc[(min_row_index):(max_row_index), row['level']] = [pre[2]] * (max_row_index - min_row_index + 1)
                prelst.loc[index_set, row['level']] = [pre[3]] * len(index_set)
                prelst.loc[max_row_index, row['level']] = pre[4]
        
        if to_right:
            prelst['t0'] = prelst.apply(lambda row: row['t0'] if row['type'] == True else row['t0'], axis=1)
            prelst = prelst.loc[:, :'property']
            prelst = prelst.iloc[:, ::-1]
        else:
            prelst['t0'] = prelst.apply(lambda row: row['t0'] + ':' if row['type'] == True else row['t0'], axis=1)
            prelst = prelst.loc[:, :'property']

        if self.infmt == 'dotspace':
            prelst['t0'] = ''
        
        self.prelst = prelst
    
    def list_tree(self, to_right=False):
        """
        Returns a DataFrame representing the tree structure of the object.

        Parameters:
        - to_right (bool): If True, aligns the tree structure to the right by padding with spaces.

        Returns:
        - tree (DataFrame): DataFrame representing the tree structure.
        """
        self.__list_tree_pre(to_right=to_right)
        
        if not isinstance(self.prelst, pd.DataFrame):
            self.tree = pd.DataFrame()
            return self.tree

        if self.prelst.empty:
            self.tree = pd.DataFrame()
            return self.tree

        try:
            out_joined = self.prelst.apply(lambda row: ''.join(row), axis=1)
        except Exception as e:
            print(f"An error occurred: {e}")
        
        if to_right:
            max_length = out_joined.str.len().max()
            out_joined = out_joined.apply(lambda x: x.rjust(max_length))
        
        self.tree = out_joined
        return self.tree


if __name__ == "__main__":
    pass