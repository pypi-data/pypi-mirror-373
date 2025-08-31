import os
import logging
from multiprocessing import Pool, cpu_count
from typing import Optional

import pandas as pd
from tqdm import tqdm
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

from directory_treemap.utils.file_utils import human_readable_size


class DirectoryTreemap:
    """Class to scan a directory and generate a treemap visualization of its contents.
    """

    def __init__(self, base_path: Path,
                 output_dir: Path,
                 parallel: bool = False):
        """Initialize the DirectoryTreemap instance.

        Args:
            base_path: The base directory to scan.
            output_dir: The directory to save the output HTML file.
            parallel: Whether to use parallel processing for scanning.
        """
        self.base_path: Path = Path(base_path)
        self.output_dir: Path = Path(output_dir)
        self.max_depth: Optional[int] = None
        self.max_files: Optional[int] = None
        self.parallel: bool = parallel
        self.file_data: list = []
        self.total_size: float = 0
        self.df: Optional[pd.DataFrame] = None
        self.fig: Optional[go.Figure] = None
        self.report_filename: Optional[str] = None

        self.path_columns: list = []
        self.limit_depth = None
        self.scan_time = None

        # Setup logging
        log_file = self.output_dir / 'dirtreemap.log'
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.info(
            f"Initialized DirectoryTreemap with base_path={self.base_path}, output_dir={self.output_dir}, max_depth={self.max_depth}, parallel={self.parallel}")

    def _scan_dir(self, path):
        scanned = []
        try:
            def fast_scan(p):
                for entry in os.scandir(p):
                    if entry.is_file():
                        yield entry.path, entry.stat().st_size
                    elif entry.is_dir():
                        yield from fast_scan(entry.path)

            for file_path, size in fast_scan(path):
                scanned.append((file_path, size))
        except Exception as e:
            logging.warning(f"Failed to scan directory: {path} - {e}")
        return scanned

    def scan(self):
        logging.info("Starting scan...")
        tic = pd.Timestamp.now()
        top_dirs = [entry.path for entry in os.scandir(self.base_path) if entry.is_dir()]
        top_files = [entry.path for entry in os.scandir(self.base_path) if entry.is_file()]

        # Scan top-level files first
        for file_path in top_files:
            try:
                size = os.path.getsize(file_path)
                self.file_data.append((file_path, size))
                self.total_size += size
            except Exception as e:
                logging.warning(f"Failed to access top-level file: {file_path} - {e}")

        # Scan subdirectories
        # Parallel branch
        if self.parallel:
            with Pool(cpu_count()) as pool:
                with tqdm(total=len(top_dirs), desc="Scanning directories", dynamic_ncols=True) as pbar:
                    for scanned in pool.imap(self._scan_dir, top_dirs):
                        self.file_data.extend(scanned)
                        self.total_size += sum(size for _, size in scanned)
                        pbar.set_postfix({"Scanned": human_readable_size(self.total_size)})
                        pbar.update(1)
        else:
            with tqdm(top_dirs, desc="Scanning directories", dynamic_ncols=True) as pbar:
                for dir_path in pbar:
                    scanned = self._scan_dir(dir_path)
                    self.file_data.extend(scanned)
                    self.total_size += sum(size for _, size in scanned)
                    pbar.set_postfix({"Scanned": human_readable_size(self.total_size)})
        self.scan_time = pd.Timestamp.now()
        logging.info(
            f"Scan completed in {str(pd.Timedelta(self.scan_time - tic)).split('.')[0]}."
            f" Total size scanned: {human_readable_size(self.total_size)}")

    def _build_dataframe(self):
        from collections import defaultdict, deque

        max_depth = self.max_depth
        max_files = self.max_files if self.max_files is not None else 10

        # Step 1: Build file and directory structure
        file_size_map = {}
        dir_children = defaultdict(list)
        all_dirs = set()
        for file_path, size in self.file_data:
            file_path = Path(file_path)
            file_size_map[str(file_path)] = size
            parent = str(file_path.parent)
            dir_children[parent].append((str(file_path), size))
            curr = file_path.parent
            while curr != self.base_path.parent:
                all_dirs.add(str(curr))
                curr = curr.parent

        # Step 2: Aggregate files per directory (apply max_files)
        aggregated_file_data = []
        for dir_path, files in dir_children.items():
            if max_files and len(files) > max_files:
                files_sorted = sorted(files, key=lambda x: x[1], reverse=True)
                keep = files_sorted[:max_files]
                other = files_sorted[max_files:]
                other_size = sum(size for _, size in other)
                aggregated_file_data.extend(keep)
                if other:
                    aggregated_file_data.append((
                        f"{dir_path}/Other files ({len(other)})",
                        other_size
                    ))
            else:
                aggregated_file_data.extend(files)

        # Step 3: Aggregate sizes bottom-up
        dir_sizes = defaultdict(int)
        dir_filecounts = defaultdict(int)
        for file_path, size in aggregated_file_data:
            file_path = Path(file_path)
            rel_parts = file_path.relative_to(self.base_path).parts
            if len(rel_parts) > max_depth:
                ancestor = self.base_path.joinpath(*rel_parts[:max_depth])
            else:
                ancestor = file_path
            curr = ancestor
            while True:
                dir_sizes[str(curr)] += size
                dir_filecounts[str(curr)] += 1
                if curr == self.base_path:
                    break
                curr = curr.parent

        # Step 4: Build all_paths up to max_depth
        all_paths = set()
        for file_path, _ in aggregated_file_data:
            file_path = Path(file_path)
            rel_parts = file_path.relative_to(self.base_path).parts
            for d in range(1, min(len(rel_parts), max_depth) + 1):
                all_paths.add(str(self.base_path.joinpath(*rel_parts[:d])))
            all_paths.add(str(self.base_path))

        # Step 5: Build DataFrame
        path_to_id = {}
        data = []
        next_id = 0

        def depth_from_base(p):
            return len(Path(p).relative_to(self.base_path).parts)

        for p in sorted(all_paths, key=lambda x: (depth_from_base(x), x)):
            curr = Path(p)
            is_file = str(curr) in file_size_map
            if str(curr) == str(self.base_path):
                parent_id = ''
                label = curr.name if curr.name else str(curr)
                if not label or label == '.':
                    label = str(self.base_path)
            else:
                parent_id = str(path_to_id.get(str(curr.parent), ''))
                label = curr.name if curr.name else str(curr)
            if is_file:
                size = file_size_map.get(str(curr), None)
                filecount = 1
            else:
                size = dir_sizes.get(str(curr), 0)
                filecount = dir_filecounts.get(str(curr), 0)
            data.append({
                'id': str(next_id),
                'parent': parent_id,
                'label': label,
                'bytes': size,
                'size': human_readable_size(size) if size is not None else '',
                'full_path': str(curr),
                'filecount': filecount
            })
            path_to_id[str(curr)] = next_id
            next_id += 1

        self.df = pd.DataFrame(data)

    def generate_treemap(self, title: str = 'Directory Treemap',
                         max_depth: Optional[int] = None,
                         max_files: Optional[int] = 50):
        """Generate the treemap visualization.
        Args:
            title: Title of the treemap.
            max_depth: Maximum directory depth to display.
            max_files: Maximum number of files to display per directory before aggregating into "Other files".
        """

        self.max_depth = max_depth
        self.max_files = max_files
        if self.df is None:
            self._build_dataframe()

        df = self.df.copy()
        df.loc[df['parent'] == '', 'label'] = df.loc[df['parent'] == '', 'full_path'].values[0]
        df['bytes'] = df['bytes'].fillna(0)

        base_dir_color = "#b3c6ff"  # You can pick any color you like
        scan_time = self.scan_time.strftime("%Y-%m-%d %H:%M:%S")

        # Build color list: first node is base dir, rest are auto
        colors = [base_dir_color] + [None] * (len(df) - 1)

        fig = go.Figure(go.Treemap(
            labels=df['label'],
            parents=df['parent'],
            values=df['bytes'],
            ids=df['id'],
            customdata=df[['size', 'filecount']],
            hovertemplate='<b>%{label}</b><br>Size: %{customdata[0]}<br>Files: %{customdata[1]}<extra></extra>',
            branchvalues="total",
            marker=dict(colors=colors)
        ))

        fig.update_layout(
            title=title,
            margin=dict(b=40),  # Add space for footer
            annotations=[
                dict(
                    text=f"Scan run: {scan_time}",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.5, y=-0.04, xanchor="center", yanchor="bottom",
                    font=dict(size=12, color="gray")
                )
            ]
        )
        self.fig = fig
        return fig

    def save_report(self, report_filename: str = "directory_treemap.html"):
        """Save the treemap to an HTML file.
        Args:
            report_filename: Name of the output HTML file.
        """

        self.report_filename = report_filename

        if not hasattr(self, 'fig'):
            raise ValueError("Treemap not generated. Run generate_treemap() first.")
        output_path = self.output_dir / self.report_filename
        self.fig.write_html(output_path)
        print(f"Treemap saved to {output_path}")

    def open_report(self):
        """Open the saved treemap HTML file in the default web browser."""
        import webbrowser
        output_path = self.output_dir / self.report_filename
        if not output_path.exists():
            raise ValueError("Report file does not exist. Save the report first.")
        webbrowser.open(f'file://{output_path.resolve()}')
