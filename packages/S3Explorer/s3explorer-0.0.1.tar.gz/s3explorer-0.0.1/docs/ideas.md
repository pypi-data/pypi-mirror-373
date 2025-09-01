# S3Explorer

![tui prototype](images/ui_proto.png)

## Command

### Explorer

Upload - Ctrl+U

Download - Ctrl+D

Copy/Paste (file/dir) - Ctrl+C/V

Mkdir - Ctrl+M

Search File/Path - Ctrl+F or / (as Vim)

Copy file/dir path - Ctrl+Shift+C

Bookmark - Ctrl+B

Select file/dir - Space

### Global

Panel Focus - Tab (Forward) Shift+Tab (Backward) or direct panel id (1, 2, 3, ...)

Quit - Ctrl+Q

Interaction - Enter

- File path textbox: go to path
- Bookmark: go to path
- explorer: got to dir, only on dir and nothing on file

## Functionnality

Color dir/file in the explorer depending on their type (dir, txt, xml). Look at the [mimetypes](https://docs.python.org/3/library/mimetypes.html) python module.
