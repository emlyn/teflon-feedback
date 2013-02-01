from gzip import GzipFile
from random import random
import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

def ln2(x):
    from math import log
    return log(x, 2)

def zopen(fname, *args, **kwargs):
    if fname.endswith('.gz'):
        return GzipFile(fname, *args, **kwargs)
    else:
        return open(fname, *args, **kwargs)

def load(fname):
    with zopen(fname) as pickler:
        return pickle.load(pickler)

def plot_viewshisto(feedback, queries, ax):
    viewstrue = [d['views'] for d in feedback
                 if d.has_key('views') and d['relevant'] == 'true']
    viewsfalse = [d['views'] for d in feedback
                  if d.has_key('views') and d['relevant'] == 'false']
    viewsclick = [d['views'] for d in feedback
                  if d.has_key('views') and d['relevant'] == '']
    viewsall = [d['views'] for d in queries]
    ax.hist(viewsall, 40, range=(0,1000), normed=1, alpha=0.5,
            facecolor='yellow', label='Queries')
    ax.hist(viewstrue,  40, range=(0,1000), normed=1, alpha=0.5,
            facecolor='blue', label='Up')
    ax.hist(viewsfalse, 40, range=(0,1000), normed=1, alpha=0.5,
            facecolor='red', label='Down')
    ax.hist(viewsclick, 40, range=(0,1000), normed=1, alpha=0.5,
            facecolor='green', label='Click')
    ax.set_xlabel('Page Views')
    ax.set_ylabel('Frequency')
    #ax.set_title(r'$\mathrm{Foo}$')
    #ax.set_xlim(40, 160)
    ax.set_ylim(0, 0.01)
    ax.legend()
    ax.grid(True)

def plot_scatter(feedback, queries, ax):
    ax.plot([ln2(d['views'] + random() - 0.5) for d in queries],
            [d['score'] for d in queries],
            'o', mfc='#eeee00', mec='yellow', alpha=0.1, markersize=3, label='Queries')
    ax.plot([ln2(d['views'] + random() - 0.5) for d in feedback
             if d.has_key('views') and d['relevant'] == ''],
            [d['score'] for d in feedback
             if d.has_key('views') and d['relevant'] == ''],
            'o', mfc='#00dd00', label='Click')
    ax.plot([ln2(d['views'] + random() - 0.5) for d in feedback
             if d.has_key('views') and d['relevant'] == 'true'],
            [d['score'] for d in feedback
             if d.has_key('views') and d['relevant'] == 'true'],
            'bo', label='Up')
    ax.plot([ln2(d['views'] + random() - 0.5) for d in feedback
             if d.has_key('views') and d['relevant'] == 'false'],
            [d['score'] for d in feedback
             if d.has_key('views') and d['relevant'] == 'false'],
            'ro', label='Down')
    ax.set_xlim(0, 10)
    ax.set_ylim(-1, 5)
    ax.set_xlabel('Log$_2$(Page Views)')
    ax.set_ylabel('Score')
    #ax.set_title(r'Bar')
    ax.legend()
    ax.grid(True)

def main():
    feedback = load('data/teflon-feedback.dat.gz')
    queries = load('data/teflon-queries.dat.gz')

    plot_viewshisto(feedback, queries, plt.subplot(121))
    plot_scatter(feedback, queries, plt.subplot(122))

    plt.show()

if __name__ == '__main__':
    main()
