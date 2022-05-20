# -*- coding: utf-8 -*-
import os
import re
import sys
from datetime import date
from recommonmark.transform import AutoStructify
from recommonmark.parser import CommonMarkParser
from sphinx_scylladb_theme.utils import multiversion_regex_builder

# -- General configuration ------------------------------------------------

sys.path.insert(0, os.path.abspath('../../'))

# Build documentation for the following tags and branches
TAGS = []
BRANCHES = ['master']
# Set the latest version.
LATEST_VERSION = 'master'
# Set which versions are not released yet.
UNSTABLE_VERSIONS = []
# Set which versions are deprecated
DEPRECATED_VERSIONS = ['']

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
    'sphinx.ext.extlinks',
    'sphinx_sitemap',
    'sphinx_scylladb_theme',
    'sphinx_multiversion',
    'breathe'
]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
autosectionlabel_prefix_document = True

# A list of warning types to suppress arbitrary warning messages.
suppress_warnings = ['ref.*']

# The encoding of source files.
#
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'contents'

# General information about the project.
project = 'Scylla C/C++ Driver Documentation'
copyright = str(date.today().year) + ', ScyllaDB. All rights reserved.'
author = u'Scylla Project Contributors'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for not found extension -------------------------------------------

# Template used to render the 404.html generated by this extension.
notfound_template =  '404.html'

# Prefix added to all the URLs generated in the 404 page.
notfound_urls_prefix = ''

# -- Options for redirect extension ---------------------------------------

# Read a YAML dictionary of redirections and generate an HTML file for each
redirects_file = "_utils/redirections.yaml"

# -- Options for multiversion extension ----------------------------------

# Whitelist pattern for tags
smv_tag_whitelist = multiversion_regex_builder(TAGS)
# Whitelist pattern for branches
smv_branch_whitelist = multiversion_regex_builder(BRANCHES)
# Defines which version is considered to be the latest stable version.
# Must be listed in smv_tag_whitelist or smv_branch_whitelist.
smv_latest_version = LATEST_VERSION
smv_rename_latest_version = ''
# Whitelist pattern for remotes (set to None to use local branches only)
smv_remote_whitelist = r'^origin$'
# Pattern for released versions
smv_released_pattern = r'^tags/.*$'
# Format for versioned output directories inside the build directory
smv_outputdir_format = '{ref.name}'

# -- Options for Doxygen (API Reference) ---------------------------------
breathe_projects = {
	'API': "../../doxygen/xml/"
}
breathe_default_project = 'API'
breathe_default_members = ('members', 'undoc-members')

# Autogenerate API reference
def _generate_structs(outdir, structs, project):	
    """Write structs docs in the designated outdir folder"""	
    for obj in structs:	
        with open(outdir + '/struct.' + obj + '.rst', 'w') as t_file:	
            t_file.write(obj + "\n" + "=" * len(obj) + "\n\n" + ".. doxygenstruct:: " + obj +" \n  :project: " + project)	

def _generate_doxygen_rst(xmldir, outdir):	
    """Autogenerate doxygen docs in the designated outdir folder"""	
    structs = []
    files = os.listdir(os.path.join(os.path.dirname(__file__), xmldir))
    for file_name in files:
        if 'struct' in file_name and '__' not in file_name:
            structs.append(file_name
            .replace('struct_', '')
            .replace('_', ' ')
            .replace('.xml','')
            .title()
            .replace(' ', ''))
    _generate_structs(outdir, structs, breathe_default_project)	

def generate_doxygen(app):
    DOXYGEN_XML_DIR = breathe_projects[breathe_default_project]
    _generate_doxygen_rst(DOXYGEN_XML_DIR, app.builder.srcdir + '/api')	

# -- Options for sitemap extension ---------------------------------------

sitemap_url_scheme = 'stable/{link}'

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_scylladb_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'conf_py_path': 'docs/source/',
    'default_branch': 'master',
    'github_repository': 'scylladb/cpp-driver',
    'github_issues_repository': 'scylladb/cpp-driver',
    'hide_edit_this_page_button': 'false',
    'versions_unstable': UNSTABLE_VERSIONS,
    'versions_deprecated': DEPRECATED_VERSIONS,
}

# If not None, a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
# The empty string is equivalent to '%b %d, %Y'.
#
html_last_updated_fmt = '%d %B %Y'

# Custom sidebar templates, maps document names to template names.
#
html_sidebars = {'**': ['side-nav.html']}

# Output file base name for HTML help builder.
htmlhelp_basename = 'ScyllaDocumentationdoc'

# URL which points to the root of the HTML documentation. 
html_baseurl = 'https://cpp-driver.docs.scylladb.com'

# Dictionary of values to pass into the template engine’s context for all pages
html_context = {'html_baseurl': html_baseurl}

def replace_relative_links(app, docname, source):
    result = source[0]
    for item in app.config.replacements:
        for key, value in item.items():
            result = re.sub(key, value, result)
    source[0] = result

# Initialize Sphinx
def setup(app):
    # Setup MarkDown
    app.add_source_parser(CommonMarkParser)
    app.add_config_value('recommonmark_config', {
        'enable_eval_rst': True,
        'enable_auto_toc_tree': False,
    }, True)
    app.add_transform(AutoStructify)

    # Workaround to replace DataStax links
    replacements = [
        {"http://datastax.github.io/cpp-driver/api/cassandra.h/": "https://cpp-driver.docs.scylladb.com/" + smv_latest_version + "/api"},
        {"http://datastax.github.io/cpp-driver": "https://cpp-driver.docs.scylladb.com/" + smv_latest_version},
        {"http://docs.datastax.com/en/developer/cpp-driver/latest": "https://cpp-driver.docs.scylladb.com/" + smv_latest_version},
    ]
    app.add_config_value('replacements', replacements, True)
    app.connect('source-read', replace_relative_links)
    
    # Autogenerate API Reference
    app.connect("builder-inited", generate_doxygen)	
