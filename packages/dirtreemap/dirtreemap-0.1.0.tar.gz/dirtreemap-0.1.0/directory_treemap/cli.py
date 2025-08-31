import argparse
from pathlib import Path
from directory_treemap.directory_treemap import DirectoryTreemap

def main():
    parser = argparse.ArgumentParser(description="Generate a directory treemap visualization.")
    parser.add_argument("base_path", type=Path, help="Base directory to scan")
    parser.add_argument("output_dir", type=Path, help="Directory to save the output HTML file")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel scanning")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum directory depth to display")
    parser.add_argument("--max-files", type=int, default=50, help="Max files per directory before aggregating")
    parser.add_argument("--open", action="store_true", help="Open the report after generation")
    parser.add_argument("--report-filename", type=str, default="directory_treemap.html", help="Output HTML filename")

    args = parser.parse_args()

    dt = DirectoryTreemap(
        base_path=args.base_path,
        output_dir=args.output_dir,
        parallel=args.parallel
    )
    dt.scan()
    dt.generate_treemap(max_depth=args.max_depth, max_files=args.max_files)
    dt.save_report(report_filename=args.report_filename)
    if args.open:
        dt.open_report()

if __name__ == "__main__":
    main()