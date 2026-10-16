# maherghalayini.com

Personal website and blog of Maher Ghalayini, EdD, LLM, MBA.

## How it's organized

- `content/pages/` holds the main content of each tab (Home, About, Leadership, Teaching, Speaking, Contact).
- `content/posts/` holds blog posts, one Markdown file each, named `YYYY-MM-DD-short-title.md`.
- `assets/` holds the stylesheet, script, favicon, and headshot.
- `build.py` assembles everything into `public/`, which is what Netlify publishes.

## Adding a blog post

1. Create `content/posts/YYYY-MM-DD-short-title.md` starting with:

   ```
   ---
   title: Post title
   date: YYYY-MM-DD
   tag: Leadership
   dek: One-line summary shown under the title.
   excerpt: Two-sentence summary shown in the post list.
   ---
   ```

   Add `draft: true` to keep a post off the live site.

2. Run `python3 build.py` (needs `pip install markdown`).
3. Commit and push. Netlify publishes the update automatically.
