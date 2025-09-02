# Changelist Sort
Making Sorting Changelist Files Easy!

1. Changelist-Init
2. Changelist-Sort
3. Changelist-FOCI

**Note:** Add alias to your shell environment to maximize your efficiency.

## Project Sorting Configuration
To configure a changelist sorting patterns for your project:
1. Run: `cl-sort --generate_sort_xml` to create `.changelists/sort.xml`
2. Edit Changelist Sorting Patterns

### File Pattern Attributes
For each `<files />` tag, apply ONE of the following attributes:
- file_ext : Match the file extension of the file. Do not include the dot.
- first_dir : The first directory in the path. Use empty string to match root directory.
- filename_prefix : The filename startswith this prefix.
- filename_suffix : The filename endswith this prefix.
- path_start : The beginning of the parent directory path. It's usually better to exclude unnecessary slash characters. 
- path_end : The end of the parent directory path. It's usually better to exclude unnecessary slash characters. 

### Sorting Keys
The `key` attribute inside changelists is integrated directly with sorting. When defining your sorting configuration, prefer the `name` attribute, only use key when necessary.
- Sorting Keys are short, simple strings that identify a changelist.
- More than one Sorting Key can map to one Changelist.
- Every File pattern is associated with a Sorting Key.

## Sorting Modes
There are two built-in sorting modes in addition to the sorting configuration (sort.xml).
 - When sort.xml is provided, it takes precedence over the Module SortMode.
 - The SourceSet SortMode is activated by a flag, only if config not provided.

### Sorting By Module (default)
Files are sorted by the name of the top level directory they are located in.
- In Android-Gradle projects, each directory in the project root is a module, with a few exception cases.
- Often, projects contain support tools and frameworks in top level dirs.
  - These get their own changelist if not gitignored.

### Sorting By Source Set (Gradle, Android)
A specialized SortMode that splits Gradle Modules by their Source Sets.
 - Add the `-s` flag or `--sourceset-sort` to use this mode.
 - This mode is not compatible with SortXML Config.
   - It is a quick and useful default for Gradle projects (beyond the Module).

### Special Changelists & Directories
There are special Changelists, and special Directories that are handled differently.
- Build Updates Changelist
- Root Directory
- Gradle Directory

**Build Updates Changelist:**
This is a changelist that is used to collect all of the files that affect the project build.
This includes all files in the gradle directory, and any file that ends with the `.gradle` file extension. There are also Gradle files that end in `.properties`, which are also sorted into the **Build Updates** Changelist.

**Root Directory:**
The Root directory is special because the file paths are really short and do not contain a module name. Often, Root directory contains `.gradle` files which are sorted into the Build Updates Changelist. Any non-Gradle files in the Root directory are sorted into a special Changelist that may be called `Root` or `Project Root`.

**Gradle Directory:**
The Gradle Directory is a direct descendant of the Root directory, and may contain `toml`, `gradle`, or `properties` files. These are all sorted into the **Build Updates** Changelist.

### Module Names and Sorting Comparisons

**Changelist Names**
The name of the changelist must match the module, ignoring letter case and removing spaces.

Otherwise, a new Changelist will be created that matches the module name.
- Underscores are replaced with spaces.
- Each Word in the Name will start with an uppercase letter.

## Remove Empty Changelists
You can remove all empty changelists after a sort has completed by adding the `-r` flag, or `--remove-empty` argument.
