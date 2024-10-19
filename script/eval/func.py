# -*- coding: utf-8 -*-
"""
Created on Thu May 16 10:12:45 2024

@author: Jaehyun
"""

import os
import pandas as pd

def read_data(path, names=None, usecols=None):
    _df = pd.read_csv(path)
    if _df.keys()[1] == 'Test_ID':
        df = _df
    else:
        df = pd.read_csv(path, names=names, usecols=usecols)
    if usecols:
        df = df[usecols]

    return df


def fig_ttl(file_lst, settings):
    # set title
    if settings['title']:
        ttl = settings['title']
    else:
        ttl = ''
        for i in range(len(file_lst)):
            ttl += file_lst[i] + '\n'
    
    return ttl


def files2df(files):
    df_dic = {}
    
    for i, v in enumerate(files):
        df = pd.read_csv(v)
        file_name = os.path.split(v)[1]
        df_dic[file_name] = df
        
    file_lst = list(df_dic.keys())
        
    return df_dic, file_lst


def div_seg(df_dic):
    df_dic = df_dic.copy()
    seg_lst_all = []
    for k, v in df_dic.items():
        new_v = {}
        # list consists of unique values in Segment column
        seg_lst = v['Segment'].unique().tolist()
        seg_lst_all.append(seg_lst)
        for i in range(len(seg_lst)):
            seg_no = seg_lst[i]
            seg_name = f'Segment {seg_no}'
            new_v[seg_name] = v[v['Segment'] == seg_no]
        df_dic[k] = new_v
    
    return df_dic, seg_lst_all
    

def dic_subset(df_dic_seg, seg_subset):
    df_dic_seg = df_dic_seg.copy()
    for k, v in df_dic_seg.items():
        v_sub = {key: v[key] for key in seg_subset if key in v}
        df_dic_seg[k] = v_sub
        
    return df_dic_seg
    