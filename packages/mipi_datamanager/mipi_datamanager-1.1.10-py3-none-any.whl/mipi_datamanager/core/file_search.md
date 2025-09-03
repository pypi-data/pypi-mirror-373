# MiPi FileSearch

## About
Search your file system for text files based on their location, name, extension, and content. Remember
to setup your prefrences in `mipi_setup.py`!

## Live Path
Set this using the `Set Live Path` button. It will persist within the session unless you change it again.
This determines where `Export Results` saves the results file and `(0) Live Path` binding copies individual files.

## Filters
Any Menu which starts with `Filter...` will set the criteria for the search. The search results uses `and` logic between filters. For example if you set filters for `extension: .sql & content_includes: UPPER`
all files must meet *BOTH* of those criteria.

### Registered (Filter Type)
There may be filters that you apply commonly but dont want to type out every single app session. You can register
parameters in `mipi_setup.py` and toggle, with check boxes, them within the search session. The syntax to register a parameter is shown
by filter, note that type hints are included. Ony some filters support this (shown below)

### Live (Filter Type)
You also may want a very specific filter only for a single search. Live filters are entered manually at the application
session. You don't have to set up anything here. Just open a filter and enter your live filter to use it! All filters support live filtering!

### Filter Search Paths (Filter Menu)

- OR logic
- Required
- Register syntax: `set_search_directories = [(path_to_directory: str, display_name: str, default_toggle_value: bool), ]

### Filter File Extensions (Filter Menu)

- OR logic
- Optional: Default include all extensions
- Register syntax: `set_search_extensions = [(.extension: str, default_toggle_value), ]

### Filter Content Includes (Filter Menu)
filter to by content to include one of the following substrings

- OR logic 
- Optional: Default no filter on content
- No Registered Filters
- Coming soon: 
   - Highlight substrings in output test
   - Toggle between filter on substring vs only highlight substring 

### Filter File Names (Filter Menu)

- OR logic 
- Optional: Default no filter on file name
- No Registered Filters


## Copy Files (Global Action)
You are likely using this to utilize one or more of the resulting files. This application has built in functionality copy files from
their source into a new location. You can do this by `selecting` a file on the results window (if using keyboard
selection you must press enter), then pressing a nuber on your keyboard which corresponds to a destination.

### Live Path (0)
(0) will always be your `Live Path`. If you have not selected one you will be prompted to do so.

### Registered Paths (1-9)
(1-9) can be registered in `mipi_setup.py` using the following syntax:

set_copy_destinations = [ (path/to/destination_dir: str, Display Name On App Footer) ]
