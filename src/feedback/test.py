import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

def convert_titles(fin, fout):
    with open(fin) as f, open(fout, 'w') as g:
        for l in f:
            if not l.startswith('INSERT INTO '):
                continue
            cl = 0
            titles = l[l.find('(')+1:-2].split('),(')
            for t in titles:
                parts = t.split(',', 3)
                if parts[1] == '0':
                    g.write(parts[0] + '\t' + parts[2][1:-1] + '\n')
#convert_titles('../enwiki-20130102-page.sql', '../titles.txt')

def convert_counts(fin, fout):
    with open(fin) as f, open(fout, 'w') as g:
        for l in f:
            if not l.startswith('en '):
                continue
            parts = l.split(' ')
            g.write(parts[1] + '\t' + parts[2] + '\n')
#convert_counts('../pagecounts-20130101-190000', '../pagecounts.txt')

def combine(ftitles, fcounts, fout):
    counts = {}
    with open(fcounts) as f:
        for l in f:
            title,count = l.rstrip('\n').split('\t')
            counts[title] = count
    with open(ftitles) as f, open(fout, 'w') as g:
        for l in f:
            id,title = l.rstrip('\n').split('\t')
            try:
                count = counts[title]
            except KeyError:
                continue
            g.write(id + '\t' + count + '\t' + title + '\n')
#combine('../titles.txt', '../pagecounts.txt', '../idcounts.txt')

def load_counts(fname):
    with open(fname) as f:
        result = {}
        for l in f:
            id,count,title = l.rstrip('\n').split('\t')
            result[int(id)] = [count, title]
        return result

def load(fname, fcounts):
    counts = load_counts(fcounts)
    with open(fname) as f:
        header = f.readline().rstrip('\n').split('\t')
        data = []
        for l in f:
            vals = l.rstrip('\n').split('\t')
            item = {k:v for k,v in zip(header, vals)}
            d = item['document']
            if d.startswith('wikipedia:'):
                try:
                    id = int(d.split(':')[1])
                    count,title = counts[id]
                    item['rank'] = count
                    tt = item['title'].replace(' ', '_')
                    if tt != title:
                        print "***", item['title'], ':', tt, "!=", title
                except ValueError:
                    print '### Bad id', d
                except KeyError:
                    print '### No id', id, ':', item['title']
            data.append(item)
        print "Loaded", len(data), "of", ','.join(header)
        return data

def dopickle(fname, fcounts, fpickle):
    data = load(fname, fcounts)
    with open(fpickle, 'w') as pickler:
        pickle.dump(data, pickler)
#dopickle('results.txt', '../idcounts.txt', 'data.dat')

with open('data.dat') as pickler:
   data = pickle.load(pickler)

rankstrue = [int(d['rank']) for d in data if d.has_key('rank') and d['relevant'] == 'true']
ranksfalse = [int(d['rank']) for d in data if d.has_key('rank') and d['relevant'] == 'false']
ranksclick = [int(d['rank']) for d in data if d.has_key('rank') and d['relevant'] == '']
#mu, sigma = 100, 15
#x = mu + sigma * np.random.randn(10000)
#print rankstrue

fig = plt.figure()
ax = fig.add_subplot(111)

# the histogram of the data
#n, bins, patches = ax.hist(x, 50, normed=1, facecolor='green', alpha=0.75)

ax.hist(rankstrue,  40, range=(0,1000), normed=1, alpha=0.5, facecolor='red')
ax.hist(ranksfalse, 40, range=(0,1000), normed=1, alpha=0.5, facecolor='green')
ax.hist(ranksclick, 40, range=(0,1000), normed=1, alpha=0.5, facecolor='blue')

# hist uses np.histogram under the hood to create 'n' and 'bins'.
# np.histogram returns the bin edges, so there will be 50 probability
# density values in n, 51 bin edges in bins and 50 patches.  To get
# everything lined up, we'll compute the bin centers
#bincenters = 0.5*(bins[1:]+bins[:-1])
# add a 'best fit' line for the normal PDF
#y = mlab.normpdf( bincenters, mu, sigma)
#l = ax.plot(bincenters, y, 'r--', linewidth=1)

ax.set_xlabel('Rank')
ax.set_ylabel('Frequency')
#ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
#ax.set_xlim(40, 160)
ax.set_ylim(0, 0.01)
ax.grid(True)

plt.show()
