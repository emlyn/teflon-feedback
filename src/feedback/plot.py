import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab


def unpickle(fname):
    with open(fname) as pickler:
        return pickle.load(pickler)

def plot_rankshisto(data, fig):
    rankstrue = [int(d['rank']) for d in data
                 if d.has_key('rank') and d['relevant'] == 'true']
    ranksfalse = [int(d['rank']) for d in data
                  if d.has_key('rank') and d['relevant'] == 'false']
    ranksclick = [int(d['rank']) for d in data
                  if d.has_key('rank') and d['relevant'] == '']

    ax = fig.add_subplot(111)

    ax.hist(rankstrue,  40, range=(0,1000), normed=1, alpha=0.5, facecolor='red')
    ax.hist(ranksfalse, 40, range=(0,1000), normed=1, alpha=0.5, facecolor='green')
    ax.hist(ranksclick, 40, range=(0,1000), normed=1, alpha=0.5, facecolor='blue')

    ax.set_xlabel('Rank')
    ax.set_ylabel('Frequency')
    #ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
    #ax.set_xlim(40, 160)
    ax.set_ylim(0, 0.01)
    ax.grid(True)

    plt.show()

def plot_scatter(data, fig):
    ax = fig.add_subplot(111)
    ax.plot([d['rank'] for d in data if d.has_key('rank') and d['relevant'] == 'true'],
            [d['score'] for d in data if d.has_key('rank') and d['relevant'] == 'true'],
            'ro',
            [d['rank'] for d in data if d.has_key('rank') and d['relevant'] == 'false'],
            [d['score'] for d in data if d.has_key('rank') and d['relevant'] == 'false'],
            'go',
            [d['rank'] for d in data if d.has_key('rank') and d['relevant'] == ''],
            [d['score'] for d in data if d.has_key('rank') and d['relevant'] == ''],
            'bo')
    plt.show()

data = unpickle('../data.dat')
fig = plt.figure()
plot_rankshisto(data, fig)
plot_scatter(data, fig)
