#!/usr/bin/env python

import os
import json
import pathlib
import datetime

import pandas as pd

from graphreduce.graph_reduce import GraphReduce
from graphreduce.node import DynamicNode, GraphReduceNode
from graphreduce.enum import StorageFormatEnum, ComputeLayerEnum, PeriodUnit
from graphreduce.enum import ComputeLayerEnum, PeriodUnit, StorageFormatEnum, ProviderEnum


data_path = '/'.join(os.path.abspath(__file__).split('/')[0:-1]) + '/data/movie_data'
label_path = '/'.join(os.path.abspath(__file__).split('/')[0:-1]) + '/data/movie_rental_labels.csv'
pk_data = '/'.join(os.path.abspath(__file__).split('/')[0:-1])+'/movie_pks.json'


def prefix(fname):
    if '_' not in fname:
        return fname[0:4]
    else:
        return ''.join([x[0:2] for x in fname.split('_')])


def test_full_transform():
    relations = pd.read_csv(label_path)
    pks = json.loads(open(pk_data,'r').read())
    
    gr_nodes = {}
    for f in pathlib.Path(data_path).iterdir():
        if f.is_file():
            fname = f.name
            pre = prefix(fname)
            try:
                gr_nodes[fname] = DynamicNode(
                    fpath=f.as_posix(),
                    date_key=None,
                    pk=pks[fname],
                    fmt='csv',
                    prefix=pre,
                    compute_layer=ComputeLayerEnum.pandas
                    )
            except Exception as e:
                continue
    gr = GraphReduce(
            name='kurve_demo',
            parent_node=gr_nodes['inventory.csv'],
            fmt='csv',
            compute_layer=ComputeLayerEnum.pandas,
            #cut_date=cut_date,
            auto_features=True,
            auto_feature_hops_front=1,
            auto_feature_hops_back=2,
            debug=True
            )
    for ix, row in relations.iterrows():
        try:
            gr.add_entity_edge(
                parent_node=gr_nodes[row['to_name']],
                relation_node=gr_nodes[row['from_name']],
                parent_key=row['to_key'],
                relation_key=row['from_key'],
                reduce=True
                )
        except Exception as e:
            continue

    gr.plot_graph('movie_graph.html')
    #print(gr.traverse_up(start=gr.parent_node))

    gr.do_transformations()
    print(gr.parent_node.df.head())
    print(f'featue matrix shape: {gr.parent_node.df.shape}')
    print(gr.parent_node.df.columns)
    print(list(set(gr.parent_node.df.columns)))



def prep_graph():
    relations = pd.read_csv(label_path)
    pks = json.loads(open(pk_data,'r').read())
    
    gr_nodes = {}
    for f in pathlib.Path(data_path).iterdir():
        if f.is_file():
            fname = f.name
            pre = prefix(fname)
            try:
                gr_nodes[fname] = DynamicNode(
                    fpath=f.as_posix(),
                    date_key=None,
                    pk=pks[fname],
                    fmt='csv',
                    prefix=pre,
                    compute_layer=ComputeLayerEnum.pandas
                    )
            except Exception as e:
                continue
    gr = GraphReduce(
            name='kurve_demo',
            parent_node=gr_nodes['inventory.csv'],
            fmt='csv',
            compute_layer=ComputeLayerEnum.pandas,
            #cut_date=cut_date,
            auto_features=True,
            auto_feature_hops_front=2,
            auto_feature_hops_back=1,
            debug=True
            )
    for ix, row in relations.iterrows():
        try:
            gr.add_entity_edge(
                parent_node=gr_nodes[row['to_name']],
                relation_node=gr_nodes[row['from_name']],
                parent_key=row['to_key'],
                relation_key=row['from_key'],
                reduce=True
                )
        except Exception as e:
            continue

    return gr
