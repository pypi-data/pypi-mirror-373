import argparse
import kwogger

parser = argparse.ArgumentParser(description='Kwogger interactive logger utility.')
parser.add_argument('path', help='log path to tail')
parser.add_argument('--level', '-l', default='NOTSET')
parser.add_argument('--seek', '-s', default='tail', choices=['head', 'tail'])
parser.add_argument('--format', '-f', choices=['log_file', 'cli'], default='cli')
args = parser.parse_args()

level = kwogger.level_value(args.level)

with kwogger.KwogFile(args.path, level, args.seek) as log:
    for entry in log.follow():
        print(entry.format(args.format))
