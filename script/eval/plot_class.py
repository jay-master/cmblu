# -*- coding: utf-8 -*-
"""
Created on Wed May 15 20:13:52 2024

@author: Jaehyun
"""

import os

import matplotlib.pyplot as plt
import addcopyfighandler
import pandas as pd
import numpy as np

from func import files2df, fig_ttl, div_seg, dic_subset

class data_init():
    
    def __init__(self, files, seg_subset):
        self.files = files
        self.df_dic, self.file_lst = files2df(self.files)
        self.df_dic_seg, self.seg_lst_all = div_seg(self.df_dic)
        if seg_subset:
            self.df_dic_seg = dic_subset(self.df_dic_seg, seg_subset)
    
class plot_fig():
    
    def __init__(self, file_lst, settings):
        self.settings = settings
        self.file_lst = file_lst
        self.ttl = fig_ttl(self.file_lst, self.settings)
        
    def nyq(self, df_dic_seg):
        ln_lst = []
        fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True)
        ax.set_prop_cycle(self.settings['lines'])
        i = 0 # for file numbering
        for k, v in df_dic_seg.items():
            i += 1
            j = 0 # for segment numbering
            for k1, v1 in v.items():
                j += 1
                ln_name = f'ln_{i}_{j}'
                if self.settings['legends']:
                    ln_name, = ax.plot(v1['Zre (ohms)'], -v1['Zim (ohms)'], label=self.settings['legends'][j-1])
                else:
                    ln_name, = ax.plot(v1['Zre (ohms)'], -v1['Zim (ohms)'], label=f'{k1}')
                ln_lst.append(ln_name)
        fig.suptitle(self.ttl)
        
        ax.set_xlabel('$Z_{re}$ (ohms)', fontsize=self.settings['fonts'][0])
        ax.set_ylabel('$-Z_{im}$ (ohms)', fontsize=self.settings['fonts'][0])
        ax.tick_params(axis='x', labelsize=self.settings['fonts'][1])
        ax.tick_params(axis='y', labelsize=self.settings['fonts'][1])
        ax.legend(handles=ln_lst, fontsize=self.settings['fonts'][2], loc=self.settings['fonts'][3])
        
        if self.settings['grid']:
            ax.grid(color='lightgrey', linestyle='--', linewidth=0.5)
            
        fig.tight_layout()
                
            
        