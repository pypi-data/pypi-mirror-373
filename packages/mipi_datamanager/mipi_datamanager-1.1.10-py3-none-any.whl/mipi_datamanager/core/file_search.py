import os
from abc import abstractmethod, ABC
from pathlib import Path
from typing import List, Protocol, Type, Tuple, Dict, Literal, overload, Iterable
from functools import lru_cache
from .common import ensure_list, EnsureList
import pandas as pd
import re

# TODO optomize by only adding files to collection if they meet all filter criterial already
# TODO optomize using threadpool

def find_substrings_ci(text: str, needles: Iterable[str]) -> Tuple[str,...]:
    """
    Return every occurrence of any string in `needles`, case-insensitive,
    preserving the exact casing that appears in `text`.

    Works inside longer words:  "ApplePie" → "Apple"
    Ignores needles that are not present: "app" isn’t returned if it
    isn’t one of the needles.

    >>> doc = "APPLE pie APPle2 ApplePie banana bread app APPLER"
    >>> find_substrings_ci(doc, ["apple", "banana"])
    ['APPLE', 'APPle', 'Apple', 'banana']
    """
    # 1) keep each needle once, 2) search longer needles first
    needles_sorted = sorted(set(needles), key=len, reverse=True)

    # build one big pattern:  r'(apple|banana|cherry)'
    rx = re.compile("|".join(re.escape(n) for n in needles_sorted),
                    flags=re.IGNORECASE)

    return tuple(set(m.group(0) for m in rx.finditer(text)))


class File:
    __slots__ = ('path',)

    def __init__(self, path: Path | str):
        """
        One file on the disk. Provides access to the content and path attributes

        Args:
            path: Absolute or relative Path to the file
        """

        self.path = Path(path) #.resolve() TODO this line makes the code take forever. why?

    @lru_cache(maxsize=1024) # TODO make variable
    def read(self) -> str:
        with open(self.path, "r", encoding="utf-8", errors="replace") as file:
            content = file.read()
        return content

    def __repr__(self) -> str:
        return f"file object at: {self.path}"

    def __str__(self) -> str:
        return f"{self.path}"

    def __eq__(self, other) -> bool:
        return self.path == other.path

    def __hash__(self):
        return hash(self.path)

    @property
    def extension(self) -> str:
        return self.path.suffix


class FileCriteria:

    def __init__(self, content_includes: List[str] | None = None,
                 file_name_includes: List[str] | None = None,
                 extensions: List[str] | None = None):
        """
        Evaluates files based on a set of criteria. Evaluation rules are defined on installation then methods work
        on each file.

        Args:
            content_includes: substrings of intrest within the content of the file.
            file_name_includes: sibstrings to search for within the file names
            extensions: File extension to check for in the file name
        """
        self.content_includes = content_includes
        self.file_name_includes = file_name_includes
        self.extensions = extensions

    def check_extension_allowed(self, file: File) -> bool:
        """
        Returns:
            True if file extension is in the list of allowed extensions
        """
        if self.extensions == [] or self.extensions is None:
            return True
        return file.extension in self.extensions

    def check_content_substring_allowed(self, file: File) -> bool:
        """
        Returns:
            True if the file contains at least one of the allowed substrings
        """
        if self.content_includes == [] or self.content_includes is None:
            return True
        content = file.read()
        return len(find_substrings_ci(content, self.content_includes)) > 0

    def check_filename_allowed(self, file: File) -> bool:
        if self.file_name_includes == [] or self.file_name_includes is None:
            return True
        return any([n in file.path.name for n in self.file_name_includes])

    def get_content_includes_values_in_content(self, file: File) -> Tuple[str, ...]:
        """
        Returns:
            A tuple of strings which are contained in the file content
        """
        if self.content_includes is None:
            return tuple()
        content = file.read()
        return find_substrings_ci(content, self.content_includes)


class FileCollection(Protocol):

    def __init__(self, content_includes: List[str] | None = None,
                       file_name_includes: List[str] | None = None,
                       extensions: List[str] | None = None):
        """
        Handles the collection of files based on a set of criteria. Logic is defined by subclasses. The final list of
        files is stored in self.files.

        Args:
            content_includes: Substrings of intrest within the file content
            extensions: Extensions of intrest
        """
        ...

    def add(self, file: File) -> None:
        ...

    @property
    def files(self) -> List[File]:
        ...


class _FileCollection(ABC):
    def __init__(self):
        self._files = []

    @abstractmethod
    def add(self, file: File) -> None:
        raise NotImplementedError()

    @property
    def files(self) -> List[File]:
        return self._files


class _SearchFileCollection(_FileCollection):
    """
    base class for FileCollection object
    """

    def __init__(self, content_includes: List[str] | None = None,
                       file_name_includes: List[str] | None = None,
                       extensions: List[str] | None = None):
        super().__init__()
        self.content_includes = content_includes
        self.file_name_includes = file_name_includes
        self.extensions = extensions


class FilterFileCollection(_SearchFileCollection):
    def __init__(self, content_includes: List[str] | None = None,
                       file_name_includes: List[str] | None = None,
                       extensions: List[str] | None = None):
        """
        Collection of files filtered to only include those which have an appropriate extension and contain at lease one
        substring in the `content_includes`
        """
        _FileCollection.__init__(self)
        self.filter = FileCriteria(content_includes, file_name_includes, extensions)

    def add(self, file: File) -> None:
        if not self.filter.check_extension_allowed(file):
            return
        if not self.filter.check_filename_allowed(file):
            return
        if self.filter.check_content_substring_allowed(file):
            self._files.append(file)


class ContentSubstringFileCollection(_SearchFileCollection):
    """
    A collection of files filtered to only include those which have an appropriate extension. Files are NOT filtered by
    content substrings, instead, a tuple of strings contained in each file is provided.
    """

    def __init__(self, content_includes: List[str] | None = None,
                       file_name_includes: List[str] | None = None,
                       extensions: List[str] | None = None):
        _FileCollection.__init__(self)
        self.filter = FileCriteria(content_includes,file_name_includes, extensions)

    def add(self, file: File) -> None:
        if not self.filter.check_extension_allowed(file):
            return
        if not self.filter.check_filename_allowed(file):
            return
        self._files.append(
            (file, self.filter.get_content_includes_values_in_content(file))
        )


class Directory:
    """
    A single directory to search for files.
    """

    def __init__(self, path: Path):
        self.path = Path(path)

    def append_dir_contents_to_file_collection(self, file_collector: FileCollection) -> None:
        for root, dirs, files in os.walk(self.path):
            for file in files:
                f = File(os.path.join(root, file))
                file_collector.add(f)

    def __repr__(self) -> str:
        return f"directory object at: {self.path}"


class FileSearch:
    """
    Recursively search the file system for files based on their location, content, and extensions. The individual
    methods of this class determine how the results are filtered and formatted.

    Args:
        directories: Directories to search
        extensions: Extensions of to consider
        content_includes: Substrings of intrest within the file content

    """
    _content_includes = EnsureList()
    _file_name_includes = EnsureList()
    _extensions = EnsureList()

    def __init__(self, directories: List[str | Path] | str | Path,
                 *,
                 extensions: List[str] | str | None = None,
                 content_includes: List[str] | str | None = None,
                 file_name_includes: List[str] | str | None = None):


        self._directories = directories
        self._file_name_includes = file_name_includes
        self._extensions = extensions
        self._content_includes = content_includes
        self._files: FileCollection | None = None

    @property
    def _directories(self) -> List[Directory]:
        return self.__directories

    @_directories.setter
    def _directories(self, value):
        if value is None:
            raise ValueError("directories cannot be None")
        _value = ensure_list(value)
        self.__directories = []
        for d in _value:
            if not os.path.isdir(d):
                raise FileNotFoundError(d)
            self.__directories.append(Directory(d))
        self.__directories = [Directory(d) for d in _value]

    def _search(self) -> List[File]:
        for dir in self._directories:
            dir.append_dir_contents_to_file_collection(self._files)
        return self._files.files

    def _set_file_collector(self, file_collector: Type[_SearchFileCollection]) -> None:
        self._files = file_collector(self._content_includes, self._file_name_includes, self._extensions)

    def _file_contents_dict(self) -> Dict[File, Dict[str, bool]]:  # TODO use generics
        self._set_file_collector(ContentSubstringFileCollection)
        files = self._search()
        return {f[0]: {ss: ss in f[1] for ss in self._content_includes or []} for f in files}


    @overload
    def file_contents_dict(self, as_strings:Literal[True] = True) -> Dict[str, Dict[str, bool]]:
        ...

    @overload
    def file_contents_dict(self, as_strings:Literal[False] = True) ->Dict[File, Dict[str, bool]]:
        ...

    def file_contents_dict(self, as_strings:bool = True) -> Dict[str, Dict[str, bool]] | Dict[File, Dict[str, bool]]:
        """
        Filter based on extension, then return a dictionary which specifies the substrings contained within each file.

        Returns:
            A dictionary where each key is an absolute file path and each value is a dictionary of the contained substrings.

        !!! example
            ```python
            >>> fs = FileSearch("path/to/searh",
                             extensions = ".sql"
                             substrings = ["Table1", "Table2"]
            >>> fs.file_contents_dict()
            {
            "C:/file1.sql":{
                "Table1": False
                "Table2": True
                },
            "C:/subdir/file2.sql":{
                "Table1": True
                "Table2": False
                }
            }
            ```
        """
        if len(self._content_includes) == 0:
            raise RuntimeError("Can not use file_contents_dict method when target substrings are empty")

        if as_strings:
            return {str(k): v for k, v in self._file_contents_dict().items()}
        else:
            return {k: v for k, v in self._file_contents_dict().items()}

    def file_contents_dataframe(self, content_flags_as_int = False) -> pd.DataFrame:
        """
        Filter based on extension then return a dataframe of which substrings are contained within each file.

        Returns:
            A dataframe where each row is a file, and there is a column for the extension, as well as each substring

        !!! example
            ```python
            >>> fs = FileSearch("path/to/searh",
                             extensions = [".sql",".py"]
                             substrings = ["Table1", "Table2"]
            >>> fs.file_contents_dataframe()
            | file                | ext  | Table1 | Table2 |
            |---------------------|------|--------|--------|
            | C:/file1.sql        | .sql | False  | True  |
            | C:/subdir/file2.sql | .sql | True   | False |
            | C:/subdir/file3.py  | .py  | False  | False |
            ```
        """

        def cast_dict_vals_to_ints(dict_: dict) -> dict:
            return {k: {ki:int(vi) for ki,vi in v.items()} for k, v in dict_.items()}


        dict_ = self._file_contents_dict()
        if content_flags_as_int:
            dict_ = cast_dict_vals_to_ints(dict_)
        dict2 = {
            str(k): {
                "file": k.path.name,
                "ext": k.path.suffix,
                 **v
        }
            for k, v in dict_.items()
        }
        return pd.DataFrame.from_dict(dict2, orient="index")

    def filtered_files(self, as_strings:bool = True) -> tuple[str, ...] | tuple[File, ...]:
        """
        Filters to files which contain at least one of the substrings and one of the extensions.

        Args:
            as_strings: If true return string results, else return File objects. File objects contain useful methods
            like reading contents.

        Returns:
            A tuple of strings or File objects.

        !!! example
            ```python
            >>> fs = FileSearch("path/to/searh",
                             extensions = [".sql"]
                             substrings = ["Table1", "Table2"]
            >>> fs.file_contents_dataframe()
             (file object at C:/file1.sql, file object at C:/subdir/file2.sql)
            ```
        """

        self._set_file_collector(FilterFileCollection)
        res = self._search()
        if as_strings:
            return tuple(str(f) for f in res)
        else:
            return tuple(res)

    def filtered_file_contents_tuple(self, as_strings:bool = True) -> Tuple[Tuple[str | File, Tuple[str,...]],...]:
        """
        Filters to files which contain at least one of the substrings and one of the extensions.

        Args:
            as_strings: If true return string results, else return File objects. File objects contain useful methods
            like reading contents.

        Returns:
            A tuple of strings or File objects, and a tuple of their respectively contained substrings.

        !!! example
            ```python
            >>> fs = FileSearch("path/to/searh",
                             extensions = [".sql"]
                             content_includes = ["Table1", "Table2"]
            >>> fs.file_contents_dataframe()
             (
             (file object at C:/file1.sql,()),
             (file object at C:/subdir/file2.sql, ("Table1", "Table2")
             )
            ```
        """

        self._set_file_collector(ContentSubstringFileCollection)
        res = self._search()
        if as_strings:
            return tuple(tuple((str(f[0]),f[1])) for f in res)
        else:
            return tuple(res)