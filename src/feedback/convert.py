import cPickle as pickle

def convert_titles(fin, fout):
    with open(fin) as f, open(fout, 'w') as g:
        for l in f:
            if not l.startswith('INSERT INTO '):
                continue
            cl = 0
            titles = l[l.find('(')+1:l.rfind(')')].split('),(')
            for t in titles:
                id,namespace,title = t.split(',')[:3]
                if namespace == '0':
                    g.write(id + '\t' + title[1:-1] + '\n')
convert_titles('../enwiki-20130102-page.sql', '../titles.txt')

def convert_counts(fin, fout):
    with open(fin) as f, open(fout, 'w') as g:
        for l in f:
            if not l.startswith('en '):
                continue
            title,count = l.split(' ')[1:3]
            g.write(title + '\t' + count + '\n')
convert_counts('../pagecounts-20130101-190000', '../pagecounts.txt')

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
combine('../titles.txt', '../pagecounts.txt', '../idcounts.txt')

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
dopickle('../results.txt', '../idcounts.txt', '../data.dat')
