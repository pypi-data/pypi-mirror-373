# Spreadlinks - publish links from a spreadsheet

Given a spreadsheet of links to resources on the web, this Django app displays
the links with a simple navigation system using tags to narrow the list down
to resources with matching tags.

There are examples on [spreadsite.org][].

  [spreadsite.org]: https://spreadsite.org/


## How it Works

A **resource library** is a collection of links to resources on web sites (either
the same as this site or external sites). A library is defined by a directory
containing, at minimum, a spreadsheet with data about the links in it. Other,
optional, files may add more metadata to flesh out the definition.

Libraries are named after the directory. Libraries all live in a **root
directory**. For the sample app, the root is `resource-libraries` and the Fan
films library is in `resource-libraries/fanfilms`.

The `spreadlinks.views` package has two exports, `library_list` and `library_detail`.
They have one required argument, `root_dir`, which names the root directory.

The `library_detail` view shows a list of links. It has an additional required
argument, `library_name`, and two *optional* arguments:

- `page` is an integer, and gives the page number (for lists of more links than
  fit on a page), where the first page is numbered 1;
- `urlencoded_keywords` is a selection of keywords used to filter the list.

The keywords might look like `ingredient:Marmalade+ingredient:Bread`, assuming
the data includes a facet named `ingredient` with keywords including `Marmalade`
and `Bread`.

The sample templates in `spreadlinks/templates/spreadlinks` will generate links
with these arguments in automatically. These templates assume the views are
named `library_list` and `library_detail` in the URLconf.


## Data Format

At present the spreadsheet must be in comma-separated values form; this is just
because I have not bothered adding support for one of the Excel-parsing libraries
available for Python. The first row MUST be column headings. Each of the
subsequent rows specifies an entry in the library.

The meaning of the columns is inferred from the column heading. Column headings
are normalized to lower case and spaces replaced with underscores before
interpreting them. The following columns are significant:

- `title`: The title of the link. Should be one line long and be unique.
- `description`: A paragraph or two describing the link. Markdown format.
- `href` or `url`: The address of the resource being linked to.
- `image-url`: A picture to illustrate the item.
- `keywords` or `main_keywords`: Keywords in the Main facet (see below)
- `FACET_keywords`: Keywords in an additional facet (where FACET is
  replaced with the name of that facet).

At present other columns are ignored. (Probably they should be displayed as part
of the link description or something.)

Keywords are used to build a browseable drill-down navigation thingummy.
The navigator automatically hides keywords that would lead to no matches.

A **facet** is a collection of keywords that describe the resource in the same
way. You might use a secondary facet to
describe the resource type, or the intended audience, say. The navigator allows
the user to select keywords from separate facets independently.

The value of the keywords cells may contain multiple keywords. By default,
keywords are required to go one per line within the cell; this allows for
keywords to be normal phrases with spaces and punctuation.

## Metadata

Additional information about the library may be specified with a separate file
`METADATA.txt`. This contains one or more headings following the RFC-2822 format
of heading:value, followed by a blank line and then the description of the
library. The description uses Markdown format.

The following headers are understood:

- `Title`: A title for the library as a whole.
- `Keyword-Separator`: A character to use instead of newlines to separate
keywords in the data file.

If there is no `METADATA.txt`, or no title is specified, then it uses library name
(the same as the directory name).
