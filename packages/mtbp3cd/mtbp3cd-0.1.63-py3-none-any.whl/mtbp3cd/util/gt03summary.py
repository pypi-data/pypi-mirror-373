
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
from scipy.stats import norm

def pd_df_flag_to_category(df):
    flag_cols = [col for col in df.columns if col.lower().endswith('fl')]
    for col in flag_cols:
        if not isinstance(df[col].dtype, pd.CategoricalDtype):
            values = sorted(set(df[col].dropna().unique()))
            if "Y" in values or "N" in values:
                if "N" in values:
                    values.remove("N")
                    values = ["N"] + list(values)
                if "Y" in values:
                    values.remove("Y")
                    values = ["Y"] + list(values)
            elif "{'Y'}" in values or "{'N'}" in values:
                if "{'N'}" in values:
                    values.remove("{'N'}")
                    values = ["{'N'}"] + list(values)
                if "{'Y'}" in values:
                    values.remove("{'Y'}")
                    values = ["{'Y'}"] + list(values)
            df[col] = pd.Categorical(df[col].fillna(""), categories=values, ordered=True)
        else:
            cats = list(df[col].cat.categories)
            if "Y" in cats or "N" in cats:
                if "N" in cats:
                    cats.remove("N")
                    cats = ["N"] + cats
                if "Y" in cats:
                    cats.remove("Y")
                    cats = ["Y"] + cats
            elif "{'Y'}" in cats or "{'N'}" in cats:
                if "{'N'}" in cats:
                    cats.remove("{'N'}")
                    cats = ["{'N'}"] + cats
                if "{'Y'}" in cats:
                    cats.remove("{'Y'}")
                    cats = ["{'Y'}"] + cats
            df[col] = df[col].cat.reorder_categories(cats, ordered=True)
    return 

def crosstab_from_lists(df, rows, cols, perct_within_index=None, col_margin_perct=False, row_margin_perct=False, report_type=1):
    # s.1
    if not isinstance(df, pd.DataFrame):
        raise TypeError("'df' must be a pandas DataFrame.")
    if df.empty:
        raise ValueError("'df' must not be empty.")
    if not rows or not cols:
        raise ValueError("'rows' and 'cols' must be non-empty lists.")
    rows = list(set(rows))
    cols = list(set(cols))
    if not all(col in df.columns for col in rows):
        raise ValueError("All elements in 'rows' must be column names of df.")
    if not all(col in df.columns for col in cols):
        raise ValueError("All elements in 'cols' must be column names of df.")
    if len([x for x in cols if x in rows])>0:
        raise ValueError("The intersection of 'rows' and 'cols' must be empty.")
    # s.2
    if perct_within_index is not None:
        if not isinstance(perct_within_index, list):
            raise ValueError("'perct_within_index' must be a list of column names.")
        for idx in perct_within_index:
            if idx not in rows and idx not in cols:
                raise ValueError(f"'{idx}' must be in either 'rows' or 'cols'.")
    # s.3
    if report_type not in [1, 2]:
        raise ValueError("'report_type' must be either 1 or 2.")
    if not isinstance(col_margin_perct, bool):
        raise ValueError("'col_margin_perct' must be a boolean.")
    if not isinstance(row_margin_perct, bool):
        raise ValueError("'row_margin_perct' must be a boolean.")

    subdf_cols = set(rows + cols)
    if perct_within_index is not None:
        subdf_cols.update(perct_within_index)
    subdf = df[list(subdf_cols)].copy()
    pd_df_flag_to_category(subdf)

    ct1 = pd.crosstab([subdf[r] for r in rows], [subdf[c] for c in cols], margins=True)
    
    if perct_within_index is not None and len(perct_within_index) > 0:
        ct_perc = ct1.copy().astype(float)
        ct_total = ct1.copy().astype(float)
        idx_names = [i for i in rows if i in perct_within_index]
        col_names = [i for i in cols if i in perct_within_index]

        if idx_names and not col_names:
            idx_vals = ct1.index.droplevel([n for n in ct1.index.names if n not in idx_names])
            unique_idx_combos = idx_vals.unique()
            for combo in unique_idx_combos:
                mask = idx_vals == combo
                subtable = ct1[mask].drop("All", axis=1, errors="ignore")
                ct_total.loc[mask, :] = subtable.values.sum() 

            if not row_margin_perct:
                if "All" in ct_total.columns.get_level_values(0):
                    ct_total.loc[:, ct_total.columns.get_level_values(0) == "All"] = np.nan

            if not col_margin_perct:
                if "All" in ct_total.index.get_level_values(0):
                    ct_total.loc[ct_total.index.get_level_values(0) == "All", :] = np.nan

            ct_perc = ct1 / ct_total 
            ct_perc = (100*ct_perc).round(1)

        elif col_names and not idx_names:
            col_vals = ct1.columns.droplevel([n for n in ct1.columns.names if n not in col_names])
            unique_col_combos = col_vals.unique()
            for combo in unique_col_combos:
                mask = col_vals == combo
                subtable = ct1.loc[:, mask].drop("All", axis=0, errors="ignore", level=0)
                ct_total.loc[:,mask] = subtable.values.sum() 

            if not col_margin_perct:
                if "All" in ct_total.index.get_level_values(0):
                    ct_total.loc[ct_total.index.get_level_values(0) == "All", :] = np.nan

            if not row_margin_perct:
                if "All" in ct_total.columns.get_level_values(0):
                    ct_total.loc[:, ct_total.columns.get_level_values(0) == "All"] = np.nan

            ct_perc = ct1 / ct_total 
            ct_perc = (100*ct_perc).round(1)

        elif col_names and idx_names:
            idx_vals = ct1.index.droplevel([n for n in ct1.index.names if n not in idx_names])
            col_vals = ct1.columns.droplevel([n for n in ct1.columns.names if n not in col_names])
            unique_idx_combos = idx_vals.unique()
            unique_col_combos = col_vals.unique()
            for idx_combo in unique_idx_combos:
                idx_mask = idx_vals == idx_combo
                for col_combo in unique_col_combos:
                    col_mask = col_vals == col_combo
                    subtable = ct1.loc[idx_mask, col_mask].drop("All", axis=1, errors="ignore").drop("All", axis=0, errors="ignore")
                    ct_total.loc[idx_mask, col_mask] = subtable.values.sum()

                if row_margin_perct:
                    if "All" in ct_total.columns.get_level_values(0):
                        subtable = ct1.loc[idx_mask, 'All'].drop("All", axis=0, errors="ignore")
                        ct_total.loc[idx_mask, ct_total.columns.get_level_values(0) == "All"] = subtable.values.sum()
                else:
                        ct_total.loc[idx_mask, ct_total.columns.get_level_values(0) == "All"] = np.nan

            if col_margin_perct:
                if "All" in ct_total.index.get_level_values(0):
                    for col_combo in unique_col_combos:
                        col_mask = col_vals == col_combo
                        subtable = ct1.loc['All', col_mask].drop("All", axis=1, errors="ignore")
                        ct_total.loc[ct_total.index.get_level_values(0) == "All",col_mask] = subtable.values.sum()
            else:
                ct_total.loc[ct_total.index.get_level_values(0) == "All",:] = np.nan

            if col_margin_perct and row_margin_perct:
                ct_total.loc[ct_total.index.get_level_values(0) == "All",ct_total.columns.get_level_values(0) == "All"] = ct1.loc[ct_total.index.get_level_values(0) == "All",ct_total.columns.get_level_values(0) == "All"] 

            ct_perc = ct1 / ct_total 
            ct_perc = (100*ct_perc).round(1)

        else:
            ct_perc[:] = np.nan
            ct_total[:] = np.nan

        if report_type == 1:
            report = ct1.fillna("-").astype(str) + " (" + ct_perc.fillna("-").astype(str) + "%)"
            report = report.map(lambda x: x.replace(" (-%)", "") if isinstance(x, str) else x)
        elif report_type == 2:
            report = ct1.fillna("-").astype(str) + "/" + ct_total.map(lambda x: f'{x:.0f}') + " (" + ct_perc.fillna("-").astype(str) + "%)"
            report = report.map(lambda x: x.replace(" (-%)", "") if isinstance(x, str) else x).map(lambda x: x.replace("/nan", "") if isinstance(x, str) else x)
        else:
            report = None

        ct = {"count": ct1, "percent": ct_perc, "report": report, "total": ct_total}
    else:
        ct = {"count": ct1, "percent": None, "report": None, "total": None}

    return ct

def geo_mean_sd_by_group(df, group_by, var):

    def geo_stats(x):
        # Change output from pd.Series to list
        n1 = len(x)
        x = x.replace([np.inf, -np.inf], np.nan)
        x = x.dropna()
        x = x[x > 0]
        if len(x) == 0:
            return [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        logs = np.log(x)
        gm = np.exp(logs.mean())
        gsd = np.exp(logs.std(ddof=1))
        n = len(x)
        se = logs.std(ddof=1) / np.sqrt(n)
        alpha = 0.05
        z = norm.ppf(1 - alpha/2)
        ci_lower = np.exp(logs.mean() - z * se)
        ci_upper = np.exp(logs.mean() + z * se)
        return [gm, gsd, ci_lower, ci_upper, alpha, n1, n]

    result = df.groupby(group_by)[var].apply(geo_stats).apply(pd.Series)
    result.columns = ['Geo_mean', 'Geo_sd_natural', 'CI_lower', 'CI_upper', 'Alpha', 'N_total', 'N_included']
    result = result.reset_index()
    result['N_total'] = result['N_total']
    result['N_included'] = result['N_included']

    return result

if __name__ == "__main__":
    pass