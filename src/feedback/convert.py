from gzip import GzipFile
import argparse
import cPickle as pickle

def zopen(fname, *args, **kwargs):
    if fname.endswith('.gz'):
        return GzipFile(fname, *args, **kwargs)
    else:
        return open(fname, *args, **kwargs)

def convert_titles(fin, fout):
    """Converts enwiki-*-page.sql.gz files downloaded from
    http://dumps.wikimedia.org/enwiki/"""
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

def convert_counts(fins, fout):
    """Converts Wikipedia pagecount files downloaded from
    http://dumps.wikimedia.org/other/pagecounts-raw/"""
    if isinstance(fins, basestring):
        fins = [fins]
    with zopen(fout, 'w') as g:
        for fin in fins:
            print "Converting", fin
            with zopen(fin) as f:
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
            id = int(id)
            try:
                c,t = result[id]
                count += c
                if title != t:
                    print "*** Title changed:", t, "->", title
                result[id] = (count, title)
            except KeyError:
                result[id] = (count, title)
        return result

def load(fname, fcounts):
    badids = set()
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
            except:
                continue
            d = item['document']
            if d.startswith('wikipedia:'):
                try:
                    id = int(d.split(':')[1])
                    count,title = counts[id]
                    item['views'] = int(count)
                    tt = item['title'].replace(' ', '_')
                    if tt != title:
                        print "***", item['title'], ':', tt, "!=", title
                except ValueError:
                    print '### Bad id', d
                    continue
                except KeyError:
                    if id not in badids:
                        badids.add(id)
                        print '### No id', id, ':', item['title']
                    continue
                data.append(item)
        print "Loaded", len(data), "of", ','.join(header)
        return data

def dopickle(data, fpickle):
    with zopen(fpickle, 'w') as pickler:
        pickle.dump(data, pickler)

def main(titles=None, counts=None, feedback=None, queries=None):
    if titles != None:
        print 'Converting titles (%s)' % titles
        convert_titles(titles, 'data/titles.csv.gz')
    if counts != None:
        print 'Converting counts'
        convert_counts(counts, 'data/pagecounts.csv.gz')
    if titles != None or counts != None:
        print 'Combining titles with counts'
        combine('data/titles.csv.gz',
                'data/pagecounts.csv.gz',
                'data/idcounts.csv.gz')
    if feedback != None:
        print 'Combining with teflon feedback (%s)' % feedback
        data = load(feedback,
                    'data/idcounts.csv.gz')
        dopickle(data, 'data/teflon-feedback.dat.gz')
    if queries != None:
        print 'Combining with teflon queries (%s)' % queries
        data = load(queries,
                    'data/idcounts.csv.gz')
        dopickle(data, 'data/teflon-queries.dat.gz')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Convert Wikipedia pageview dumps and combine with teflon feedback")
    parser.add_argument('--titles',   '-t', dest='titles',   nargs='?', type=str, default=None)
    parser.add_argument('--counts',   '-c', dest='counts',   nargs='+', type=str, default=None)
    parser.add_argument('--feedback', '-f', dest='feedback', nargs='?', type=str, default=None)
    parser.add_argument('--queries',  '-q', dest='queries',  nargs='?', type=str, default=None)
    args = parser.parse_args()
    main(**vars(args))
