import yaml
import csv
import logging
import os
import matplotlib.pyplot as plt

#- rsrp
#- sinr
#- rsrq
#- thp
#- tx_pwr
#- BLER
#- spectral efficiency (b/s/Hz)
#
#datasets:
#    1.5DL:
#        paths: ['dna/*', 'elisa/*', 'telia/*']
#        fields: ['rsrp', 'rssi', 'rsrq', 'pdsch thp', 'bler']
#        test: 'HTTP DL'
#        altitude: 1.5
#
#    15DL:
#        paths: ['dna/*', 'elisa/*', 'telia/*']
#        fields: ['rsrp', 'rssi', 'rsrq', 'pdsch thp', 'bler']
#        test: 'HTTP DL'
#        altitude: 15
#
#    15UL:
#        paths: ['dna/*', 'elisa/*', 'telia/*']
#        fields: ['rsrp', 'rssi', 'rsrq', 'pusch thp', 'bler', 'tx pwr']
#        test: 'HTTP UL'
#        altitude: 15
#
#graphs:
#    RSRP_UL:
#        datasets: ['1.5UL', '15UL', '30UL', '45UL']
#        legends: ['1.5m', '15m', '30m', '45m']
#        key: 'rsrp'
#        y-label: 'RSRP [dBm]'
#        type: cdf|hist|pdf|???
#        size: (x, y)
#        preview: True
#        outdir: './../joku-kansio'
#
#    RSSI_DL:
#        datasets: ['1.5DL', '15DL', '30DL', '45m']
#        legends: ['1.5m', '15m', '30m', '45m']
#        key: 'RSSI'
#        y-label: 'RSSI [dB]'
#        type: cdf|hist|pdf|???
#        size: (x, y)
#        preview: True
#        outdir: './../joku-kansio'

#struct metadata():
#    some_data: some value
#
#wordbook = {
#    full: abbr,
#    full2: abbr2
#}
#
#def cdf(data, metadata):
#    pass
#
#def pdf(data, metadata):
#    pass
#
#def hist(data, metadata):
#    pass
#
#def derive_metric(item, from):
#    switch (item):
#    case spectral_eff:
#        return smthing
#    case smthing:
#        return smthing else
#    etc...

def parse_datasets(datasets) -> dict:
    # TODO: Un-hardcode this
    altitude_accuracy = 2.5

    file_data = {}
    r_datasets = {}
    for id, dataset in datasets.items():
        for path in dataset['paths']:
            if path not in file_data:
                file_data[path] = {}
            file_data[path][id] = {}
    
    for filename in file_data:
        takeoff_altitude = None
        with open(filename, 'r') as file:
            headers = file.readline().replace('\u200b', '')
            #file.seek(0)
             
            reader = csv.DictReader(file, fieldnames=headers.split(','), delimiter=',')
            for row in reader:
                if row['Altitude'] == None or row['Altitude'] == '':
                    continue
                elif takeoff_altitude == None:
                    takeoff_altitude = float(row['Altitude'])

                otg_altitude = float(row['Altitude']) - takeoff_altitude
                for dataset in file_data[filename]:
                    #flight_level = float(datasets[dataset]['altitude'])
                    flight_level = 0

                    if datasets[dataset]['test'].upper() != row['Last started test\n'].upper() \
                    or row['Data technology'] != 'LTE-5GNR' \
                    or otg_altitude < flight_level-altitude_accuracy \
                    or otg_altitude > flight_level+altitude_accuracy \
                    : continue

                    for field in datasets[dataset]['fields']:
                        if field not in file_data[filename][dataset]:
                            file_data[filename][dataset][field] = [row[field]]
                        else:
                            file_data[filename][dataset][field].append(row[field])

    for dataset, data in datasets.items():
        if dataset not in r_datasets: r_datasets[dataset] = {}
        for filename in data['paths']:
            for field in data['fields']:
                r_datasets[dataset][field] = file_data[filename][dataset][field]

    return r_datasets

def cdf(datasets, params):
    fig, ax = plt.subplots(figsize=(8, 4))
    
    for i, dataset in enumerate(params['datasets']):
        #ax = plt.subplot(2, 2, i+1)
        x_data = datasets[dataset][params['key']]
        ax.hist(x_data, len(x_data), density=True, histtype='step', cumulative=True, label=params['legends'][i])
    ax.legend(loc='right')
    ax.set_title(params['title'])
    ax.set_xlabel(params['x-label'])
    ax.set_ylabel('Probability')
    return ax

def parse(file, preview_flag):
    logger = logging.getLogger(__name__)
    with open(file, 'r') as f:
        config = yaml.load(f, yaml.SafeLoader)

    datasets = parse_datasets(config['datasets'])

    #from pprint import pprint
    #pprint(datasets, compact=True)
    #exit()

    for title, params in config['graphs'].items():
        for dataset in params['datasets']:
            if dataset not in datasets:
                logger.error(f'Dataset \'{dataset}\' in graph \'{title}\' not configured. Omitting...')
                continue

        if params['type'].upper() == 'CDF':
            graph = cdf(datasets, params)
        elif params['type'].upper() == 'PDF':
            pass
        elif params['type'].upper() == 'HISTOGRAM':
            pass
        else:
            pass
            # TODO: Error msg

        if preview_flag:
            plt.show()
        else:
            plt.savefig(os.path.join(params['outdir'], title+'.png'))

