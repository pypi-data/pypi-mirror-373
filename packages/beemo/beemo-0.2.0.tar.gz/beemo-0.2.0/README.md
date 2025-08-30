# beemo

A Python-based static site generator to build my website [bennuttall.com](https://bennuttall.com)

## PyPI

- [beemo](https://pypi.org/project/beemo/)

## Content

Content and templates for my site are at
[github.com/bennuttall/web-content](https://github.com/bennuttall/web-content). If you wish to use
this project for your own website, this repo will be a useful reference.

## Features

- Content as markdown and/or HTML
- Pages
- Posts
- Tags
- Archives (index, years and months)
- XML sitemap
- Atom feed
- Custom Chameleon templates
- Custom CSS, JS and other static files

## Usage

Create content directories e.g. `posts`, `pages`, `static` and `templates`.

### Posts

Populate your `posts` directory with your blog posts. Each post must be in its own directory but can
be organised in any hierarchy e.g. by year, year/month or just flat. Post directories must contain a
`meta.yml` and an `index.md` and can contain images in an `images` directory, used within your post.

### Pages

Populate your `pages` directory with your pages. Each page must be in its own directory but can
be organised in any hierarchy e.g. by year, year/month or just flat. Post directories must contain a
`meta.yml` and an `index.md`.

### Static

Any files in your `static` directory will be copied into the site build root. Keep your CSS files
and such in this directory.

### Templates

Create Chameleon templates for your site in the `templates` directory. See the [Chameleon
docs](https://chameleon.readthedocs.io/en/latest/) for reference.

## Configuration

The Beemo config file is a YAML file specifying some basic config about your site build.

For example, here `pages_dir` and `posts_dir` are both specified, and the site will be built with
both pages and blog posts:

```yml
posts_dir: content/posts
pages_dir: content/pages
static_dir: static
templates_dir: templates
blog_root: blog
output_dir: www
```

If `pages_dir` is not specified, the site will be built without pages (i.e. blog only mode), e.g:

```yml
posts_dir: posts
static_dir: static
templates_dir: templates
output_dir: www
```

If `posts_dir` is not specified, the site will be built without pages (i.e. pages only mode), e.g:

```yml
pages_dir: pages
static_dir: static
templates_dir: templates
output_dir: www
```

If `posts_dir` is specified, this comes with archives, tag indexes and such which cannot currently
be disabled.

### Environment variables

The only environment variable required is `BEEMO_CONFIG` which must point to your site's config
file:

```
export BEEMO_CONFIG=config.yml
```

## Install

Install the latest release with:

```
pip install beemo
```

### Development

Create a virtual environment and run `make develop` to install the library and its dependencies.

This can be served locally with e.g. `python -m http.server -d www` and viewed at e.g.
`http://localhost:8000`.

### Build

Build your site by running the command `beemo` with the environment variable `BEEMO_CONFIG` set
pointing at a valid config file. It will build your site into your configured `output_dir`.

## Examples

- [bennuttall.com](https://bennuttall.com) ([repo](https://github.com/bennuttall/web-content))
- [blog.piwheels.org](https://blog.piwheels.org) ([repo](https://github.com/piwheels/blog))

## Licence

- [BSD-3-Clause](LICENSE.txt)