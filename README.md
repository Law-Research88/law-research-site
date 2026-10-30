# law-research.nl

Static website for Law & Research. Netlify publishes the `site/` folder (see `netlify.toml`).

- `site/`: the live website (HTML, CSS, JS, images). `.htaccess` is only for Apache hosting such as Strato; Netlify uses `_redirects` and `_headers`.
- `build/build.py`: generates the HTML pages (shared header and footer, news, structured data, sitemap). Run `python3 build/build.py site`.
- `build/news_extra.py`: the news items. Add new items here and rebuild.

News items are published only after the owner approves them.
- `build/modellen.py`: own model documents and letters. Each has a `status`: `download` (Word file published in `site/modellen/`), `aanvraag` (listed, request form only, file not published) or `verborgen`. Rebuild after changing.
