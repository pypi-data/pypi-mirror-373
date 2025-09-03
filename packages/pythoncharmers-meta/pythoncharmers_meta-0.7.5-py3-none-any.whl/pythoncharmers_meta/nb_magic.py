"""
An IPython extension that registers notebook cell magics: %code and %md

%code: Grabs code cells from a notebook on the filesystem
%md: Grabs markdown cells from a notebook (by index or relative to code cells)
%nb: Alias for %code (for backward compatibility)

All default to the most recently modified notebook in the highest-numbered
~/Trainer_XYZ/ folder.

For help on the magics, run:

    %code?
    %md?

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


def get_last_code_cell_with_number(code_num: int, nb) -> int:
    """
    Find the last code cell with the given execution_count.
    Returns the index of that cell in the notebook, or -1 if not found.
    """
    last_index = -1
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "code" and cell.get("execution_count") == code_num:
            last_index = i
    return last_index


def parse_md_range(range_str: str, nb) -> list[str]:
    """
    Parse a range specification and return the corresponding markdown cells.

    Supports:
    - "-N": All markdown before code cell N (using last occurrence)
    - "N-": All markdown after code cell N (using last occurrence)
    - "N-M": All markdown between code cells N and M (using last occurrences)
    - "mN": Markdown cell at index N
    - "mN-": Markdown cells from index N onwards
    - "mN-mM": Markdown cells from index N to M
    - "-mN": Markdown cells from beginning to index N
    """
    range_str = range_str.strip()
    markdown_contents = []

    # Handle markdown index syntax (mN, mN-mM, etc.)
    if "m" in range_str.lower():
        # Remove 'm' prefix and parse as regular range
        clean_range = range_str.lower().replace("m", "")

        # Handle different patterns
        if clean_range.startswith("-"):
            # "-N" means from beginning to N
            end_num = int(clean_range[1:])
            for i in range(1, end_num + 1):
                content = get_markdown_cell_by_index(i, nb)
                if content:
                    markdown_contents.append(content)
        elif clean_range.endswith("-"):
            # "N-" means from N to end
            start_num = int(clean_range[:-1])
            all_md = get_markdown_cells(nb)
            for i in range(start_num, len(all_md) + 1):
                content = get_markdown_cell_by_index(i, nb)
                if content:
                    markdown_contents.append(content)
        elif "-" in clean_range:
            # "N-M" means from N to M
            parts = clean_range.split("-")
            start_num = int(parts[0]) if parts[0] else 1
            end_num = int(parts[1]) if parts[1] else len(get_markdown_cells(nb))
            for i in range(start_num, end_num + 1):
                content = get_markdown_cell_by_index(i, nb)
                if content:
                    markdown_contents.append(content)
        else:
            # Single number
            content = get_markdown_cell_by_index(int(clean_range), nb)
            if content:
                markdown_contents.append(content)

    # Handle code-relative syntax (-N, N-, N-M)
    elif range_str.startswith("-"):
        # "-N" means all markdown before code cell N
        code_num = int(range_str[1:])
        # Find the last occurrence of this code cell number
        last_idx = get_last_code_cell_with_number(code_num, nb)
        if last_idx >= 0:
            # Get all markdown cells before this position
            for i, cell in enumerate(nb["cells"][:last_idx]):
                if cell["cell_type"] == "markdown":
                    markdown_contents.append(cell["source"])

    elif range_str.endswith("-"):
        # "N-" means all markdown after code cell N
        code_num = int(range_str[:-1])
        # Find the last occurrence of this code cell number
        last_idx = get_last_code_cell_with_number(code_num, nb)
        if last_idx >= 0:
            # Get all markdown cells after this position
            for i, cell in enumerate(nb["cells"][last_idx + 1 :]):
                if cell["cell_type"] == "markdown":
                    markdown_contents.append(cell["source"])

    elif "-" in range_str:
        # "N-M" means markdown between code cells N and M
        parts = range_str.split("-")
        start_code = int(parts[0])
        end_code = int(parts[1])

        # Find last occurrences of both code cell numbers
        start_idx = get_last_code_cell_with_number(start_code, nb)
        end_idx = get_last_code_cell_with_number(end_code, nb)

        if start_idx >= 0 and end_idx >= 0 and start_idx < end_idx:
            # Get markdown cells between these positions
            for i in range(start_idx + 1, end_idx):
                cell = nb["cells"][i]
                if cell["cell_type"] == "markdown":
                    markdown_contents.append(cell["source"])

    else:
        # Plain code cell number without range - not valid in new syntax
        raise ValueError(f"Invalid range specification: {range_str}")

    return markdown_contents


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
        """Load markdown cells from a notebook using flexible selection syntax.

        Usage:

          %md [ranges...]
          %md --list
          %md -f notebook.ipynb [ranges...]

        Range Syntax:

          Code-relative selections (refers to last occurrence of code cell number):
            -N       All markdown cells before code cell N
            N-       All markdown cells after code cell N
            N-M      All markdown cells between code cells N and M

          Markdown index selections:
            mN       Markdown cell number N
            mN-mM    Markdown cells N through M (inclusive)
            mN-      Markdown cells from N onwards
            -mN      Markdown cells from beginning through N

        Examples:

          %md -1 2-4 8-      # Before code 1, between code 2-4, after code 8
          %md m1 m3-m5       # Markdown cells 1, 3, 4, and 5
          %md m2- -1         # Markdown from cell 2 onwards, plus all before code 1
          %md --list         # List all markdown cells with numbers

        Optional arguments:

          -f filename      Specify notebook file (default: latest in Trainer folder)
          -v version       Notebook version (default: 4)
          --list          Show numbered list of all markdown cells

        Note: After running, convert the cell to Markdown with Esc M in Jupyter.
        """
        # Store original arg_s for better error messages
        original_arg_s = arg_s

        # Check for common mistakes (but not --list itself!)
        if "--list" not in arg_s and (
            "--lsit" in arg_s
            or "--lst" in arg_s
            or "--lis" in arg_s
            or "--lits" in arg_s
        ):
            raise UsageError(
                f"Invalid option. Did you mean '--list'?\n"
                f"Usage: %md --list  or  %md m1-m3  or  %md -1 2-\n"
                f"See %md? for full documentation."
            )

        # Check if user is trying to use old %mdat syntax
        if any(
            arg_s.startswith(prefix) for prefix in ["after:", "before:", "between:"]
        ):
            # Convert old syntax to new
            suggestion = (
                arg_s.replace("after:", "")
                .replace("before:", "-")
                .replace("between:", "")
            )
            if "between:" in arg_s:
                parts = arg_s.split(":")[1:]
                if len(parts) >= 2:
                    suggestion = f"{parts[0]}-{parts[1]}"
            raise UsageError(
                f"The syntax '{arg_s}' has been replaced.\n"
                f"New syntax: %md {suggestion}\n"
                f"Examples:\n"
                f"  %md -1        # All markdown before code cell 1\n"
                f"  %md 3-        # All markdown after code cell 3\n"
                f"  %md 2-4       # All markdown between code cells 2 and 4\n"
            )

        # Check for --list before parse_options
        list_mode = "--list" in arg_s
        if list_mode:
            # Remove --list from arg_s before parsing options
            arg_s = arg_s.replace("--list", "").strip()

        # Pre-process to handle ranges that start with - (like -1, -5)
        # which would otherwise be interpreted as options
        import re

        parts = arg_s.split()
        processed_parts = []
        i = 0
        while i < len(parts):
            part = parts[i]
            # Check if this looks like a code-before range (-N where N is a number)
            # or markdown range from start (-mN)
            if re.match(r"^-\d+$", part):
                # This is a range like -1, -5, not an option
                # Mark it specially so we can restore it after parse_options
                processed_parts.append(f"BEFORE{part[1:]}")
            elif re.match(r"^-m\d+$", part, re.IGNORECASE):
                # This is a range like -m3, not an option
                processed_parts.append(f"MDBEFORE{part[2:]}")
            elif part == "-f" and i + 1 < len(parts):
                # Keep -f and its argument together
                processed_parts.append(part)
                i += 1
                processed_parts.append(parts[i])
            elif part == "-v" and i + 1 < len(parts):
                # Keep -v and its argument together
                processed_parts.append(part)
                i += 1
                processed_parts.append(parts[i])
            else:
                processed_parts.append(part)
            i += 1

        processed_arg_s = " ".join(processed_parts)

        try:
            opts, args = self.parse_options(processed_arg_s, "v:f:", mode="list")
            # Restore the -N and -mN syntax in args
            restored_args = []
            for arg in args:
                if arg.startswith("BEFORE"):
                    restored_args.append("-" + arg[6:])  # BEFORE has 6 chars
                elif arg.startswith("MDBEFORE"):
                    restored_args.append("-m" + arg[8:])  # MDBEFORE has 8 chars
                else:
                    restored_args.append(arg)
            args = restored_args
        except UsageError as e:
            # Check if it's an unrecognized option error
            error_msg = str(e)
            if "not recognized" in error_msg:
                # Extract the bad option if possible
                import re

                match = re.search(r"option (\S+) not recognized", error_msg)
                if match:
                    bad_option = match.group(1)
                    raise UsageError(
                        f"Invalid option '{bad_option}'.\n"
                        f"Valid options for %md:\n"
                        f"  --list           Show all markdown cells with previews\n"
                        f"  -f filename      Specify notebook file\n"
                        f"  -v version       Notebook version (default: 4)\n"
                        f"Examples:\n"
                        f"  %md m1-m3 m5    Get markdown cells 1-3 and 5\n"
                        f"  %md -1 2-       Before code 1, after code 2\n"
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
                # Show with m-prefix and extra spacing for 3-digit numbers
                print(f"  m{idx:<3}: {preview}")
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
                "No ranges specified.\n"
                "Usage examples:\n"
                "  %md m1          # Get first markdown cell\n"
                "  %md m1-m3 m5    # Get cells 1-3 and 5\n"
                "  %md -1          # All markdown before code cell 1\n"
                "  %md 2-4         # All markdown between code cells 2 and 4\n"
                "  %md 8-          # All markdown after code cell 8\n"
                "  %md --list      # List all markdown cells\n"
                "See %md? for full documentation."
            )

        # Load notebook
        nb = nbformat.read(my_notebook_file, as_version=version)

        # Parse each range and collect markdown contents
        contents = []
        seen_content = set()  # To avoid duplicates

        for arg in args:
            try:
                range_contents = parse_md_range(arg, nb)
                for content in range_contents:
                    # Use hash to detect duplicates (same content)
                    content_hash = hash(content)
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        contents.append(content)
            except (ValueError, IndexError) as e:
                # Check if it's a markdown index that's out of range
                if "m" in arg.lower():
                    all_markdown = get_markdown_cells(nb)
                    total_md_cells = len(all_markdown)
                    raise UsageError(
                        f"Invalid markdown cell range '{arg}'.\n"
                        f"This notebook has {total_md_cells} markdown cell(s) (m1-m{total_md_cells}).\n"
                        f"Use '%md --list' to see all available markdown cells."
                    )
                else:
                    # Code cell reference issue
                    raise UsageError(
                        f"Invalid range '{arg}'.\n"
                        f"Check that the code cell numbers exist in the notebook.\n"
                        f"Syntax: -N (before code N), N- (after code N), N-M (between codes)\n"
                        f"Use '%code --list' to see code cells with their numbers."
                    )

        if not contents:
            all_markdown = get_markdown_cells(nb)
            if len(all_markdown) == 0:
                raise UsageError(
                    f"No markdown cells found in {my_notebook_file.name}.\n"
                    f"This notebook contains only code cells."
                )
            else:
                raise UsageError(
                    f"No markdown cells found for the specified ranges.\n"
                    f"Use '%md --list' to see available markdown cells."
                )
            return

        # Join contents without header comment for markdown
        contents = "\n\n".join(contents)

        self.shell.set_next_input(contents, replace=True)


# In order to actually use these magics, you must register them with a
# running IPython. See load_ipython_extension() in __init__.py.
