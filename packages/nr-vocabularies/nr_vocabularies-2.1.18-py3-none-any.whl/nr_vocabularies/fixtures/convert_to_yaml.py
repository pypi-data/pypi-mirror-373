from pathlib import Path
import yaml

from oarepo_runtime.datastreams.readers.excel import ExcelReader

def convert_to_yaml(xlsx_file):
    reader = ExcelReader(source=xlsx_file)
    entries = [dict(entry.entry) for entry in reader.iter_entries()]
    yaml_file = xlsx_file.with_suffix(".yaml")
    with open(yaml_file, "w") as f:
        yaml.safe_dump_all(entries, f, encoding="utf-8", allow_unicode=True)

def convert_all():
    xlsx_directory = Path(__file__).parent
    for xlsx_file in xlsx_directory.glob("*.xlsx"):
        convert_to_yaml(xlsx_file)

if __name__ == '__main__':
    convert_all()