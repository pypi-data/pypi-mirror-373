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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class catPlotter:
    """
    A class for creating categorical box plots and strip plots.

    Parameters:
    - df (pandas.DataFrame): The input DataFrame.
    - group_col (str): The column name for grouping the data.
    - y_col (str): The column name for the y-axis variable.
    - x_col (str): The column name for the x-axis variable.
    - grid_col (str, optional): The column name for creating subplots based on a grid. Default is None.
    - grid_wrap (int, optional): The number of columns in the grid. Default is None.
    - pt_size (int, optional): The size of the points in the strip plot. Default is 5.
    - x_scale_base (int, optional): The base for the x-axis scale. Default is 10.
    - title (str, optional): The title of the plot. Default is an empty string.
    - fig_size_0 (int, optional): The width of the figure. Default is 7.
    - fig_size_1 (int, optional): The height of the figure. Default is 6.
    - grid_kws (dict, optional): Additional keyword arguments for the FacetGrid. Default is None.

    Methods:
    - update_parameters(**kwargs): Update the parameters of the catPlotter instance.
    - boxplot(): Create a categorical box plot and strip plot.
    - lineplot(): Create a line plot by categorical group_col on the x-axis with grid option.
    - generate_example_dataset(): Generate an example dataset.

    Raises:
    - ValueError: If an invalid parameter is provided or if group_col, x_col, or y_col is not found in DataFrame columns.
    """

    def __init__(self, df, y_col, group_col=None, grid_col=None, grid_wrap=None, x_col=None, pt_size=5, y_scale_base=0, x_scale_base=0, title="", fig_size_0=7, fig_size_1=6, point_position='swarm', x_label_rotate=None, grid_kws=None, line_color_col=None):

        if df is None:
            df = self.generate_example_dataset()
        self.df = df

        if not grid_col or not grid_col in df.columns:
            grid_col = ""
        self.grid_col = grid_col

        if not grid_wrap:
            grid_wrap = 1

        self.point_position = point_position
        self.grid_wrap = grid_wrap
        self.group_col = group_col
        self.y_col = y_col
        self.x_col = x_col
        self.pt_size = pt_size
        self.x_scale_base = x_scale_base
        self.y_scale_base = y_scale_base
        self.title = title
        self.fig_size_0 = fig_size_0
        self.fig_size_1 = fig_size_1
        self.x_label_rotate = x_label_rotate
        self.line_color_col = line_color_col

        if group_col and group_col in df.columns:
            self.group_order = sorted(df[self.group_col].unique())
        else:
            self.group_order = []
        if x_col and x_col in df.columns:
            self.x_order = sorted(df[self.x_col].unique())
        else:
            self.x_order = []
        if grid_kws is None:
            grid_kws = {}
        
        self.grid_kws = grid_kws
        sns.set_style("ticks", {'axes.grid': True})
    
    def update_parameters(self, **kwargs):
        valid_parameters = [
            "y_col", "group_col", "grid_col", "grid_wrap", "x_col", "pt_size",
            "y_scale_base", "x_scale_base", "title", "fig_size_0", "fig_size_1",
            "point_position", "x_label_rotate", "line_color_col"
        ]
        not_valid_parameters = [
            "df", "grid_kws"
        ]
        for key, value in kwargs.items():
            if key in not_valid_parameters:
                raise ValueError(f"Unable to update parameter: {key}. Please create a new plot with the updated parameters.")
            if key not in valid_parameters:
                raise ValueError(f"Invalid parameter: {key}")
            setattr(self, key, value)
        
        if 'group_col' in kwargs:
            group_col = kwargs.get('group_col')
            if group_col and group_col in self.df.columns:
                self.group_order = sorted(self.df[self.group_col].unique())
            else:
                self.group_order = []
        if 'x_col' in kwargs:
            x_col = kwargs.get('x_col')
            if x_col and x_col in self.df.columns:
                self.x_order = sorted(self.df[self.x_col].unique())
            else:
                self.x_order = []
        if 'grid_col' in kwargs:
            grid_col = kwargs.get('grid_col')
            if not grid_col or not grid_col in self.df.columns:
                grid_col = ""
            self.grid_col = grid_col
        if 'grid_wrap' in kwargs:
            grid_wrap = kwargs.get('grid_wrap')
            if not grid_wrap:
                grid_wrap = 1

    def boxplot(self):

        if self.x_col not in self.df.columns or self.y_col not in self.df.columns:
            raise ValueError("x_col or y_col not found in DataFrame columns")

        if self.grid_col:
            df = self.df.sort_values(by=[self.grid_col, self.x_col]).reset_index()

            g = sns.FacetGrid(df, col=self.grid_col, col_wrap=self.grid_wrap, height=self.grid_kws.get('height', 2.5), aspect=self.grid_kws.get('aspect', 3), sharex=True, sharey=False, legend_out=True)
            g.map(sns.boxplot, self.y_col, self.x_col, order=self.x_order, whis=[0, 100], width=0.4, palette=sns.light_palette("#79C", n_colors=len(self.x_order)), hue_order=self.x_order)
            if self.point_position=='swarm': 
                g.map(sns.swarmplot, self.y_col, self.x_col, order=self.x_order, size=self.pt_size, marker='o', color=".3", alpha=0.5, palette=sns.dark_palette("#69d", reverse=True, n_colors=len(self.x_order)), hue_order=self.x_order)
            else: 
                g.map(sns.stripplot, self.y_col, self.x_col, order=self.x_order, size=self.pt_size, marker='*', color=".3", alpha=0.5, jitter=0.3, palette=sns.dark_palette("#69d", reverse=True, n_colors=len(self.x_order)), hue_order=self.x_order)
            g.set_titles("{col_name}")
            g.set(xlabel=None, xticklabels=[])
            g.despine(trim=False, left=False)

            if self.y_scale_base > 0:
                plt.xscale("log", base=self.y_scale_base)

            for ax in g.axes.flat:
                tmp = ax.get_xlim()
                font_size = int(ax.xaxis.label.get_fontsize() * 0.9)
                subset_df = df[df[self.grid_col] == ax.get_title()]
                x_counts = subset_df.groupby(self.x_col, dropna=True).size()
                geometric_means = subset_df.groupby(self.x_col)[self.y_col].apply(lambda x: np.exp(np.mean(np.log(x))))
                nan_percentage = subset_df.groupby(self.x_col)[self.y_col].apply(lambda x: (x.isna() | np.isnan(x)).mean() * 100)
                for i in list(range(0, len(self.x_order))):
                    if self.x_order[i] in x_counts.index:
                        count = x_counts[self.x_order[i]]
                        mean = geometric_means[self.x_order[i]]
                        nanperct = nan_percentage[self.x_order[i]]
                        ax.text(tmp[1], i, f'N={count}; %m={nanperct:.1f}\n♦GM={mean:.2f}', va='center', ha='left', fontsize=font_size)
                        ax.plot(mean, i, marker='d', markersize=max(int(font_size*.6),1), color="#248")

            plt.suptitle(self.title, weight='bold')
            plt.tight_layout() 

        else:
            df = self.df.sort_values(self.x_col).reset_index()
            f, ax = plt.subplots(figsize=(self.fig_size_0, self.fig_size_1))

            sns.boxplot(df, x=self.y_col, y=self.x_col, order=self.x_order, whis=[0, 100], width=0.4, palette=sns.light_palette("#79C", n_colors=len(self.x_order)), hue_order=self.x_order)
            if self.point_position=='swarm': 
                sns.swarmplot(df, x=self.y_col, y=self.x_col, order=self.x_order, size=self.pt_size, marker='o', color=".3", alpha=0.3, palette=sns.dark_palette("#69d", reverse=True, n_colors=len(self.x_order)), hue_order=self.x_order)
            else: 
                sns.stripplot(df, x=self.y_col, y=self.x_col, order=self.x_order, size=self.pt_size, marker='*', color=".3", alpha=0.3, jitter=0.3, palette=sns.dark_palette("#69d", reverse=True, n_colors=len(self.x_order, hue_order=self.x_order)) )

            if self.y_scale_base > 0:
                plt.xscale("log", base=self.y_scale_base)

            x_counts = df.groupby(self.x_col, dropna=True).size()
            geometric_means = df.groupby(self.x_col)[self.y_col].apply(lambda x: np.exp(np.mean(np.log(x))))
            nan_percentage = df.groupby(self.x_col)[self.y_col].apply(lambda x: (x.isna() | np.isnan(x)).mean() * 100)
            font_size = int(ax.xaxis.label.get_fontsize() * 0.9)
            tmp = ax.get_xlim()
            for i in list(range(0, len(self.x_order))):
                count = x_counts[self.x_order[i]]
                mean = geometric_means[self.x_order[i]]
                nanperct = nan_percentage[self.x_order[i]]
                ax.text(tmp[1], i, f'N: {count}\n♦GM: {mean:.2f}\n%m: {nanperct:.1f}', va='center', ha='left')
                ax.plot(mean, i, marker='d', markersize=max(int(font_size*.6),1), color="#248")

            plt.tight_layout()
            ax.set_title(self.title)
            ax.xaxis.grid(True)
            ax.set(ylabel="")
            sns.despine(trim=False, left=True)

    @staticmethod
    def generate_example_dataset():
        """
        Generate an example dataset.

        Returns:
            pandas.DataFrame: The example dataset.
        """
        grid = ['G1'] * 50 + ['G2'] * 50
        group = np.repeat(['A', 'B', 'C', 'D', 'E'], 20)
        y_value = np.random.normal(0, 1, size=100)
        x_value = np.tile(['C1', 'C2', 'C3', 'C4'], 25)
        x_group = np.repeat(range(25),4)
        df = pd.DataFrame({'Group': group, 'Value': y_value, 'Grid': grid, 'CValue': x_value, 'CValueGroup': x_group})
        df.loc[df['Group'] == 'B', 'Value'] += 2
        df.loc[df['Group'] == 'C', 'Value'] += 3
        df.loc[df.index[0], 'Value'] = np.nan
        df.loc[df.index[1], 'Value'] = None 

        df['Value'] = np.exp(np.abs(df['Value'])+6)
        return df

    def lineplot(self):

        if self.group_col not in self.df.columns or self.y_col not in self.df.columns or self.x_col not in self.df.columns:
            raise ValueError("group_col, x_col, or y_col not found in DataFrame columns")

        if self.grid_col:
            df_grouped = self.df.groupby([self.x_col, self.group_col, self.grid_col])[self.y_col].nunique()
        else:
            df_grouped = self.df.groupby([self.x_col, self.group_col])[self.y_col].nunique()
        if (df_grouped > 1).any():
            raise AssertionError("Multiple y_col values found for a combination of x_col and group_col")

        if self.grid_col:
            df = self.df.copy()
            df['GroupedMean'] = df.groupby([self.grid_col, self.group_col])[self.y_col].transform('mean')
            df = df.sort_values([self.grid_col, self.x_col, 'GroupedMean']).reset_index()

            g = sns.FacetGrid(df, col=self.grid_col, col_wrap=self.grid_wrap, height=self.grid_kws.get('height', 3), aspect=self.grid_kws.get('aspect', 2.5), sharex=True, sharey=True, legend_out=True)
            
            if self.point_position=='density':
                if self.y_scale_base > 0:
                    g.map(sns.violinplot, self.x_col, self.y_col, log_scale=self.y_scale_base, fill=False, order=self.x_order)
                else:
                    g.map(sns.violinplot, self.x_col, self.y_col, log_scale=False, fill=False, order=self.x_order)
            else:
                if self.y_scale_base > 0:
                    g.map(sns.violinplot, self.x_col, self.y_col, log_scale=self.y_scale_base, fill=False, order=self.x_order, linewidth=0)
                else:
                    g.map(sns.violinplot, self.x_col, self.y_col, log_scale=False, fill=False, order=self.x_order, linewidth=0)
                    
            if self.line_color_col and self.line_color_col in df.columns:
                g.map(sns.lineplot, self.x_col, self.y_col, self.group_col, sort=True, hue=self.line_color_col, linewidth=0.7)
            else:
                g.map(sns.lineplot, self.x_col, self.y_col, self.group_col, sort=True, hue='GroupedMean', linewidth=0.7)

            g.set_titles("{col_name}")

            if self.y_scale_base > 0:
                plt.yscale("log", base=self.y_scale_base)

            for ax in g.axes.flat:
                tmp = ax.get_ylim()
                font_size = int(ax.xaxis.label.get_fontsize() * 0.9)
                subset_df = df[df[self.grid_col] == ax.get_title()]
                x_counts = subset_df.groupby(self.x_col, dropna=True).size()
                geometric_means = subset_df.groupby(self.x_col)[self.y_col].apply(lambda x: np.exp(np.mean(np.log(x))))
                nan_percentage = subset_df.groupby(self.x_col)[self.y_col].apply(lambda x: (x.isna() | np.isnan(x)).mean() * 100)
                for i in list(range(0, len(self.x_order))):
                    if self.x_order[i] in x_counts.index:
                        count = x_counts[self.x_order[i]]
                        mean = geometric_means[self.x_order[i]]
                        nanperct = nan_percentage[self.x_order[i]]
                        ax.text(i, tmp[1], f'N={count}\n%m={nanperct:.1f}\n♦GM={mean:.2f}', va='top', ha='center', fontsize=font_size)
                        ax.plot(i, mean, marker='d', markersize=max(int(font_size*.6),1), color="#248")
                    if self.x_label_rotate:
                        ax.tick_params(axis='x', rotation=self.x_label_rotate)  
                        #plt.xticks(rotation=self.x_label_rotate)

            ax.set_ylim(top=tmp[1]*1.1) 
            tmp = ax.get_xlim()
            ax.set_xlim(left=tmp[0] - len(self.x_order)*0.05, right=tmp[1] + len(self.x_order)*0.05) 
            plt.suptitle(self.title, weight='bold')
            plt.tight_layout()

        else:
            df = self.df.copy()
            df['GroupedMean'] = df.groupby([self.group_col])[self.y_col].transform('mean')
            df = df.sort_values([self.x_col, 'GroupedMean']).reset_index()
            f, ax = plt.subplots(figsize=(self.fig_size_0, self.fig_size_1))
            
            if self.point_position=='density':
                if self.y_scale_base > 0:
                    sns.violinplot(df, x=self.x_col, y=self.y_col, log_scale=self.y_scale_base, fill=False, order=self.x_order)
                else:
                    sns.violinplot(df, x=self.x_col, y=self.y_col, log_scale=False, fill=False, order=self.x_order)
            else:
                if self.y_scale_base > 0:
                    sns.violinplot(df, x=self.x_col, y=self.y_col, log_scale=self.y_scale_base, fill=False, order=self.x_order, linewidth=0)
                else:
                    sns.violinplot(df, x=self.x_col, y=self.y_col, log_scale=False, fill=False, order=self.x_order, linewidth=0)
            sns.lineplot(df, x=self.x_col, y=self.y_col, hue=self.group_col, sort=True, legend=False)

            if self.y_scale_base > 0:
                plt.yscale("log", base=self.y_scale_base)

            tmp = ax.get_ylim()
            x_counts = df.groupby(self.x_col, dropna=True).size()
            geometric_means = df.groupby(self.x_col)[self.y_col].apply(lambda x: np.exp(np.mean(np.log(x))))
            nan_percentage = df.groupby(self.x_col)[self.y_col].apply(lambda x: (x.isna() | np.isnan(x)).mean() * 100)
            font_size = int(ax.xaxis.label.get_fontsize() * 0.9)
            for i in list(range(0, len(self.x_order))):
                count = x_counts[self.x_order[i]]
                mean = geometric_means[self.x_order[i]]
                nanperct = nan_percentage[self.x_order[i]]
                ax.text(i, tmp[1], f'N={count}\n%m={nanperct:.1f}\n♦GM={mean:.2f}', va='top', ha='center', fontsize=font_size)
                ax.plot(i, mean, marker='d', markersize=max(int(font_size*.6),1), color="#248")

            ax.set_ylim(top=tmp[1]*1.1) 
            tmp = ax.get_xlim()
            ax.set_xlim(left=tmp[0] - len(self.x_order)*0.05, right=tmp[1] + len(self.x_order)*0.05) 
            ax.set_title(self.title)
            ax.xaxis.grid(True)
            if self.x_label_rotate:
                plt.xticks(rotation=self.x_label_rotate)
            plt.tight_layout()
            sns.despine(trim=False, left=False)

if __name__ == "__main__":
    pass
