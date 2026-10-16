#!/usr/bin/env python3
"""Build maherghalayini.com into ./public.

Pages:  content/pages/*.html   (the inside of <main> for each tab)
Posts:  content/posts/YYYY-MM-DD-slug.md   (header block, then Markdown)
Assets: assets/   (copied to /assets/)

Run:  python3 build.py
"""
import datetime as dt
import html
import math
import re
import shutil
from email.utils import format_datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
OUT = ROOT / "public"

SITE = "https://maherghalayini.com"
NAME = "Maher Ghalayini"
DEFAULT_DESC = ("Maher Ghalayini, EdD, LLM, MBA. Higher education leader, educator, "
                "and course designer working across Ontario and New York.")
BLOG_DESC = "Notes on academic leadership, AI in higher education, and what helps students finish."
BYLINE = ("Maher Ghalayini is Vice President of Academic Affairs at SUNY Niagara "
          "and teaches accounting and management as an adjunct professor.")
FONTS = ("https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;"
         "1,400;1,500&family=Instrument+Sans:wght@400;500;600&display=swap")

TABS = [
    ("home", "Home", "/"),
    ("about", "About", "/about/"),
    ("leadership", "Leadership", "/leadership/"),
    ("teaching", "Teaching", "/teaching/"),
    ("speaking", "Speaking", "/speaking/"),
    ("blog", "Blog", "/blog/"),
    ("contact", "Contact", "/contact/"),
]

# (source file, output path, active tab, page title, meta description)
PAGES = [
    ("home.html", "/", "home", None, DEFAULT_DESC),
    ("about.html", "/about/", "about", "About",
     "Background, areas of focus, and credentials of Maher Ghalayini, EdD, LLM, MBA."),
    ("leadership.html", "/leadership/", "leadership", "Leadership",
     "Senior academic leadership roles at SUNY Niagara, St. Lawrence College, Georgian College, Sheridan College, and Corinthian Colleges."),
    ("teaching.html", "/teaching/", "teaching", "Teaching",
     "Teaching appointments and online course design through Pilos Learning."),
    ("speaking.html", "/speaking/", "speaking", "Speaking & Service",
     "Conference presentations, board service, and a speaker bio for event organizers."),
    ("contact.html", "/contact/", "contact", "Contact",
     "Get in touch with Maher Ghalayini about academic leadership, speaking, and partnerships."),
]


def esc(text):
    return html.escape(text, quote=True)


def nice_date(d):
    return f"{d:%B} {d.day}, {d.year}"


def layout(*, title, description, path, active, body, og_type="website"):
    full_title = NAME if not title else f"{title} | {NAME}"
    nav = []
    for key, label, href in TABS:
        current = ' aria-current="page"' if key == active else ""
        nav.append(f'        <li><a href="{href}"{current}>{label}</a></li>')
    nav = "\n".join(nav)
    year = dt.date.today().year
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/assets/headshot.png">
<meta name="twitter:card" content="summary">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{NAME}: Blog" href="/blog/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/styles.css">
<script src="/assets/site.js" defer></script>
</head>
<body>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="wordmark" href="/">
      <span class="wordmark-name">{NAME}</span>
      <span class="wordmark-post">EdD, LLM, MBA</span>
    </a>
    <nav class="tabs" aria-label="Main">
      <ul>
{nav}
      </ul>
    </nav>
  </div>
</header>

<main id="main">
{body}
</main>

<footer class="site-footer">
  <div class="wrap footer-inner">
    <span>© {year} {NAME}</span>
    <span class="footer-links"><a href="https://www.linkedin.com/in/maherghalayini" target="_blank" rel="noopener">LinkedIn</a><a href="/blog/feed.xml">RSS</a></span>
  </div>
</footer>
</body>
</html>
"""


# ---------- posts ----------

def parse_post(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path.name}: the post must start with a --- header block")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip()
    body_md = m.group(2).strip()
    name = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)", path.stem)
    date = dt.date.fromisoformat(meta.get("date") or (name.group(1) if name else ""))
    slug = meta.get("slug") or (name.group(2) if name else path.stem)
    words = len(re.findall(r"\w+", body_md))
    return {
        "title": meta["title"],
        "date": date,
        "slug": slug,
        "tag": meta.get("tag", ""),
        "dek": meta.get("dek", ""),
        "excerpt": meta.get("excerpt", ""),
        "draft": meta.get("draft", "").lower() in ("true", "yes"),
        "minutes": max(1, math.ceil(words / 230)),
        "html": markdown.markdown(body_md, extensions=["smarty"]),
    }


def post_url(post):
    return f"/blog/{post['slug']}/"


def post_meta(post):
    parts = [f'<time datetime="{post["date"].isoformat()}">{nice_date(post["date"])}</time>']
    if post["tag"]:
        parts.append(f"<span>{esc(post['tag'])}</span>")
    parts.append(f"<span>{post['minutes']} min read</span>")
    return f'<p class="post-meta">{"".join(parts)}</p>'


def post_card(post, *, tag="li", heading="h2"):
    url = post_url(post)
    return f"""<{tag} class="post">
  {post_meta(post)}
  <{heading} class="post-title"><a href="{url}">{esc(post['title'])}</a></{heading}>
  <p class="excerpt">{esc(post['excerpt'])}</p>
  <a class="read-more" href="{url}">Read post →</a>
</{tag}>"""


def latest_block(posts):
    if not posts:
        return ""
    return f"""<section class="latest" aria-labelledby="latest-h">
  <div class="wrap latest-inner">
    <div class="latest-head">
      <h2 class="label" id="latest-h">Latest from the blog</h2>
      <a class="text-link" href="/blog/">All posts →</a>
    </div>
    {post_card(posts[0], tag="div", heading="h3")}
  </div>
</section>"""


def blog_index(posts):
    if posts:
        items = "\n".join(post_card(p) for p in posts)
        listing = f'<ul class="posts">\n{items}\n</ul>'
    else:
        listing = '<p class="empty">The first posts are on their way.</p>'
    return f"""<div class="wrap page">
  <header class="page-head">
    <h1 class="page-title">Blog</h1>
    <p class="page-intro">{esc(BLOG_DESC)}</p>
    <p class="feed-link"><a href="/blog/feed.xml">Subscribe by RSS</a></p>
  </header>
  <div class="page-body">
    {listing}
  </div>
</div>"""


def post_page(post):
    dek = f'<p class="dek">{esc(post["dek"])}</p>' if post["dek"] else ""
    return f"""<div class="wrap">
  <article class="article article-wrap">
    <a class="back" href="/blog/">← All posts</a>
    <header class="article-head">
      {post_meta(post)}
      <h1>{esc(post['title'])}</h1>
      {dek}
    </header>
    <div class="article-body">
{post['html']}
    </div>
    <p class="byline">{esc(BYLINE)}</p>
  </article>
</div>"""


def feed(posts):
    items = []
    for p in posts[:20]:
        when = dt.datetime(p["date"].year, p["date"].month, p["date"].day, 12, tzinfo=dt.timezone.utc)
        url = SITE + post_url(p)
        items.append(f"""  <item>
    <title>{esc(p['title'])}</title>
    <link>{url}</link>
    <guid>{url}</guid>
    <pubDate>{format_datetime(when)}</pubDate>
    <description>{esc(p['excerpt'])}</description>
  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{NAME}</title>
  <link>{SITE}/blog/</link>
  <atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml"/>
  <description>{esc(BLOG_DESC)}</description>
  <language>en</language>
{chr(10).join(items)}
</channel>
</rss>
"""


# ---------- build ----------

def write(path, text):
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ASSETS, OUT / "assets")

    posts = [parse_post(p) for p in sorted((CONTENT / "posts").glob("*.md"))]
    posts = sorted((p for p in posts if not p["draft"]), key=lambda p: p["date"], reverse=True)

    urls = []
    for src, path, active, title, desc in PAGES:
        body = (CONTENT / "pages" / src).read_text(encoding="utf-8")
        body = body.replace("<!--LATEST-->", latest_block(posts))
        write(path, layout(title=title, description=desc, path=path, active=active, body=body))
        urls.append((path, None))

    write("/blog/", layout(title="Blog", description=BLOG_DESC, path="/blog/", active="blog",
                           body=blog_index(posts)))
    urls.append(("/blog/", posts[0]["date"] if posts else None))
    for p in posts:
        write(post_url(p), layout(title=p["title"], description=p["excerpt"] or BLOG_DESC,
                                  path=post_url(p), active="blog", body=post_page(p),
                                  og_type="article"))
        urls.append((post_url(p), p["date"]))
    write("/blog/feed.xml", feed(posts))

    not_found = (CONTENT / "pages" / "404.html").read_text(encoding="utf-8")
    write("/404.html", layout(title="Page not found", description=DEFAULT_DESC, path="/404.html",
                              active=None, body=not_found))

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, lastmod in urls:
        extra = f"<lastmod>{lastmod.isoformat()}</lastmod>" if lastmod else ""
        sitemap.append(f"  <url><loc>{SITE}{path}</loc>{extra}</url>")
    sitemap.append("</urlset>")
    write("/sitemap.xml", "\n".join(sitemap) + "\n")
    write("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    # Send every Canadian-domain visit to the main .com site (works for Git and drag-and-drop deploys).
    write("/_redirects",
          "https://maherghalayini.ca/*      https://maherghalayini.com/:splat  301!\n"
          "https://www.maherghalayini.ca/*  https://maherghalayini.com/:splat  301!\n")

    print(f"Built {len(PAGES) + 2 + len(posts)} pages and {len(posts)} post(s) into {OUT}")


if __name__ == "__main__":
    main()
