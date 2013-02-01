from gzip import GzipFile
import cPickle as pickle

def zopen(fname, *args, **kwargs):
    if fname.endswith('.gz'):
        return GzipFile(fname, *args, **kwargs)
    else:
        return open(fname, *args, **kwargs)

def convert_titles(fin, fout):
    with zopen(fin) as f, zopen(fout, 'w') as g:
        for l in f:
            if not l.startswith('INSERT INTO '):
                continue
            cl = 0
            titles = l[l.find('(')+1:l.rfind(')')].split('),(')
            for t in titles:
                id,namespace,title = t.split(',')[:3]
                if namespace == '0':
                    g.write(id + '\t' + title[1:-1] + '\n')

def convert_counts(fin, fout):
    with zopen(fin) as f, zopen(fout, 'w') as g:
        for l in f:
            if not l.startswith('en '):
                continue
            title,count = l.split(' ')[1:3]
            g.write(title + '\t' + count + '\n')

def combine(ftitles, fcounts, fout):
    counts = {}
    with zopen(fcounts) as f:
        for l in f:
            title,count = l.rstrip('\n').split('\t')
            counts[title] = count
    with zopen(ftitles) as f, zopen(fout, 'w') as g:
        for l in f:
            id,title = l.rstrip('\n').split('\t')
            try:
                count = counts[title]
            except KeyError:
                continue
            g.write(id + '\t' + count + '\t' + title + '\n')

def load_counts(fname):
    with zopen(fname) as f:
        result = {}
        for l in f:
            id,count,title = l.rstrip('\n').split('\t')
            result[int(id)] = [count, title]
        return result

def load(fname, fcounts):
    counts = load_counts(fcounts)
    with zopen(fname) as f:
        header = f.readline().rstrip('\n').split('\t')
        data = []
        for l in f:
            vals = l.rstrip('\n').split('\t')
            item = {k:v for k,v in zip(header, vals)}
            try:
                n = int(item['pos'])
                item['pos'] = n
            except KeyError:
                pass
            try:
                n = int(item['timestamp'])
                item['timestamp'] = n
            except KeyError:
                pass
            try:
                n = float(item['score'])
                item['score'] = n
            except KeyError:
                pass
            except ValueError:
                item['score'] = None
            d = item['document']
            if d.startswith('wikipedia:'):
                try:
                    id = int(d.split(':')[1])
                    count,title = counts[id]
                    item['rank'] = int(count)
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

def dopickle(data, fpickle):
    with zopen(fpickle, 'w') as pickler:
        pickle.dump(data, pickler)

def main():
    print 'Converting titles'
    convert_titles('data/enwiki-20130102-page.sql.gz',
                   'data/titles.csv.gz')
    print 'Converting counts'
    convert_counts('data/pagecounts-20130131-150000.gz',
                   'data/pagecounts.csv.gz')
    print 'Combining titles with counts'
    combine('data/titles.csv.gz',
            'data/pagecounts.csv.gz',
            'data/idcounts.csv.gz')
    print 'Combining with teflon feedback'
    data = load('data/teflon-feedback.csv',
                'data/idcounts.csv.gz')
    dopickle(data, 'data/teflon-feedback.dat.gz')
    print 'Combining with teflon queries'
    data = load('data/teflon-queries.csv',
                'data/idcounts.csv.gz')
    dopickle(data, 'data/teflon-queries.dat.gz')

if __name__ == '__main__':
    main()
