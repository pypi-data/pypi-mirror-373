# help.py

def show_help():
    help_text = r"""
giget — Download GitHub directories / sub-directories / files

USAGE
  giget [flags] <github_repo_url> [-o <output_dir>]

SUPPORTED URL FORMATS
  • Repository root:
      https://github.com/<owner>/<repo>
      (downloads the repo root directory; branch defaults to 'master')

  • Subdirectory on a specific branch:
      https://github.com/<owner>/<repo>/tree/<branch>/<path/to/dir>
      (downloads only that directory)

  Notes:
    - If /tree/<branch>/ is omitted, giget assumes branch 'master'.
      For repos that use 'main', include it explicitly:
      https://github.com/<owner>/<repo>/tree/main/<path>
    - Trailing slashes are okay; giget trims them.

FLAGS
  -h, --help
      Show this help message and exit.

  -v, -V, --version
      Print giget version and exit.

  list
      Shows the structure of the folder
      Example : giget list <url>

  -o <path>
      Output directory to save downloads (default: current directory ".").
      Example: -o ./downloads

  -nf
      "No folders" (a.k.a. flat mode). Saves all files directly into the
      output directory without recreating the GitHub folder structure.
      If multiple files share the same filename, combine with --force
      or --rename to control collisions.

  --force
      Overwrite if a file/directory with the same name already exists
      at the destination. This applies to both normal mode and -nf.
      If both --force and --rename are supplied, --force takes precedence.

  --rename
      Do not overwrite existing files/directories. Instead, dynamically
      rename the new item as:
        <name>_1<ext>, <name>_2<ext>, ... (files)
        <dirname>_1, <dirname>_2, ... (directories)
      Only used when a naming conflict is detected and --force is not set.

BEHAVIOR ON CONFLICTS
  • Default (no --force / --rename):
      giget stops with an error if a target file/dir already exists and
      nothing is overwritten.

  • With --force:
      Existing files/dirs at the destination may be overwritten.

  • With --rename:
      New files/dirs are saved with a numeric suffix to avoid overwriting.

EXAMPLES
  # Download entire repo root (assumes branch 'master')
  giget https://github.com/user/repo

  # Download a subdirectory on the 'main' branch into ./downloads
  giget https://github.com/user/repo/tree/main/path/to/dir -o ./downloads

  # Flat mode (no folders): place all files directly in current directory
  giget -nf https://github.com/user/repo/tree/main/assets/images

  # Flat mode into a custom folder
  giget -nf https://github.com/user/repo/tree/main/assets/images -o ./img

  # Overwrite any existing files/dirs in the destination
  giget --force https://github.com/user/repo/tree/main/docs -o ./site-docs

  # Avoid overwriting by renaming new items
  giget --rename https://github.com/user/repo/tree/main/docs -o ./site-docs

  # Prints the Structure of the Folder
  giget list https://github.com/user/repo/tree/main/docs

  # Show version / help
  giget --version
  giget --help

NOTES
  • Branch selection is inferred from the URL (…/tree/<branch>/…).
    Without /tree/, giget defaults to 'master'.
  • If you frequently hit GitHub API rate limits (HTTP 403), consider
    running giget with a GITHUB_TOKEN environment variable for higher limits.
  • Exit status: 0 on success, 1 on error.

"""
    print(help_text)
