import glob
from hestia_earth.utils.pivot.pivot_csv import pivot_csv


def pivot_csv_file(filepath: str):
  pd = pivot_csv(filepath)
  dest = filepath.replace('.csv', '-compacted.csv')
  pd.to_csv(dest, index=None)


files = glob.glob('examples/*.csv')

list(map(pivot_csv_file, files))
