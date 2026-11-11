### Setup and regeneration

Run these commands from the repository root. The generator needs uv and
Python 3.9+. Git supplies commit dates. Gum supplies the optional terminal animation.
The Python generator uses only the standard library.

```sh
chmod +x do/readme
./do/readme
./do/readme --check
```

The first run builds README.md. The check exits 0 when it is current, 1 when
missing or stale, and 2 for a generator error. In a terminal with Gum installed,
the wrapper shows a spinner and then the command output. Without Gum, or when
output is redirected, it prints a plain progress message. No artificial delay
is added. Arguments pass through to the generator.

The wrapper resolves the repository from its own location, so it also works
when called from elsewhere. To bypass the wrapper:

```sh
uv run --script do/readme.py
```

### Update a section

1. Edit the appropriate source document below.
2. Run `./do/readme`.
3. Review the generated README and commit it with the edited source.

| What to change | Source, relative to the repository root |
| :-- | :-- |
| Title, introduction, decorative symbols | docs/readme/intro.md |
| Favorites, descriptions, recorded demos | docs/readme/highlights.md |
| Public installation instructions | docs/readme/install.md |
| Section order, headings, collapsible blocks | docs/readme/template.md |
| Setup and operator procedures | docs/maintainer.md |
| Statistics and generated catalog | do/readme.py |

For a new favorite, copy an existing subsection in highlights.md and change
its heading, description, and source link. Use `bin/NAME` for source links:
they resolve from the generated README at the repository root. Wrap optional
demos in a details block, following the existing examples.

To reorder sections, move their headings and `{{slot}}` markers together in
template.md. Available slots are intro, highlights, install, stats, catalog,
and maintainer. Adding an entirely new source document also requires adding
its mapping to the generator's render function.

### Packaging and publication

These procedures remain work in progress. The commands below deliberately
do nothing beyond printing a reminder.

| Task | Placeholder command |
| :-- | :-- |
| Install collection | `echo 'TODO: install scripts'` |
| Update collection | `echo 'TODO: update scripts'` |
| Stage executables | `echo 'TODO: stage bin/ with pkg'` |
| Build packages | `echo 'TODO: build packages'` |
| Publish | `echo 'TODO: publish packages'` |

### Keep the root clean

README.md is the only root document. Its source documents live under docs/.
Repository maintenance commands live under do/; public commands live under bin/.
Only bin/ belongs on PATH.

After applying this update, remove SETUP.md and the old preview/ directory:
setup is included here, and generation now uses the actual bin/ directory.
The generator no longer accepts --inventory.

Keep pkg and stage until the packaging workflow confirms whether it references
them. Their contents and consumers have not been inspected. Do not delete
package state as part of documentation cleanup.

### How the numbers work

No script headers are required and no public script is executed. Counts cover
regular, non-hidden files directly in bin/; symlinks are excluded. The largest
file is measured in bytes; source lines include comments and blank lines.
Interpreter detection uses the shebang.

Recently committed lists the latest commit touching each current path, in UTC.
Without history, dates remain unavailable; shallow history can be incomplete.
Working-tree edits affect sizes and lines but not commit dates. The --check
option compares generated Markdown, not every source byte.
