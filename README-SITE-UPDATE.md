# Website update and clean exports

This folder contains the website source and its required media. The uploaded
`rFCsite 4.zip` is unchanged. The returned update omits the repository database;
it does not rewrite the original Git history or update a remote repository.

## Mounting changes

- Added three small SVG diagrams: bare sensor axes with sticker/button/USB-C,
  the assembled mount with the same axes, and two strapped mounts relative to
  a squared blade (top and end views).
- Explained that RZ means rotation about Z: Z is perpendicular to the drive/bend
  plane. The sticker face is upward with the blade squared; +Y faces the handle.
- Corrected the exploded saddle drawing: snap lips face the housing, away from
  the shaft. Preserved the existing kit photos and other assembly drawings.
- Updated both standalone guides and their embedded copies in `index.html`.
- Kept the rest of the website and all active media.

Axis references were checked against the manufacturer’s WT9011DCL datasheet
(v23-0608, pages 9–10), linked from its
[official product page](https://witmotion-sensor.com/products/wt9011dcl-bluetooth5-0-compact-size-accelerometer-inclinometer-sensor),
and the supplied Ritmo kit photographs. The diagrams are technical schematics,
not dimensioned fabrication drawings.

## Why the original ZIP was large

The original ZIP was **252,763,006 bytes (252.76 MB)**. Its compressed contents
were divided approximately as follows (the ZIP directory adds a little overhead):

| Contents | Compressed bytes | Approximate size |
| --- | ---: | ---: |
| `.git` repository database and history | 203,547,718 | 203.55 MB |
| Current website files | 49,006,360 | 49.01 MB |
| macOS metadata | 9,558 | 0.01 MB |

Git history accounts for about **80.5% of the original download**. It contains
older versions of the movie, reports, pages with embedded images, and removed
archive pictures. There is also an unreachable Git blob containing an old
**54,098,104-byte ZIP archive**. This explains why zipping the entire checkout
reintroduced old large files that are absent from the current website.

The two largest current website files are still used:

| File | Uncompressed bytes | Used by |
| --- | ---: | --- |
| `assets/rowing-welcome.mp4` | 29,126,249 | Welcome page and the main site's Welcome panel |
| `example_workout.html` | 14,395,688 | Interactive example report links and embedded report views |

Both are retained. They have not been recompressed, shortened, or stripped of
report data. All current images, assembly drawings, screenshots, and the PDF
have references in the HTML, including the panels embedded in `index.html`.
No current media was classified as dead and deleted. Current website text is
preserved except for the requested additions and mounting corrections.

## Apply this update to your existing checkout

Unzip the download into a separate folder, then copy its contents into your
existing `rFCsite` checkout. Preserve the checkout's existing `.git` directory.
Do not replace the entire checkout with this export if you want to retain your
local Git history and remote configuration. This update does not require a
deletion of any current website asset.

Review the resulting changes with `git status` and `git diff`, then commit and
deploy through your usual process. No publishing or remote changes have been
performed by this update.

## Make future small ZIP exports

From this website folder, run:

```sh
python3 tools/package-site.py
```

Or choose a destination:

```sh
python3 tools/package-site.py ../rFCsite-update.zip
```

The helper exports the current files on disk, including changes not yet
committed. It excludes `.git`, old ZIP exports, macOS resource files, local R
command history, dependency folders, and common Python caches. It preserves
other dotfiles such as `.github`, `.nojekyll`, and site configuration, and keeps
`CNAME`. It retains all website text and required media.

For a committed snapshot, Git itself can also export without repository history:

```sh
git archive --format=zip --prefix=rFCsite/ -o ../rFCsite-committed.zip HEAD
```

That command includes only the selected commit, so commit the intended changes
first. Unlike the provided helper, it includes every tracked file in that
commit, including any archives accidentally tracked in the past.

## Git cleanup is separate from making a small export

Deleting a file in a new commit, or adding it to `.gitignore`, does **not** remove
older versions from Git history. The new ignore file helps prevent fresh ZIP
exports and machine files from being added accidentally; it does not untrack
files already committed.

Ordinary Git garbage collection can remove sufficiently old unreachable objects
and repack the repository, but it keeps content reachable from commits and
branches. Permanently removing selected old images or media revisions requires
a coordinated history rewrite, backup, and replacement of the remote history.
That was not necessary for this download and has not been performed. The
original history remains available, including historical text and words.

For routine sharing and deployment, exporting the current website without
`.git` is the simplest way to keep the download small without losing history.
