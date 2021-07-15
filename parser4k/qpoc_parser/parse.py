import yaml
yaml.load = yaml.safe_load

"""
- rsrp
- sinr
- rsrq
- thp
- tx_pwr
- BLER
- spectral efficiency (b/s/Hz)

1.5m:
    paths: ['dna/*', 'elisa/*', 'telia/*']
    data: ['rsrp', 'rssi', 'rsrq', 'pdsch thp', 'pusch thp', 'bler', 'tx pwr', 'spectral eff']
    alt: 1.5

15m:
    paths: ['dna/*', 'elisa/*', 'telia/*']
    data: ['rsrp', 'rssi', 'rsrq', 'pdsch thp', 'pusch thp', 'bler', 'tx pwr', 'spectral eff']
    alt: 15

graphs:
    graph_id1:
        data-set: ['some-set', 'some-other-set', 'another-set']
        legends: ['some-legend', 'some-other-legend', 'another-legend']
        key: 'rsrp'
        title: 'RSRP'
        y-label: 'RSRP [dBm)'
        graph-type: cdf|hist|pdf|???
        size: (x, y)
        preview: True
        outdir: './../joku-kansio'

    graph_id2:
        data-set: ['1.5m', '15m', '25m', '35m', '45m']
        legends: ['1.5m', '15m', '25m', '35m', '45m']
        key: 'RSSI'
        title: 'paskagraafi'
        y-label: 'RSSI [dB]'
        graph-type: cdf|hist|pdf|???
        size: (x, y)
        preview: True
        outdir: './../joku-kansio'
"""

"""
struct metadata():
    some_data: some value

wordbook = {
    full: abbr,
    full2: abbr2
}

def cdf(data, metadata):
    pass

def pdf(data, metadata):
    pass

def hist(data, metadata):
    pass

def derive_metric(item, from):
    switch (item):
    case spectral_eff:
        return smthing
    case smthing:
        return smthing else
    etc...

def concat_files(files):
    for row in each files:
        if altitude = empty; then skip row
        groundLevel := first non-empty altitude
        if (altitude - groundLevel < altitudeTgt); then skip row
        else; for each item in data:
            item_key = wordbook[item]
            if item in derived_types; id['data'].append(derive_metric(item_key, row))
            elif row[item] != empty; then id['data'].append(row[item_key])
            else skip

"""

def parse(files):
    pass

    """
    'main' function:
    parses files into data sets
        - concatenates the files given in name:path
    """

    """
    for graph_id in graphs:
        for data-set in data-sets:
            if not exists(sets[data-set]):
                sets[data-set] = concat_files(data-set.paths)

        switch(graph-type):
            case CDF:
                graph = cdf(data, metadata)
                if graph_id.preview:
                    show(graph)
                with open os.path.join(graph_id.outdir, graph_id) as f:
                    f.write(graph)
    """    
