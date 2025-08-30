import json
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

import yaml
from chameleon import PageTemplateLoader
from structlog import get_logger

from .post_types import Page, Post
from .settings import get_config
from .utils import prev_current_next


logger = get_logger()


class TheScribe:
    def __init__(self):
        self.now = datetime.now(timezone.utc)
        self.config = get_config()
        self.output_path = self.config.output_dir
        self.templates = PageTemplateLoader(
            search_path=[self.config.templates_dir],
            default_extension=".pt",
        )
        self.pages = list(self.iter_pages())
        self.posts = sorted(self.iter_posts(), key=lambda p: p.published)
        self.tags = self.get_tags()

    def setup_output_path(self):
        logger.info("Setting up output path", output_path=str(self.output_path))
        shutil.rmtree(self.output_path, ignore_errors=True)
        self.output_path.mkdir()
        for source_path in self.config.static_dir.iterdir():
            if source_path.is_file():
                with open(source_path, "rb") as source:
                    f = self.output_path / source_path.name
                    with open(f, "wb") as dest:
                        logger.info("Copying static file", src=str(source_path), dest=str(f))
                        shutil.copyfileobj(source, dest)

    def iter_pages(self) -> Generator[Page, None, None]:
        if not self.config.pages_dir:
            return
        for page_dir in self.config.pages_dir.iterdir():
            if page_dir.stem != "home":
                page_data = self.parse_content(page_dir)
                yield validate_page(page_data, src_dir=page_dir)

    def iter_posts(self) -> Generator[Post, None, None]:
        if not self.config.posts_dir:
            return
        for year_dir in self.config.posts_dir.iterdir():
            for post_dir in year_dir.iterdir():
                post_data = self.parse_content(post_dir)
                yield validate_post(post_data, src_dir=post_dir)

    def parse_content(self, src_dir: Path) -> dict[str]:
        metadata_file = src_dir / "meta.yml"
        content_file = src_dir / "index.md"
        images_dir = src_dir / "images"

        metadata = yaml.safe_load(metadata_file.read_text(encoding="utf-8"))
        content = content_file.read_text(encoding="utf-8")
        if images_dir.exists() and images_dir.is_dir():
            images = [img for img in images_dir.iterdir() if img.is_file()]
        else:
            images = []

        return {"content": content, "images": images, **metadata}

    def get_tags(self) -> dict[str, list[Post]]:
        tags = defaultdict(list)
        for post in reversed(self.posts):
            for tag in post.tags:
                tags[tag].append(post)
        return dict(sorted(tags.items(), key=lambda item: len(item[1]), reverse=True))

    def get_homepage(self) -> Page:
        homepage_dir = self.config.pages_dir / "home"
        page_data = self.parse_content(homepage_dir)
        return validate_page(page_data, src_dir=homepage_dir)

    def get_archive(self) -> dict[int, list[Post]]:
        archive = defaultdict(list)

        for post in reversed(self.posts):
            year = post.published.year
            archive[year].append(post)

        return dict(archive)

    def write_homepage(self):
        logger.info("Writing homepage")
        homepage = self.get_homepage()
        html = self.templates["home"](
            layout=self.templates["layout"]["layout"],
            page=homepage,
            posts=reversed(self.posts[-5:]),
            now=self.now,
        )
        output_path = self.output_path / "index.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)

    def write_pages(self):
        logger.info("Writing pages", len=len(self.pages))
        for page in self.pages:
            logger.info("Writing page", output_path=str(page.output_path))
            page.output_path.mkdir(parents=True, exist_ok=True)
            html = self.templates["page"](
                layout=self.templates["layout"]["layout"],
                page=page,
                now=self.now,
            )
            html_path = page.output_path / "index.html"
            html_path.write_text(html)

    def write_posts(self):
        logger.info("Writing posts", len=len(self.posts))
        for prev_post, post, next_post in prev_current_next(self.posts):
            logger.info("Writing post", output_path=str(post.output_path))
            post.output_path.mkdir(parents=True, exist_ok=True)
            html = self.templates["post"](
                layout=self.templates["layout"]["layout"],
                post=post,
                prev_post=prev_post,
                next_post=next_post,
                now=self.now,
            )
            html_path = post.output_path / "index.html"
            html_path.write_text(html)
            if post.images:
                img_dir = post.output_path / "images"
                img_dir.mkdir(parents=True, exist_ok=True)
                for img in post.images:
                    img_dest = img_dir / img.name
                    shutil.copy(img, img_dest)
                    logger.info("Copied image", path=str(img_dest))

    def write_blog_index(self):
        link = self.config.blog_root
        logger.info("Writing blog index", link=str(link))
        html = self.templates["posts"](
            layout=self.templates["layout"]["layout"],
            title="Blog",
            link=link,
            posts=reversed(self.posts),
            now=self.now,
        )
        output_path = self.output_path / link / "index.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)

    def write_year_indexes(self):
        logger.info("Writing year indexes")
        years = defaultdict(list)
        for post in self.posts:
            year = post.published.strftime("%Y")
            years[year].append(post)
        for year, posts in years.items():
            link = self.config.blog_root / year
            logger.info("Writing year index", year=year, post_count=len(posts), link=str(link))
            html = self.templates["posts"](
                layout=self.templates["layout"]["layout"],
                title=f"Archive: {year}",
                link=link,
                posts=reversed(posts),
                now=self.now,
            )
            output_path = self.output_path / link / "index.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html)

    def write_month_indexes(self):
        logger.info("Writing month indexes")
        months = defaultdict(list)
        for post in self.posts:
            year = post.published.strftime("%Y")
            month = post.published.strftime("%m")
            month_name = post.published.strftime("%B")
            months[(year, month, month_name)].append(post)
        for (year, month, month_name), posts in months.items():
            link = self.config.blog_root / year / month
            logger.info(
                "Writing month index", year=year, month=month, post_count=len(posts), link=str(link)
            )
            html = self.templates["posts"](
                layout=self.templates["layout"]["layout"],
                title=f"Archive: {month_name} {year}",
                link=link,
                posts=reversed(posts),
                now=self.now,
            )
            output_path = self.output_path / link / "index.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html)

    def write_tags_index(self):
        link = self.config.blog_root / "tags"
        logger.info("Writing tags index", len=len(self.tags), link=str(link))
        html = self.templates["tags"](
            layout=self.templates["layout"]["layout"],
            title="Tags",
            link=link,
            tags=self.tags,
            now=self.now,
        )
        output_path = self.output_path / link / "index.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)

    def write_tag_pages(self):
        logger.info("Writing tag pages", len=len(self.tags))
        for tag, posts in self.tags.items():
            link = self.config.blog_root / "tags" / tag
            logger.info("Writing tag page", tag=tag, post_count=len(posts), link=str(link))
            tag_str = tag.replace("-", " ")
            html = self.templates["posts"](
                layout=self.templates["layout"]["layout"],
                title=f"Tag: {tag_str}",
                link=link,
                posts=posts,
                now=self.now,
            )
            output_path = self.output_path / link / "index.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html)

    def write_archive_page(self):
        link = self.config.blog_root / "archive"
        logger.info("Writing archive page")
        archive = self.get_archive()
        html = self.templates["archive"](
            layout=self.templates["layout"]["layout"],
            title="Blog archive",
            link=link,
            archive=archive,
            now=self.now,
        )
        output_path = self.output_path / link / "index.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)

    def write_sitemap(self):
        logger.info("Writing sitemap")
        years = {post.published.year for post in self.posts}
        months = {(post.published.year, post.published.strftime("%m")) for post in self.posts}
        html = self.templates["sitemap"](
            pages=[page for page in self.pages if page.slug != "404"],
            posts=self.posts,
            tags=list(self.tags),
            years=years,
            months=months,
            now=self.now,
        )
        output_path = self.output_path / "sitemap.xml"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)

    def write_atom_feed(self):
        logger.info("Writing Atom feed")
        html = self.templates["atom"](
            title="Blog",
            posts=reversed(self.posts[-10:]),
            now=self.now,
        )
        output_path = self.output_path / self.config.blog_root / "atom.xml"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)

    def write_json(self):
        logger.info("Writing json")
        data = {
            "posts": [
                {
                    "title": post.title,
                    "link": str(post.link),
                    "published": post.published.isoformat(),
                }
                for post in reversed(self.posts)
            ],
        }
        output_path = self.output_path / "posts.json"
        output_path.write_text(json.dumps(data, indent=4))

    def build_site(self):
        logger.info("Starting build process", output_dir=str(self.output_path))

        self.setup_output_path()
        if self.config.pages_dir is not None:
            self.write_homepage()
            self.write_pages()
        if self.config.posts_dir is not None:
            self.write_posts()
            self.write_blog_index()
            self.write_year_indexes()
            self.write_month_indexes()
            self.write_tags_index()
            self.write_tag_pages()
            self.write_archive_page()
            self.write_atom_feed()
            self.write_json()
        self.write_sitemap()


def validate_post(post_data: dict[str], src_dir: Path) -> Post:
    try:
        return Post.model_validate(post_data)
    except Exception as exc:
        logger.error("Failed to validate post", src_dir=str(src_dir))
        print(exc)
        sys.exit(1)


def validate_page(page_data: dict[str], src_dir: Path) -> Page:
    try:
        return Page.model_validate(page_data)
    except Exception as exc:
        logger.error("Failed to validate page", src_dir=str(src_dir))
        print(exc)
        sys.exit(1)


def main():
    scribe = TheScribe()
    scribe.build_site()
