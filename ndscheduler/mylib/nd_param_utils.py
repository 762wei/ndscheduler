#-*- coding: utf-8 -*-

import sys
import pandas as pd
import json


def get_project_params():
    project_desc_path = sys.argv[1:][0]
    project_name = sys.argv[1:][1]
    project_df = pd.read_excel(project_desc_path, index_col='project')
    nd_params = project_df.loc[project_name]
    return nd_params

# 把控制台的传入的占位符为“\”的格式的字符串该为json格式的字符串，并转成dic格式
def convert_cmdstr_2_dic(cmd_param_str):
    param_dic = {}
    try:
        tmp = cmd_param_str.replace('\\','"')
        param_dic = json.loads(tmp)
    except Exception as e:
        print e
    return param_dic

