import glob
import re
import requests
import sqlite3
import tempfile
import zipfile


def download(date):
    """Download an extract zips from http://data.charitycommission.gov.uk/."""
    base_url = 'http://apps.charitycommission.gov.uk/data/' + \
        date.strftime('%Y%m') + '/extract1/'

    urls = [
        'TableBuildScripts.zip',
        'RegPlusExtract_' + date.strftime('%B_%Y') + '.zip'
    ]

    for url in urls:
        url = base_url + url
        print('Downloading ' + url)
        temp = tempfile.TemporaryFile()
        res = requests.get(url)
        temp.write(res.content)
        with zipfile.ZipFile(temp) as zip_file:
            zip_file.extractall('data/in')
    print('Done')

# Maybe there is a library out there than can convert from the 
# supplied TableBuildScripts.zip. In the mean time:

def _translate_col_type(type):
    type_re = re.match('\[(.+?)\]', type)
    base_type = type_re.group(1)
    if base_type == 'int':
        return 'integer'
    elif base_type == 'numeric':
        return 'real'
    else:
        return 'text'

# TableBuildScripts.zip are light on index information (not sure
# why) hence we presume that the following should be indexed.

indexed_cols = ['aookey', 'aootype', 'aootypeclassno', 'arno', 'artype', 'class',
                'code', 'fyend', 'nameno', 'regdate', 'regno', 'seqno', 'subno', 'trustee']

def create_tables():
    """Creates sqlite tables from downloaded Build_extract_*.sql files"""
    tables = []
    indexes = []
    for file in glob.glob('data/in/Build_extract_*.sql'):
        print("Creating table from '{}'".format(file))
        with open(file) as fp:
            sql = fp.read()
            table_re = re.search('CREATE TABLE \[dbo\]\.\[extract_(.+?)\]\((.+)\) ON', sql, re.DOTALL)
            table = table_re.group(1)
            col_defs = []
            for column in [column.strip() for column in table_re.group(2).strip().split(',\n')]:
                column_re = re.match('\[(.+?)\] (.+?) ((NOT )?NULL)', column)
                col_name = column_re.group(1)
                col_type = _translate_col_type(column_re.group(2))
                col_defs.append(col_name + ' ' + col_type)
                if col_name in indexed_cols:
                    indexes.append('CREATE INDEX {0}_{1} ON {0} ({1})'.format(table, col_name))
            tables.append('DROP TABLE IF EXISTS {}'.format(table))
            tables.append('CREATE TABLE IF NOT EXISTS {0} ({1})'.format(table, ', '.join(col_defs)))
        conn = sqlite3.connect('data/out/cc-datasette.db')
        c = conn.cursor()
        for command in tables + indexes:
            c.execute(command)

def insert_rows():
    conn = sqlite3.connect('data/out/cc-datasette.db')
    c = conn.cursor()
    for file in glob.glob('data/in/extract_*.bcp'):
        print("Importing data from '{}'".format(file))
        name_match = re.search('data\/in\/extract_(.+)\.bcp', file)
        table_name = name_match.group(1)
        with open(file, encoding='latin_1') as fp:
            data = fp.read()
            data = data.replace('\n', '\\n').replace('\t', '\\t').replace('@**@', '\t')
            for row in data.split('*@@*')[:-1]:
                cols = row.split('\t')
                query = 'INSERT INTO {} VALUES ({})'.format(table_name, ','.join(['?']*len(cols)))
                c.execute(query, cols)
        conn.commit()
