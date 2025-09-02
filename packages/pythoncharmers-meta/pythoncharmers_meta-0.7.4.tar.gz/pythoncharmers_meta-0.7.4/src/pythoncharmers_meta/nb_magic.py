"""
An IPython extension that registers notebook cell magics: %code, %md, and %mdat

%code: Grabs code cells from a notebook on the filesystem
%md: Grabs markdown cells from a notebook on the filesystem (by index)
%mdat: Grabs markdown cells by position relative to code cells
%nb: Alias for %code (for backward compatibility)

All default to the most recently modified notebook in the highest-numbered
~/Trainer_XYZ/ folder.

For help on the magics, run:

    %code?
    %md?
    %mdat?

"""

import warnings
from pathlib import Path
from typing import Iterable, Optional

from IPython.core.magic import Magics, magics_class, line_magic
from IPython.core.magics.code import extract_code_ranges
from IPython.core.error import UsageError
import nbformat


def extract_code_ranges_inclusive(ranges_str: str) -> Iterable[tuple[int, int]]:
    """Turn a string of ranges, inclusive of the endpoints, into 2-tuples of
    (start, stop) suitable for use with range(start, stop).

    Examples
    --------
    >>> list(extract_code_ranges_inclusive("5-10 2"))
    [(5, 11), (2, 3)]

    >>> list(
    ...     tz.concat((range(start, stop) for (start, stop) in extract_code_ranges_inclusive('3-4 6 3')))
    ... )

    [3, 4, 6, 3]
    """
    return ((start + 1, stop + 1) for (start, stop) in extract_code_ranges(ranges_str))


def get_cell_nums(ranges_str: str) -> Iterable[int]:
    """
    Yields cell numbers specified in the given ranges_str string, assuming the
    ranges are specified inclusive of the endpoint.

    Example:
    >>> list(get_cell_nums('5-6 2 12'))
    [5, 6, 2, 12]
    """
    for start, stop in extract_code_ranges_inclusive(ranges_str):
        yield from range(start, stop)


def get_cell_input(cell_number: int, nb):
    "Return input for the given code cell in the given notebook"
    if not isinstance(cell_number, int):
        raise ValueError("pass an integer cell number")
    for cell in nb["cells"]:
        if "execution_count" in cell and cell["execution_count"] == cell_number:
            return cell["source"]


def get_markdown_cells(nb) -> list[tuple[int, str]]:
    """
    Return a list of (index, source) tuples for all markdown cells in the notebook.
    Index is 1-based for user-friendliness.
    """
    markdown_cells = []
    md_index = 1
    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown":
            markdown_cells.append((md_index, cell["source"]))
            md_index += 1
    return markdown_cells


def get_markdown_cell_by_index(cell_index: int, nb) -> Optional[str]:
    """
    Return the source of the markdown cell at the given 1-based index.
    Returns None if index is out of range.
    """
    markdown_cells = get_markdown_cells(nb)
    if 1 <= cell_index <= len(markdown_cells):
        return markdown_cells[cell_index - 1][1]
    return None


def get_markdown_after_code(code_cell_num: int, nb) -> list[str]:
    """
    Return all markdown cells immediately after the specified code cell,
    stopping at the next code cell or end of notebook.
    """
    found_code = False
    markdown_cells = []

    for cell in nb["cells"]:
        if cell["cell_type"] == "code" and cell.get("execution_count") == code_cell_num:
            found_code = True
            continue

        if found_code:
            if cell["cell_type"] == "markdown":
                markdown_cells.append(cell["source"])
            elif cell["cell_type"] == "code":
                break  # Stop at next code cell

    return markdown_cells


def get_markdown_before_code(code_cell_num: int, nb) -> list[str]:
    """
    Return all markdown cells that appear before the specified code cell,
    regardless of other code cells in between.
    """
    markdown_cells = []

    for cell in nb["cells"]:
        if cell["cell_type"] == "code" and cell.get("execution_count") == code_cell_num:
            # Found the target code cell, return all markdown cells collected so far
            return markdown_cells
        elif cell["cell_type"] == "markdown":
            markdown_cells.append(cell["source"])

    # If we didn't find the code cell, return empty list
    return []


def get_markdown_between_codes(start_code: int, end_code: int, nb) -> list[str]:
    """
    Return all markdown cells between two code cells (exclusive).
    """
    found_start = False
    markdown_cells = []

    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            if cell.get("execution_count") == start_code:
                found_start = True
                continue
            elif cell.get("execution_count") == end_code:
                break

        if found_start and cell["cell_type"] == "markdown":
            markdown_cells.append(cell["source"])

    return markdown_cells


def paths_sorted_by_mtime(paths: Iterable[Path], ascending: bool = True) -> list[Path]:
    """
    Return a sorted list of the given Path objects sorted by
    modification time.
    """
    mtimes = {path: path.stat().st_mtime for path in paths}
    return sorted(paths, key=mtimes.get)


def latest_trainer_path() -> Path:
    """
    Look for the highest-numbered ~/Trainer_XYZ folder and return it as a
    Path object.
    """
    # If there's just a "Trainer" folder by itself, don't assume it's the
    # current one, because this was our convention with earlier courses.
    # Participants who previously did an old course would otherwise get an
    # old trainer transcript if they use %nb
    # naked_trainer_folder = Path('~/Trainer').expanduser()
    # if naked_trainer_folder.exists():
    #     return naked_trainer_folder

    # Sort alphanumerically and return the last one.
    trainer_paths = [p for p in Path("~").expanduser().glob("Trainer_*") if p.is_dir()]
    try:
        latest_trainer_path = sorted(trainer_paths, key=course_num_from_trainer_path)[
            -1
        ]
        return latest_trainer_path
    except Exception:
        cwd = Path.cwd()
        warnings.warn(
            f"No ~/Trainer_* folders found. Using current directory {cwd}",
            RuntimeWarning,
        )
        return cwd


def latest_notebook_file(folder_path: Path) -> Path:
    """
    Return the most recently modified .ipynb file in the given folder
    path.
    """
    notebook_files = list(folder_path.glob("*.ipynb"))
    try:
        path = paths_sorted_by_mtime(notebook_files)[-1]
    except Exception:
        raise OSError(f"Cannot find any .ipynb files in {folder_path}")
    return path


def course_num_from_trainer_path(trainer_path: Path) -> str:
    """
    Returns a course 'number' like 612 or 705b as a string
    from a Trainer path like `Path('/home/jovyan/Trainer_612')`
    """
    return trainer_path.name.split("_")[1]


@magics_class
class NotebookMagic(Magics):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notebook_path = latest_trainer_path()

        # If notebook_file_override is set, use this notebook file for
        # %code. If notebook_file_override is None, use the latest notebook
        # in the notebook_path (given by %nbpath):
        self.notebook_file_override = None

    @line_magic
    def nbpath(self, arg_s: str) -> Optional[str]:
        """
        Usage:
            %nbpath
            Show the folder path being queried for %code and %md

            %nbpath ~/Trainer_614
            Set ~/Trainer_614 as the folder to query for %code and %md

            %nbpath --reset
            Reset the folder being queried for %code and %md to the highest-numbered ~/Trainer_XYZ folder.
        """
        if arg_s == "":
            return str(self.notebook_path)
        elif "--reset" in arg_s:
            self.notebook_path = latest_trainer_path()
        else:
            new_notebook_path = Path(arg_s).expanduser().resolve()
            if new_notebook_path.exists():
                self.notebook_path = new_notebook_path
            else:
                raise UsageError(f"path {new_notebook_path} does not exist")

    @line_magic
    def nbfile(self, arg_s: str) -> Optional[str]:
        """
        Usage:
            %nbfile
            Show the file in %nbpath being queried for %code and %md

            %nbfile "Training day 1.ipynb"
            Set the notebook file in %nbpath to be queried for %code and %md

            %nbfile --reset
            Reset the notebook file to the most recently modified
            .ipynb file in the directory given by %nbpath.
        """
        if arg_s == "":
            if self.notebook_file_override is not None:
                print(f"The default notebook is set to {self.notebook_file_override}")
                return self.notebook_file_override
            else:
                my_notebook_file = latest_notebook_file(self.notebook_path)
                print(
                    "No default notebook is set. Using the most recently modified file in %nbpath."
                )
                return str(my_notebook_file)
        elif "--reset" in arg_s:
            self.notebook_file_override = None
            print(
                "The default notebook has been unset. The most recently modified .ipynb file will be used in the directory given by %nbpath."
            )
            return None
        else:
            # Strip off any quotes at the start or end of the filename
            # and expand ~ to the user's home folder.
            # Then resolve any symlinks to get an absolute path.
            filepath = Path(arg_s.strip('"').strip("'")).expanduser().resolve()
            if not filepath.exists():
                raise Exception(f"notebook {filepath} does not exist")
            else:
                # Interpret it as a path or filename relative to %nbpath
                filepath = self.notebook_path / filepath
            self.notebook_file_override = filepath
            print(f"Set default notebook file to {self.notebook_file_override}")

    @line_magic
    def code(self, arg_s):
        """Load code cells from a notebook into the current frontend.
        Usage:

          %code n1-n2 n3-n4 n5 ...

        or:

          %code -f ipynb_filename n1-n2 n3-n4 n5 ...

          where `ipynb_filename` is a filename of a Jupyter notebook

        Ranges:

          Ranges are space-separated and inclusive of the endpoint.

          Example: 123 126 131-133

          This gives the contents of these code cells: 123, 126, 131, 132, 133.

        Optional arguments:

          -f ipynb_filename: the filename of a Jupyter notebook (optionally
              omitting the .ipynb extension). Default is the most recently
              modified .ipynb file in the highest-numbered ~/Trainer_XYZ/
              folder.

          -v [notebook_version]: default is 4
        """
        opts, args = self.parse_options(arg_s, "v:f:", mode="list")
        # for i, arg in enumerate(args):
        #     print(f'args[{i}] is {args[i]}')

        if "f" in opts:
            fname = opts["f"]
            if not fname.endswith(".ipynb"):
                fname += ".ipynb"
            path = Path(fname)
            if not path.exists():
                raise UsageError(f"File {path.absolute()} does not exist")
        else:
            # If there's a default set, use it:
            if self.notebook_file_override is not None:
                my_notebook_file = self.notebook_file_override
            else:
                try:
                    my_notebook_file = latest_notebook_file(self.notebook_path)
                except Exception:
                    raise UsageError(
                        "No default notebook set (%nbfile); no notebook filename specified (-f option); and cannot infer it."
                    )

        if "v" in opts:
            try:
                version = int(opts["v"])
            except ValueError:
                warnings.warn(
                    "Cannot interpret version number as an integer. Defaulting to version 4."
                )
                version = 4
        else:
            version = 4

        codefrom = " ".join(args)

        # Load notebook into a dict
        nb = nbformat.read(my_notebook_file, as_version=version)

        # Get cell numbers
        cellnums = list(get_cell_nums(codefrom))

        # Get cell contents
        contents = [get_cell_input(cellnum, nb) for cellnum in cellnums]

        # Remove Nones
        contents = [c for c in contents if c is not None]

        # print(*contents, sep='\n\n')
        contents = "\n\n".join(contents)
        contents = "# %code {}\n".format(arg_s) + contents

        self.shell.set_next_input(contents, replace=True)

    @line_magic
    def nb(self, arg_s):
        """Alias for %code (for backward compatibility).

        Load code cells from a notebook into the current frontend.
        See %code? for full documentation.
        """
        # Simply call the code method with the same arguments
        return self.code(arg_s)

    @line_magic
    def md(self, arg_s):
        """Load markdown cells into the current frontend.
        Usage:

          %md n1-n2 n3-n4 n5 ...

        or:

          %md --list

        or:

          %md -f ipynb_filename n1-n2 n3-n4 n5 ...

          where `ipynb_filename` is a filename of a Jupyter notebook

        Ranges:

          Ranges are space-separated and inclusive of the endpoint.
          Numbers refer to the sequential index of markdown cells (1st, 2nd, 3rd, etc.)

          Example: 1 3 5-7

          This gives the contents of markdown cells: 1, 3, 5, 6, 7.

        Special options:

          --list: Show a numbered list of all markdown cells with previews

        Optional arguments:

          -f ipynb_filename: the filename of a Jupyter notebook (optionally
              omitting the .ipynb extension). Default is the most recently
              modified .ipynb file in the highest-numbered ~/Trainer_XYZ/
              folder.

          -v [notebook_version]: default is 4

        Note: After running this magic, convert the cell to Markdown type
        using Esc M in Jupyter. Unlike %code, this command does not add a
        comment line at the top.
        """
        # Store original arg_s for better error messages
        original_arg_s = arg_s
        
        # Check for common mistakes (but not --list itself!)
        if "--list" not in arg_s and ("--lsit" in arg_s or "--lst" in arg_s or "--lis" in arg_s or "--lits" in arg_s):
            raise UsageError(
                f"Invalid option. Did you mean '--list'?\n"
                f"Usage: %md --list  or  %md 1-3 5 7\n"
                f"See %md? for full documentation."
            )
        
        # Check if user is trying to use %mdat syntax
        if any(arg_s.startswith(prefix) for prefix in ["after:", "before:", "between:"]):
            raise UsageError(
                f"'{arg_s}' is not valid for %md.\n"
                f"For position-based selection, use %mdat:\n"
                f"  %mdat {arg_s}\n"
                f"For %md, use cell indices:\n"
                f"  %md 1-3     # Get markdown cells 1, 2, and 3\n"
                f"  %md --list  # List all markdown cells"
            )
        
        # Check for --list before parse_options
        list_mode = "--list" in arg_s
        if list_mode:
            # Remove --list from arg_s before parsing options
            arg_s = arg_s.replace("--list", "").strip()
        
        try:
            opts, args = self.parse_options(arg_s, "v:f:", mode="list")
        except UsageError as e:
            # Check if it's an unrecognized option error
            error_msg = str(e)
            if "not recognized" in error_msg:
                # Extract the bad option if possible
                import re
                match = re.search(r'option (\S+) not recognized', error_msg)
                if match:
                    bad_option = match.group(1)
                    raise UsageError(
                        f"Invalid option '{bad_option}'.\n"
                        f"Valid options for %md:\n"
                        f"  --list           Show all markdown cells with previews\n"
                        f"  -f filename      Specify notebook file\n"
                        f"  -v version       Notebook version (default: 4)\n"
                        f"Examples:\n"
                        f"  %md 1-3 5       Get cells 1,2,3 and 5\n"
                        f"  %md --list      List all markdown cells"
                    )
            raise

        # Handle --list option
        if list_mode:
            # Determine notebook file
            if "f" in opts:
                fname = opts["f"]
                if not fname.endswith(".ipynb"):
                    fname += ".ipynb"
                my_notebook_file = Path(fname)
                if not my_notebook_file.exists():
                    raise UsageError(
                        f"File {my_notebook_file.absolute()} does not exist"
                    )
            else:
                if self.notebook_file_override is not None:
                    my_notebook_file = self.notebook_file_override
                else:
                    try:
                        my_notebook_file = latest_notebook_file(self.notebook_path)
                    except Exception:
                        raise UsageError(
                            "No default notebook set (%nbfile); no notebook filename specified (-f option); and cannot infer it."
                        )

            version = int(opts.get("v", 4))
            nb = nbformat.read(my_notebook_file, as_version=version)

            markdown_cells = get_markdown_cells(nb)
            if not markdown_cells:
                print("No markdown cells found in the notebook.")
                return

            print(f"Markdown cells in {my_notebook_file.name}:")
            print("-" * 50)
            for idx, source in markdown_cells:
                preview = source[:100].replace("\n", " ")
                if len(source) > 100:
                    preview += "..."
                print(f"{idx:3}: {preview}")
            return

        # Normal operation - get specific cells
        if "f" in opts:
            fname = opts["f"]
            if not fname.endswith(".ipynb"):
                fname += ".ipynb"
            my_notebook_file = Path(fname)
            if not my_notebook_file.exists():
                raise UsageError(f"File {my_notebook_file.absolute()} does not exist")
        else:
            if self.notebook_file_override is not None:
                my_notebook_file = self.notebook_file_override
            else:
                try:
                    my_notebook_file = latest_notebook_file(self.notebook_path)
                except Exception:
                    raise UsageError(
                        "No default notebook set (%nbfile); no notebook filename specified (-f option); and cannot infer it."
                    )

        version = int(opts.get("v", 4))

        if not args:
            raise UsageError(
                "No cell indices specified.\n"
                "Usage examples:\n"
                "  %md 1           # Get first markdown cell\n"
                "  %md 1-3 5       # Get cells 1,2,3 and 5\n"
                "  %md --list      # List all markdown cells\n"
                "See %md? for full documentation."
            )

        cellranges = " ".join(args)
        
        # Additional validation for common mistakes
        for arg in args:
            if ":" in arg:
                raise UsageError(
                    f"'{arg}' contains ':' which is not valid for %md.\n"
                    f"For position-based selection (after:, before:, between:), use %mdat:\n"
                    f"  %mdat {arg}\n"
                    f"For %md, use numeric indices:\n"
                    f"  %md 1-3        # Get cells 1, 2, and 3"
                )

        # Load notebook
        nb = nbformat.read(my_notebook_file, as_version=version)

        # Get cell numbers
        cellnums = list(get_cell_nums(cellranges))

        # Get markdown cell contents
        contents = []
        for cellnum in cellnums:
            content = get_markdown_cell_by_index(cellnum, nb)
            if content is not None:
                contents.append(content)

        if not contents:
            # Get total number of markdown cells for better error message
            all_markdown = get_markdown_cells(nb)
            total_md_cells = len(all_markdown)
            
            if total_md_cells == 0:
                raise UsageError(
                    f"No markdown cells found in {my_notebook_file.name}.\n"
                    f"This notebook contains only code cells."
                )
            else:
                invalid_indices = [num for num in cellnums if num > total_md_cells or num < 1]
                if invalid_indices:
                    raise UsageError(
                        f"Invalid markdown cell indices: {invalid_indices}\n"
                        f"This notebook has {total_md_cells} markdown cell(s) (numbered 1-{total_md_cells}).\n"
                        f"Use '%md --list' to see all available markdown cells."
                    )
                else:
                    # This shouldn't happen, but just in case
                    raise UsageError(
                        f"Could not retrieve markdown cells {cellnums}.\n"
                        f"Use '%md --list' to see available cells."
                    )
            return

        # Join contents without header comment for markdown
        contents = "\n\n".join(contents)

        self.shell.set_next_input(contents, replace=True)

    @line_magic
    def mdat(self, arg_s):
        """Load markdown cells based on their position relative to code cells.
        Usage:

          %mdat after:n     - Get markdown cells after code cell n (until next code cell)
          %mdat before:n    - Get ALL markdown cells before code cell n
          %mdat between:n:m - Get markdown cells between code cells n and m

        or with a specific notebook file:

          %mdat -f ipynb_filename after:n

        Examples:

          %mdat after:3      - Get all markdown cells after code cell 3
          %mdat before:5     - Get all markdown cells before code cell 5
          %mdat between:2:4  - Get all markdown cells between code cells 2 and 4

        Optional arguments:

          -f ipynb_filename: the filename of a Jupyter notebook (optionally
              omitting the .ipynb extension). Default is the most recently
              modified .ipynb file in the highest-numbered ~/Trainer_XYZ/
              folder.

          -v [notebook_version]: default is 4

        Note: After running this magic, convert the cell to Markdown type
        using Esc M in Jupyter. Unlike %nb, this command does not add a comment
        line at the top.
        """
        opts, args = self.parse_options(arg_s, "v:f:", mode="list")

        if "f" in opts:
            fname = opts["f"]
            if not fname.endswith(".ipynb"):
                fname += ".ipynb"
            my_notebook_file = Path(fname)
            if not my_notebook_file.exists():
                raise UsageError(f"File {my_notebook_file.absolute()} does not exist")
        else:
            if self.notebook_file_override is not None:
                my_notebook_file = self.notebook_file_override
            else:
                try:
                    my_notebook_file = latest_notebook_file(self.notebook_path)
                except Exception:
                    raise UsageError(
                        "No default notebook set (%nbfile); no notebook filename specified (-f option); and cannot infer it."
                    )

        version = int(opts.get("v", 4))

        if not args:
            raise UsageError(
                "Please specify position (after:n, before:n, or between:n:m)"
            )

        position_spec = args[0]

        # Load notebook
        nb = nbformat.read(my_notebook_file, as_version=version)

        # Parse position specification
        contents = []
        if position_spec.startswith("after:"):
            try:
                code_num = int(position_spec.split(":")[1])
                markdown_cells = get_markdown_after_code(code_num, nb)
                contents = markdown_cells
            except (ValueError, IndexError):
                raise UsageError(
                    "Invalid format. Use: after:n where n is a code cell number"
                )

        elif position_spec.startswith("before:"):
            try:
                code_num = int(position_spec.split(":")[1])
                markdown_cells = get_markdown_before_code(code_num, nb)
                contents = markdown_cells
            except (ValueError, IndexError):
                raise UsageError(
                    "Invalid format. Use: before:n where n is a code cell number"
                )

        elif position_spec.startswith("between:"):
            try:
                parts = position_spec.split(":")
                start_code = int(parts[1])
                end_code = int(parts[2])
                markdown_cells = get_markdown_between_codes(start_code, end_code, nb)
                contents = markdown_cells
            except (ValueError, IndexError):
                raise UsageError(
                    "Invalid format. Use: between:n:m where n and m are code cell numbers"
                )

        else:
            raise UsageError(
                "Position must be specified as after:n, before:n, or between:n:m"
            )

        if not contents:
            warnings.warn(f"No markdown cells found for position: {position_spec}")
            return

        # Join contents without header comment for markdown
        contents = "\n\n".join(contents)

        self.shell.set_next_input(contents, replace=True)


# In order to actually use these magics, you must register them with a
# running IPython. See load_ipython_extension() in __init__.py.
