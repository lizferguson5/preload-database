#!/usr/bin/env python
import json
import os
import gdata.spreadsheet.service as service
import pandas as pd
import config

CSV_OVERWRITE_WARNING = '\n\nThis will overwrite the Resource Data csv\n' \
                        'files with the data from the RTN Preloaded\n' \
                        'Resources Google Sheet.\n\n' +\
                        'Do you want to continue [y|n]? > '

key = config.SPREADSHEET_KEY

SHEET_COLUMNS = {
    'ParameterDefs':
        ['scenario', 'confluence', 'name', 'id', 'hid', 'hidconflict',
         'parametertype', 'dimensions', 'valueencoding', 'codeset',
         'unitofmeasure', 'fillvalue', 'displayname', 'precision', 'visible',
         'parameterfunctionid', 'parameterfunctionmap', 'lookupvalue',
         'qcfunctions', 'standardname', 'dataproductidentifier',
         'referenceurls', 'description', 'reviewstatus', 'reviewcomment',
         'longname', 'skip', 'dataproducttype', 'datalevel'],
    'ParameterFunctions':
        ['scenario', 'id', 'hid', 'name', 'instrumentclass',
         'instrumentseries', 'functiontype', 'function', 'owner', 'args',
         'kwargs', 'description', 'reference', 'skip', 'qcflag'],
    'ParameterDictionary':
        ['scenario', 'id', 'confluence', 'name', 'parameterids',
         'temporalparameter', 'streamdependency', 'streamtype',
         'streamcontent', 'reviewstatus'],
    'BinSizes':
        ['stream', 'binsize', 'estimatedrate', 'measuredrate', 'binsizeindays',
         'particlesperbin', 'estimatedvsingested', 'dataratenotes'],
}


def sheet_generator(name):
    rows = []

    print 'fetching from google'
    client = service.SpreadsheetsService()
    for sheet in client.GetWorksheetsFeed(key, visibility='public',
                                          projection='basic').entry:
        title = sheet.title.text
        rowid = sheet.id.text.split('/')[-1]

        if title == name:
            for x in client.GetListFeed(key, rowid, visibility='public',
                                        projection='values').entry:
                d = {}
                for k, v in x.custom.items():
                    if v.text is not None:
                        d[k] = v.text.strip()
                    else:
                        d[k] = None

                rows.append(d)
                yield d


def create_csv_files():
    for sheet in SHEET_COLUMNS:
        df = pd.DataFrame(list(sheet_generator(sheet)),
                          columns=SHEET_COLUMNS[sheet])
        df.to_csv(os.path.join('csv', '%s.csv' % sheet),
                  encoding='utf-8', index=False)


if __name__ == '__main__':
    resp = ''
    while resp not in ['y', 'n']:
        resp = raw_input(CSV_OVERWRITE_WARNING)

    if resp == 'y':
        create_csv_files()
