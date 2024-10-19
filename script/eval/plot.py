# -*- coding: utf-8 -*-
"""
Created on Wed May 15 20:13:20 2024

@author: Jaehyun

[Setting Guide]

1. title
    (1) False: file names will be title
    (2) [title, font]: ex) [f'title', None] or [f'title', 30]

2. line_cycler (default)
    (cycler(lw=[1, 1, 1, 1]) +
     cycler(linestyle=['-', '--', ':', '-.']) +
     cycler(color=['r', 'g', 'b', 'y']))
    
2. fonts
    (1) [axis_label, axis_ticks, legends, lgd_loc]: ex) [None, None, None, None] or [35, 32, 32, 'best']
    (2) legend location examples: 'upper left', 'upper right', 'lower left', 'lower right', 'upper center', 'lower center', 'center left', 'center right', 'center', 'best'
    (3) default fonts:
        (a) for log:                  [None, None, None, None]
        (b) for journal (2 columns):  [25, 22, 22, None]
        (c) for journal (1 column):   [25, 22, 22, None]

3. grid
    boolean: True or False

4. step_idx: to plot certain steps
    (1) False: entire data will be plotted
    (2) [step_idx_data1, step_idx_data2, ..]: ex) [1, 2, ..]
    
5. legends
    (1) False: legends will be given as default (Cell 1, Cell 2, ...)
    (2) [legend1, legend2, ...]: ex) ['25 \u2103', '10 \u2103']
"""


#%% read data
from tkinter.filedialog import askopenfilenames
from plot_class import data_init, plot_fig
from cycler import cycler

# line cycler settings
line_cycler = (cycler(lw=[1, 1, 1, 1, 1]) +
               cycler(linestyle=['-', '--', ':', '-.', (5, (10, 3))]) + # linestyle=['-', '--', ':', '-.']
               cycler(color=['r', 'g', 'b', 'y', 'c']))

# call data
files = askopenfilenames()
# seg_subset = ['Segment 0', 'Segment 2', 'Segment 4' , 'Segment 6', 'Segment 8']
# seg_subset = ['Segment 10', 'Segment 12', 'Segment 14' , 'Segment 16', 'Segment 18']
# seg_subset = ['Segment 20', 'Segment 22', 'Segment 24' , 'Segment 26', 'Segment 28']
# seg_subset = ['Segment 30', 'Segment 32', 'Segment 34' , 'Segment 36']
df_dic_seg = data_init(files, seg_subset).df_dic_seg
file_lst = data_init(files, seg_subset).file_lst
seg_lst_all = data_init(files, seg_subset).seg_lst_all

#%% plot_log
settings_log = {'title':False,
            'lines':line_cycler,
            'fonts':[None, None, None, None],
            'grid':True,
            'legends':False} # ['25 \u2103', '10 \u2103']

# init: class to object
p_log = plot_fig(file_lst, settings_log)

p_log.nyq(df_dic_seg)

