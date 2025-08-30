#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# synerty-peek documentation build configuration file

import os
import shutil
import sys

import sphinx
import sphinx_rtd_theme
from pytmpdir.directory_ import Directory
from sphinx.ext import apidoc


# Add the path to your project if needed
sys.path.insert(0, os.path.abspath("../"))

# Project information
project = "SynertyPeek-AdminDocs"
title = "Synerty Peek - Administration Documentation"
copyright = "2024, Synerty"
author = "Synerty"
version = '5.0.0'

# Extensions to use
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]

# Templates path
templates_path = ["_templates"]

# Source suffixes
source_suffix = ".rst"

# Master document
master_doc = "index"

# Exclude patterns
exclude_patterns = ["*Test.*", "_build", "Thumbs.db", ".DS_Store"]

# Pygments style for syntax highlighting
pygments_style = "sphinx"

# HTML theme options
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Static path for HTML
html_static_path = ["_static"]

# LaTeX documents (if needed)
latex_documents = [(master_doc, project + ".tex", title, author, "manual")]

# Manual page documents (if needed)
man_pages = [(master_doc, project, title, [author], 1)]

# Texinfo documents (if needed)
texinfo_documents = [
    (
        master_doc,
        project,
        title,
        author,
        project,
        "Enterprise Extensible Python Platform.",
        "Miscellaneous",
    )
]


###############################################################################
# Begin apidoc hack
###############################################################################


# Custom functions for apidoc
class _Opts:
    destdir = None
    suffix = "rst"
    dryrun = False
    force = False
    noheadings = False
    modulefirst = True
    separatemodules = False
    followlinks = False
    implicit_namespaces = False
    maxdepth = 10
    includeprivate = False
    append_syspath = True
    header = project


def makename(package, module):
    package = package or ""
    module = module or ""
    return package + "." + module if module else package


def format_heading(level, text):
    """Format a heading for reStructuredText."""
    text = text.replace(".", "-").strip("_")
    underlining = ["=", "-", "~", '"', "^"][level - 1]
    return f"{text}\n{underlining * len(text)}\n"


def format_directive(module, package):
    """Format a module directive for reStructuredText."""
    if module:
        full_name = f"{package}.{module}"
    else:
        full_name = package

    full_name = full_name.replace("..", ".")

    return (
        f".. automodule:: {full_name}\n"
        f"    :members:\n"
        f"    :undoc-members:\n"
        f"    :show-inheritance:\n"
    )


def _listFiles(dir):
    ignoreFiles = set(".lastHash")
    paths = []
    for path, directories, filenames in os.walk(dir):
        for filename in filenames:
            if filename in ignoreFiles:
                continue
            paths.append(os.path.join(path[len(dir) + 1 :], filename))

    return paths


def _fileCopier(src, dst):
    with open(src, "rb") as f:
        contents = f.read()

    # If the contents hasn't change, don't write it
    if os.path.isfile(dst):
        with open(dst, "rb") as f:
            if f.read() == contents:
                return

    with open(dst, "wb") as f:
        f.write(contents)


def _syncFiles(srcDir, dstDir):
    if not os.path.isdir(dstDir):
        os.makedirs(dstDir)

    # Create lists of files relative to the dstDir and srcDir
    existingFiles = set(_listFiles(dstDir))
    srcFiles = set(_listFiles(srcDir))

    for srcFile in srcFiles:
        srcFilePath = os.path.join(srcDir, srcFile)
        dstFilePath = os.path.join(dstDir, srcFile)

        dstFileDir = os.path.dirname(dstFilePath)
        os.makedirs(dstFileDir, exist_ok=True)
        _fileCopier(srcFilePath, dstFilePath)

    for obsoleteFile in existingFiles - srcFiles:
        obsoleteFile = os.path.join(dstDir, obsoleteFile)

        if os.path.islink(obsoleteFile):
            os.remove(obsoleteFile)

        elif os.path.isdir(obsoleteFile):
            shutil.rmtree(obsoleteFile)

        else:
            os.remove(obsoleteFile)


def shall_skip(filepath, opts):
    """Determine if a file should be skipped based on certain criteria."""
    # Example criterion: skip if file name starts with an underscore
    return os.path.basename(filepath).startswith("_")


def write_file(filename, text, opts):
    """Write the text to the specified file."""
    with open(
        os.path.join(opts.destdir, filename + "." + opts.suffix), "w"
    ) as f:
        f.write(text)


def create_module_file(package, module, opts):
    """Build the text of the file and write the file."""
    raise Exception("create_module_file shouldn't get called")


def create_package_file(
    root,
    master_package,
    subroot,
    py_files,
    opts,
    subs,
    is_namespace,
    excludes=[],
    *args,
    **kwargs,
):
    """Build the text of the file and write the file."""

    master_package = master_package or ""
    subroot = subroot or ""

    text = ".. _%s:\n\n" % makename(master_package, subroot)

    text += format_heading(1, "(P) %s" % subroot if subroot else master_package)
    text += format_directive(subroot, master_package)
    text += "\n"

    INITPY = "__init__.py"

    # build a list of directories that are szvpackages (contain an INITPY file)
    subs = [
        sub for sub in subs if os.path.isfile(os.path.join(root, sub, INITPY))
    ]
    # if there are some package directories, add a TOC for theses subpackages

    if subs:
        text += ".. toctree::\n\n"
        for sub in subs:
            text += "    %s.%s\n" % (makename(master_package, subroot), sub)
        text += "\n"

    submods = [
        os.path.splitext(sub)[0]
        for sub in py_files
        if not shall_skip(os.path.join(root, sub), opts) and sub != INITPY
    ]

    for submod in submods:
        text += format_heading(2, "(M) %s" % submod)
        text += format_directive(makename(subroot, submod), master_package)
        text += "\n"

    text += "\n"

    write_file(makename(master_package, subroot), text, opts)


def is_excluded(root, excludes):
    """Check if the directory is in the exclude list.

    Note: by having trailing slashes, we avoid common prefix issues, like
          e.g. an exlude "foo" also accidentally excluding "foobar".
    """

    fileName = os.path.basename(root)
    dirName = os.path.dirname(root)

    excludes = ["Test.py", "setup.py"]

    for exclude in excludes:
        if fileName.endswith(exclude):
            return True

    return False


# Overwrite the apidoc render methods with ours
sphinx.ext.apidoc.create_package_file = create_package_file
sphinx.ext.apidoc.create_module_file = create_module_file
sphinx.ext.apidoc.is_excluded = is_excluded


def createApiDocs(modFileName):
    moduleName = os.path.basename(os.path.dirname(modFileName))

    rootpath = os.path.abspath(os.path.dirname(modFileName))
    realDstDir = os.path.join(
        os.path.dirname(__file__), "doc_link", moduleName + "_api"
    )

    tmpDir = Directory()

    opts = _Opts()
    opts.destdir = tmpDir.path

    if not os.path.isdir(opts.destdir):
        os.makedirs(opts.destdir)

    # Generate the package documentation
    apidoc.main(
        [
            "-f",  # Overwrite existing files
            "-o",
            opts.destdir,  # Output directory
            "--no-toc",  # Don't create a table of contents file (modules.rst)
            rootpath,  # Root path of the package
        ]
    )

    # Incrementally update files
    _syncFiles(tmpDir.path, realDstDir)


###############################################################################
# End apidoc hack
###############################################################################

from peek_admin_doc.doc_link import plugin_api_conf

plugin_api_conf.load(createApiDocs)
