# dirtreemap
Directory treemap visualization tool using Plotly

## Installation
You can install the package via pip:

```bash
pip install dirtreemap
```
## Usage
You can use the `dirtreemap` command in your terminal to generate a treemap visualization of a directory. For example:
```bash
dirtreemap /path/to/directory /path/to/output_dir --report-filename treemap.html
```
This will create an HTML file with the treemap visualization of the specified directory.
You can also customize the visualization using various options. For a full list of options, run:
```bash
dirtreemap --help
```
> **Note**
>
> A log file named `dirtreemap.log` will be created in the specified output directory to record scan and generation details.

## Example
Here's an example of how to use `dirtreemap` in a Python script:
```python
import os
from pathlib import Path

from directory_treemap import DirectoryTreemap

scan_dir: Path = Path(os.path.expanduser("~"))

dtm: DirectoryTreemap = DirectoryTreemap(base_path=scan_dir,
                                         output_dir=Path("."),
                                         parallel=False)
dtm.scan()
dtm.generate_treemap(title='Demo Directory Treemap',
                     max_depth=4,
                     max_files=25)
dtm.save_report()
dtm.open_report()
```
This will generate a treemap visualization of the specified directory and save it as `treemap.html`

## Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details
