from argparse import ArgumentParser
from collections import Counter
import csv
import gzip
from pathlib import Path


def count_periods(path, encoding):
    opener = gzip.open if path.suffix.lower() == '.gz' else open
    with opener(path, 'rt', encoding=encoding, newline='') as stream:
        dialect = csv.Sniffer().sniff(stream.readline(), delimiters=',;\t')
        stream.seek(0)
        reader = csv.DictReader(stream, dialect=dialect)
        fields = {name.strip().upper(): name for name in reader.fieldnames or []}
        if 'PERIODO' not in fields:
            raise ValueError('Falta la columna PERIODO en el CSV.')
        period_column = fields['PERIODO']
        counts = Counter()
        for row in reader:
            period = (row[period_column] or '').strip()
            if len(period) != 5 or not period.isdecimal():
                period = 'SIN_CODIGO_VALIDO'
            counts[period] += 1
    if not counts:
        raise ValueError('El CSV no contiene registros.')
    return counts


def main():
    parser = ArgumentParser(description='Cuenta filas de Saber 11 por código original de periodo.')
    parser.add_argument('archivo', type=Path, help='Fuente CSV o CSV comprimido en gzip.')
    parser.add_argument('--salida', required=True, type=Path)
    parser.add_argument('--encoding', default='utf-8-sig')
    args = parser.parse_args()
    counts = count_periods(args.archivo, args.encoding)
    with args.salida.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(('periodo_original', 'filas_csv'))
        writer.writerows(sorted(counts.items()))
    print(f'Filas leídas: {sum(counts.values()):,}')


if __name__ == '__main__':
    main()
