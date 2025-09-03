from pathlib import Path
import datetime as dt
from shutil import copy
from dataclasses import dataclass
import logging
from getpass import getuser

from click import command, option
from textual.widget import Widget
from textual.message import Message
from textual import on
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll, Vertical, Horizontal, VerticalGroup
from textual.reactive import reactive, Reactive
from textual import events
from textual.widgets import (
    Button, Footer, Header, Markdown, TabbedContent, TabPane, SelectionList, Input, TextArea, ListView, ListItem,
    Static, ContentSwitcher
)

from tkinter import filedialog, Tk

from mipi_datamanager.core.common import read_text_file
from mipi_datamanager.core.read_setup import SetupFileLoader, SetupFS
from mipi_datamanager import FileSearch

# V2
# TODO Absract
# TODO Files tab needs access to relative path
# TODO Custom widget multiple directories
# TODO loading screens
# TODO highlight searched words
# TODO Toggle case sensitivity
# TODO Toggle substring must be included vs substrings hilight only
# TODO set themes
# TODO check special caracters dont break content search
# TODO add MORE button with instructions and Set Live Path
# TODO optomize in python the write performance critical components in C
    # compile regex at a class level to avoid duplication
    # search file contents by chunk so you dont read the whole file if the key substring is in the first line
    # filter by extension BEFORE by substring
    # switch from os.walk to os.scandir or Path.itterdir
    # Parallelize across files using concurrent.futures.ThreadPoolExecutor if your disk can keep up.
    # C options Cython, C Extension, Aho-Corasick

def set_logger(test_mode, log_path):
    user = getuser()
    if test_mode:
        write_mode = "w"
        log_level = logging.DEBUG
    else:
        write_mode = "a"
        log_level = logging.INFO

    logging.basicConfig(
        filename=log_path,                   # log file in your CWD
        filemode=write_mode,                            # overwrite on each run
        level=log_level,                     # capture everything ≥ DEBUG
        format=f"%(asctime)s | [{user}] | %(levelname)-5s | %(name)s: | %(message)s",
    )
    global logger
    logger = logging.getLogger("mipi_utility_gui")
    return logger


@dataclass
class FilterPresets:
    """
    contents of mipi_setup.py converted to interface with the gui
    """
    setup = SetupFS(SetupFileLoader()).export_as_object()
    dirs = tuple((display_name, public_name, default_toggle) for i, (public_name, display_name, default_toggle) in enumerate(setup.search_directories))
    exts = tuple((ext, ext, default_toggle) for i, (ext, default_toggle) in enumerate(setup.search_extensions))
    cp_dests = {public_name.replace(" ","_").lower():path  for (path, public_name) in setup.copy_destinations}
    cp_bindings = [tuple((str(i+1), public_name.replace(" ","_").lower(), public_name)) for i, (path, public_name) in enumerate(setup.copy_destinations)]

    def __repr__(self):
        return (
            f"FilterPresets(\n"
            f"  setup={self.setup!r},\n"
            f"  dirs={self.dirs!r},\n"
            f"  exts={self.exts!r},\n"
            f"  cp_dests={self.cp_dests!r},\n"
            f"  cp_bindings={self.cp_bindings!r}\n"
            f")"
        )

def _ask_path(prompt: str) -> Path | None:
    """
    Open an external file selector window and return the selected path

    Args:
        prompt: prompt user action on the header of the file selector window.

    Returns: selected file/directory path

    """
    root = Tk()
    root.withdraw()
    path = filedialog.askdirectory(title=prompt)
    root.destroy()

    if not path:
        logging.debug(f"No file selected for prompt: {prompt}")
        return

    return Path(path)

class UserFilterRow(HorizontalGroup):
    """ A single user applied filter.
    A container containing the value and a delete button. Intended to be mounted to a Filter Container.
    """

    def __init__(self, value):
        self.value = value
        super().__init__()

    def on_button_pressed(self, event:Button.Pressed):
        """Remove this button"""
        self.remove()

    def compose(self) -> ComposeResult:
        yield Button(label="✕", id="remove")
        yield Static(self.value)

class BaseFilterContainer(Vertical):
    """Base Container to contain child UserFilterRows Must overwrite `_handle_submit`
        user filters are stored in inner VerticalScroll container"""
    def __init__(self, filter_name, input_widget:Widget):
        self.filter_name = filter_name
        self.input_widget = input_widget
        super().__init__(id = f"{filter_name}_filter_container")

    def compose(self) -> ComposeResult:
        yield self.input_widget
        yield VerticalScroll(id = f"{self.filter_name}_filters_vscroll")

    def _handle_submit(self, event) -> None:
        """
        overwrite with an `@on(event)` to specify what happens when an input is submitted
        """
        raise NotImplementedError

    @property
    def filter_values(self):
        """List of all user defined filters in the container derived from UserFilterRow objects within the container"""
        container = self.query_one(f"#{self.filter_name}_filters_vscroll", VerticalScroll)
        return [row.value for row in container.query(UserFilterRow)]

class FilterStrContainer(BaseFilterContainer):
    """
    Widget which contains all user entered STRING filters entered as free text
    """
    def __init__(self, filter_name):
        input_widget = Input(placeholder=f"Enter {filter_name}")
        super().__init__(filter_name, input_widget)

    @on(Input.Submitted)
    def _handle_submit(self, event: Input.Submitted):
        """Submit free text input value to filters"""
        container = self.query_one(f"#{self.filter_name}_filters_vscroll", VerticalScroll)
        container.mount(UserFilterRow(event.value))


class FilterDirContainer(BaseFilterContainer):
    """
    Widget which contains all user entered DIRECTORY filters entered using file picker
    """
    def __init__(self, filter_name):
        input_widget = Button("Add Directory", id="add_search_directory_btn")
        super().__init__(filter_name, input_widget)

    @on(Button.Pressed, "#add_search_directory_btn")
    def _handle_submit(self, event: Button.Pressed):
        """Open Directory picker and submit path to filters"""
        path = _ask_path("Choose live search destination")

        if not path:
            return  # user cancelled input entry # TODO change to TRY EXCEPT block

        container = self.query_one("#live_dirs_filters_vscroll",
                                   VerticalScroll)  # inner container of all user filters
        container.mount(UserFilterRow(str(path)))

# class DirectoryTreeFS(DirectoryTree):
#
#
#     # TODO Make faster by passing File objects directly to tree to leverage LRU cache
#     # TODO Make handle several directories
#
#     def __init__(self,*args,files:Tuple[File,...],**kwargs):
#         super().__init__(*args,**kwargs)
#         self.files = {f.path for f in files}
#         self._dirs = {anc for f in self.files for anc in f.parents[:-1]}
#         self._tree_nodes = list(self._dirs | self.files)
#
#     def filter_paths(self,paths: Iterable[Path]) -> Iterable[Path]:
#         tree_nodes = self._tree_nodes
#         return (p for p in paths if p in tree_nodes)

class ListViewPathsFS(ListView):

    """ListView of File objects which returned from the file search presented as absolute paths"""

    files = reactive(tuple(), recompose = True)

    def __init__(self,*args,files,**kwargs): # TODO do i need * args?
        self.set_reactive(ListViewPathsFS.files, files)
        super().__init__(*args, **kwargs)


    def compose(self) -> ComposeResult:
        if self.files:
            for f in self.files:
                yield ListItem(Static(str(f.path)))

# class ListViewFilesFS(ListView):
    """ListView of File objects which returned from the file search presented as relative paths"""

#     def __init__(self,*args,files:Tuple[File,...],**kwargs): # TODO do i need * args?
#         items = (
#             ListItem(Static(str(f.path.name)))
#             for f in files
#         )
#         super().__init__(*items, **kwargs)

class MenuButton(Button):
    """
    A button which functions like a menu item on a menu bar.
    Toggelable will change color and send a message to the menu bar Widget when selected
    """
    toggled = reactive(False)

    CLASSES = ["menu_toggled"]

    class Toggled(Message):
        def __init__(self,toggled: bool, id: str) -> None:
            self.toggled = toggled
            self.id = id
            super().__init__()

    def __init__(self, *args, id, toggled = False, **kwargs):
        super().__init__(*args, id = id, **kwargs)
        self.set_reactive(MenuButton.toggled, toggled)

    def set_toggled(self):
        self.toggled = True
        self.set_class(True,*self.CLASSES)

    def set_untoggled(self):
        self.toggled = False
        self.set_class(False,*self.CLASSES)

    def on_button_pressed(self, event: Button.Pressed):
        if self.toggled:
            self.set_untoggled()
        else:
            self.set_toggled()
        self.post_message(self.Toggled(self.toggled, self.id))

class FilterMenu(HorizontalGroup):
    """
    Filter meue functions as a menu bar container for MenuButtons.
    Ensures only one menu is selected at a time so it functions like a menu
    """
    selected = Reactive(None)

    def compose(self) -> ComposeResult:
        yield MenuButton("Filter Search Paths", id="nav_filter_dirs")
        yield MenuButton("Filter File Extensions", id="nav_filter_exts")
        yield MenuButton("Filter Content Includes", id="nav_filter_substrs")
        yield MenuButton("Filter File Names", id="nav_filter_file_names")

    @on(MenuButton.Toggled)
    def _handle_toggled(self, event: MenuButton.Toggled):
        self.selected = event.id

    def deselect(self, selected = None):
        """deselect the current option."""
        # TODO needs refactor. selected kwarg is inconsistant

        if selected is None:
            _selected = self.selected
        else:
            _selected = selected
        if not _selected:
            return
        old_btn = self.query_one(f"#{_selected}", MenuButton)
        old_btn.set_untoggled()

    def watch_selected(self, old_selected, new_selected):
        """deselect the old option whenever a new option is selected."""
        if old_selected is not None:
            self.deselect(old_selected)

class MainMenu(VerticalGroup):
    """
    Main menu bar containing all filters menues and app action buttons.
    """

    def __init__(self, preset_filters:FilterPresets):
        self.preset_filters = preset_filters
        super().__init__(id = "search_filters_cont")

    def compose(self):
        with HorizontalGroup():
            yield Button("Search...", id = "search")
            yield Button("Set Live Path", id = "set_live_path_btn")
            yield Button("Export Results", id="export_results_btn")
            yield FilterMenu()

class ResultsViewer(HorizontalGroup):
    """Results of the search. Contains the files returned list, and the display content window"""

    files = reactive(tuple())
    dir = reactive(tuple())

    def __init__(self, dir = None, files = None, **kwargs):
        super().__init__(**kwargs)
        if files is not None:
            self.set_reactive(ResultsViewer.files, files)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.dir!r}) - Parent: ({self.parent!r})"

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="files"):
                with TabbedContent():
                    # with TabPane("Tree"):
                    #     yield DirectoryTreeFS(self.dir[0], files=self.files, id="file_tree")
                    with TabPane("Paths"):
                        yield ListViewPathsFS(files=self.files, id="list_paths_tree").data_bind(ResultsViewer.files)
                    # with TabPane("Files"):
                    #     yield ListViewFilesFS(self.dir[0], files=self.files, id="list_files_tree")

            yield TextArea.code_editor("Select a file...",id="content_space", read_only=True)

    def update_results(self,dirs,files):
        self.dirs = dirs
        self.files = files

    # @on(DirectoryTreeFS.FileSelected)
    # def _when_file_tree_is_selected(self, event: DirectoryTreeFS.FileSelected) -> None:
    #     # 1. load the text
    #     content = event.path.read_text(encoding="utf-8")
    #
    #     # 2. figure out the language from the suffix (not .stem)
    #     ext = event.path.suffix.lower() # TODO change to suffixes and support .jinja.sql
    #     # map “py” → “python”, “sql” → “sql”, etc.
    #     lang = {".py": "python",
    #             ".sql": "sql"}.get(ext, "text")
    #     # 3. grab your custom TextArea and set it
    #     editor = self.query_one(TextArea)
    #     if lang:
    #         editor.language = lang
    #     editor.text = content

    @on(ListViewPathsFS.Selected)
    def _when_path_list_is_selected(self, event: ListViewPathsFS.Selected) -> None:
        """
        Action when a file object is selected within the FileList as absolute paths object (ListViewPathsFS)
        """

        item = event.item  # this is your ListItem
        label = item.query_one(Static)

        text = label.renderable
        full_path = Path(text)
        self.app.selected_file = full_path
        # Relative Paths
        # # now you can parse that back into a Path or File if you want:
        # relative = Path(text)
        # full_path = Path(dir_selected) / relative

        # 1. load the text
        content = full_path.read_text(encoding="utf-8")  # TODO Set encoding

        # 2. figure out the language from the suffix (not .stem)
        ext = full_path.suffix.lower()  # TODO change to suffixes and support .jinja.sql
        # map “py” → “python”, “sql” → “sql”, etc.
        lang = {".py": "python",
                ".sql": "sql"}.get(ext, None)

        # 3. grab your live TextArea and set it
        editor = self.query_one(TextArea)
        if lang:
            editor.language = lang
        editor.text = content

    # @on(ListViewFilesFS.Selected)
    # def _when_file_list_is_selected(self, event: ListViewFilesFS.Selected) -> None:
    #     item = event.item  # this is your ListItem
    #     label = item.query_one(Static)
    #
    #     text = label.renderable
    #
    #     # now you can parse that back into a Path or File if you want:
    #     relative = Path(text)
    #     full_path = Path(dir_selected) / relative
    #     self.selected_file = full_path
    #
    #     # 1. load the text
    #     content = full_path.read_text(encoding="utf-8")
    #
    #     # 2. figure out the language from the suffix (not .stem)
    #     ext = full_path.suffix.lower()  # TODO change to suffixes and support .jinja.sql
    #     # map “py” → “python”, “sql” → “sql”, etc.
    #     lang = {".py": "python",
    #             ".sql": "sql"}.get(ext, None)
    #
    #     # 3. grab your live TextArea and set it
    #     editor = self.query_one(TextArea)
    #     editor.text = content
    #     if lang:
    #         editor.language = lang


class MainContent(Vertical):

    """Main content that the user sees. Switches between Results, Instructions, and Filter criteria opened by filter menu"""


    def __init__(self,preset_filters):
        super().__init__()
        self.preset_filters = preset_filters
        self.switcher:ContentSwitcher | None = None

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial="instructions", id = "main_content_switcher") as cs:
            with VerticalScroll(id = "instructions"):
                yield Markdown(read_text_file(Path(__file__).parent / "file_search.md"))

            yield ResultsViewer(id = "results_viewer")

            with VerticalGroup(id = "dirs_container"):
                yield SelectionList[str](*self.preset_filters.dirs, id="selection_dirs")
                yield FilterDirContainer(filter_name="live_dirs")

            with VerticalGroup(id = "exts_container"):
                yield SelectionList(*self.preset_filters.exts, id = "selection_extensions")
                yield FilterStrContainer(filter_name="file_extensions") # TODO constrain with regex

            with VerticalGroup(id = "substrs_container"):
                yield FilterStrContainer(filter_name="content_includes")

            with VerticalGroup(id = "file_names_container"):
                yield FilterStrContainer(filter_name="file_names")

        self.switcher = cs

class FileSearchGui(App):
    """A Textual to search for files based on their contents"""
    CSS = """
       #files {
           width: 25%;
           min-width: 25;
           max-width: 40%;
       }

       Placeholder {
           width: 1fr;
           height: 1fr;
       }
    """

    CSS_PATH = "file_search.tcss"

    filter_presets = FilterPresets()
    BINDINGS = [
        ("0","set_live_path","Live Path"),
        *filter_presets.cp_bindings,
                ]

    file_content: reactive[str] = reactive("", always_update=True)
    selected_file: Path | None = None
    live_path = None
    fs = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info(f"Launching app with presets: {self.filter_presets}")

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""

        yield Header()
        with Vertical(id ="main_window"):
            yield MainMenu(FilterPresets())
            yield MainContent(self.filter_presets)
        yield Footer()

    def _set_live_path(self):
        """
        Set the live path which is used to export results, and copy files on upon option 0
        """
        path = _ask_path("Choose a Live path")
        if path:
            self.live_path = path
            logger.debug(f"Live Path set: {self.live_path}")

    @on(Button.Pressed, "#set_live_path_btn")
    def _on_set_live_path(self, event: Button.Pressed) -> None:
        """action to set live path on button press"""
        self._set_live_path()

    def on_key(self, event: events.Key) -> None:
        """
        Actions to copy a file upon numeric button press (0-9)
        """
        logger.debug(f"Running `on_key`: {event} with selected file: {self.selected_file}")
        key = event.key

        # ── handle 0 first ────────────────────────────────────────────────────
        if key == "0":
            # 1) no file selected → ignore
            if self.selected_file is None:
                return

            # 2) live folder not yet set → ask the user once
            if getattr(self, "live_path", None) is None:
                self._set_live_path()

            # 3) live folder already set → copy silently
            dst = self.live_path / self.selected_file.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                copy(self.selected_file, dst)
                logger.info(f"Copied {self.selected_file} → {dst}")
            except Exception as e:
                logger.exception(f"Copy failed: {e}")
            return

        # ── handle digits 1…N ─────────────────────────────────────────────────
        if not key.isdigit() or not self.selected_file:
            return

        idx = int(key) - 1
        if idx < 0 or idx >= len(self.filter_presets.cp_bindings):
            return

        _, dest_key, _ = self.filter_presets.cp_bindings[idx]
        dest_dir = self.filter_presets.cp_dests.get(dest_key)
        if not dest_dir:
            return

        dst = Path(dest_dir) / self.selected_file.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            copy(self.selected_file, dst)
            logger.info(f"Copied {self.selected_file} → {dst}")
        except Exception as e:
            logger.exception(f"Copy failed: {e}") # TODO make DRY


    @on(Button.Pressed, "#export_results_btn")
    def _export_results(self, event: Button.Pressed):
        """Action to save the results of a file search to the Live Path as a csv"""
        if self.live_path is None:
            try:
                self._set_live_path()
            except:
                return # if set path doesnt work, end function
        if self.fs is None or self.live_path is None:
            return # dont do anything if filesearchis none/live path nost successfully set been set.. # TODO change to files reactive element in Results Viewer

        df = self.fs.file_contents_dataframe(content_flags_as_int=True)
        filename = f"file_search_results_{str(dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))}.csv"
        out_path = self.live_path / filename
        df.to_csv(out_path , index=True)
        logger.info(f"exported results to {out_path}")

    @on(MenuButton.Toggled)
    def _handle_menu_toggled(self, message:MenuButton.Toggled):
        """Action to open a file menu in the main content window"""
        switcher = self.query_one("#main_content_switcher", ContentSwitcher)
        if message.toggled is True:
            pane_id = message.id.removeprefix("nav_filter_") + "_container"
            switcher.current = pane_id
        else:
            viewer = self.query_one("#results_viewer", ResultsViewer)
            if len(viewer.files) > 0:
                switcher.current = "results_viewer"
            else:
                switcher.current = "instructions"

    def on_button_pressed(self, event: Button.Pressed):

        """
        Execute the search on the current filters
        """

        if event.button.id != "search":
            return

        dirs_selection = self.app.query_one("#selection_dirs")
        dirs_container = self.app.query_one("#live_dirs_filter_container")
        dirs =dirs_container.filter_values + dirs_selection.selected

        exts_selection = self.app.query_one("#selection_extensions")
        exts_container = self.app.query_one("#file_extensions_filter_container")
        exts = exts_container.filter_values + exts_selection.selected

        content_includes_container = self.app.query_one("#content_includes_filter_container")
        content_includes = content_includes_container.filter_values

        file_names_container = self.app.query_one("#file_names_filter_container")
        file_names = file_names_container.filter_values

        logger.info(f"Performing File Search - dirs: {dirs} | exts: {exts} | content_includes: {content_includes} | file_names_includes: {file_names}")

        self.fs = FileSearch(dirs, extensions=exts, content_includes=content_includes, file_name_includes=file_names)
        self.res = self.fs.filtered_files(as_strings=False)

        container = self.app.query_one(ResultsViewer)
        container.update_results(dirs,self.res)

        switcher = self.query_one("#main_content_switcher", ContentSwitcher)
        switcher.current = "results_viewer"

        self.query_one(FilterMenu).deselect()

@command()
@option("--dev-mode",is_flag=True, help = "sets the script to development mode for detailed logs. WARNING DELETES LOGS EVERY SESSION")
@option("--log-path",default = None)
def main(dev_mode,log_path):
    _log_path = Path(log_path) if log_path else None
    set_logger(dev_mode, log_path)
    app = FileSearchGui()
    app.run()

if __name__ == "__main__":
    main()