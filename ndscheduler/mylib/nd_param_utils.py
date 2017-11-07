#-*- coding: utf-8 -*-

import sys
import pandas as pd


def get_project_params():
    project_desc_path = sys.argv[1:][0]
    project_name = sys.argv[1:][1]
    project_df = pd.read_excel(project_desc_path, index_col='project')
    nd_params = project_df.loc[project_name]
    return nd_params
