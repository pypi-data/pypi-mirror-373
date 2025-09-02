import argparse
from .io import quick_summary

def main():
    parser = argparse.ArgumentParser(prog="atikin-data", description="Atikin-Data small CLI")
    sub = parser.add_subparsers(dest="cmd")

    parser_q = sub.add_parser("summary", help="Quick summary for a dataset file (csv/json/xlsx)")
    parser_q.add_argument("path", help="Path to file")

    args = parser.parse_args()
    if args.cmd == "summary":
        s = quick_summary(args.path)
        print(f"Rows={s['rows']}, Columns={s['columns']}, Missing={s['missing']}")
    else:
        parser.print_help()
