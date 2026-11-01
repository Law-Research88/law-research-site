# law-research.nl

Static website for Law & Research. Netlify publishes the `site/` folder (see `netlify.toml`).

- `site/`: the live website (HTML, CSS, JS, images). `.htaccess` is only for Apache hosting such as Strato; Netlify uses `_redirects` and `_headers`.
- `build/build.py`: generates the HTML pages (shared header and footer, news, structured data, sitemap). Run `python3 build/build.py site`.
- `build/news_extra.py`: the news items. Add new items here and rebuild. Each item gets its own page at `site/nieuws/<id>.html` (listed in the sitemap); the overview is `nieuws.html` and each area page shows the 2 newest items. An optional `published="YYYY-MM-DD"` sets the publication date in the structured data.

News items are published only after the owner approves them.
