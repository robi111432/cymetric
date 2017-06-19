import warnings

import pandas as pd
import numpy as np

try:
    from graphviz import Digraph
    HAVE_GRAPHVIZ = True
except ImportError:
    HAVE_GRAPHVIZ = False

try:
    from pyne import data
    import pyne.enrichment as enr
    from pyne import nucname
    HAVE_PYNE = True
except ImportError:
    HAVE_PYNE = False

from cymetric import tools
from cymetric.filter import get_transaction_nuc_df


def flow_graph(evaler, senders=(), receivers=(), commodities=(), nucs=(),
               start=None, stop=None):
    """
    Generate the dot graph of the transation between facilitiese. Applying times
    nuclides selection when required.

    Parameters
    ----------
    evaler : evaler
    senders : list of the sending facility to consider
    receivers : list of the receiving facility to consider
    commodities : list of the commodity exchanged to consider
    nucs : list of nuclide to consider
    start : first timestep to consider, start included
    stop : last timestep to consider, stop included
    """
    tools.raise_no_graphviz('Unable to generate flow graph!', HAVE_GRAPHVIZ)

    df = get_transaction_nuc_df(
        evaler, senders, receivers, commodities, nucs)

    if start != None:
        df = df.loc[(df['Time'] >= time[0])]
    if stop != None:
        df = df.loc[(df['Time'] <= time[1])]

    group_end = ['ReceiverPrototype', 'SenderPrototype']
    group_start = group_end + ['Mass']
    df = df[group_start].groupby(group_end).sum()
    df.reset_index(inplace=True)

    agents_ = evaler.eval('AgentEntry')['Prototype'].tolist()

    dot = Digraph('G')

    for agent in agents_:
        dot.node(agent)

    for index, row in df.iterrows():
        dot.edge(row['SenderPrototype'], row['ReceiverPrototype'],
                 label=str(row['Mass']))

    return dot