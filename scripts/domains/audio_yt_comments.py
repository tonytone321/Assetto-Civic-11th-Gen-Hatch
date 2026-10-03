#!/usr/bin/env python3
"""Read the TEXT of a YouTube watch page's comments, expanding reply threads.

Domain 10 (audio). Text only: no media is requested, downloaded or analyzed
(video playback is behind YouTube's bot wall in this sandbox and downloading is
contrary to YouTube's terms). Honors robots.txt via fetch_page.robots_allowed.
Output text is cached under cache/pages/ (git-ignored) like fetch_page.py.

Usage: python3 scripts/domains/audio_yt_comments.py VIDEO_ID [--scrolls N]
"""
import argparse
import hashlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import fetch_page as fp  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_id")
    ap.add_argument("--scrolls", type=int, default=12)
    a = ap.parse_args()
    url = f"https://www.youtube.com/watch?v={a.video_id}"
    ok, detail = fp.robots_allowed(url)
    print("robots:", detail)
    if not ok:
        return 2
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        kw = {"headless": True}
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if proxy:
            kw["proxy"] = {"server": proxy}
        exe = fp._chromium_path()
        if exe:
            kw["executable_path"] = exe
        browser = p.chromium.launch(**kw)
        ctx = browser.new_context(user_agent=fp.UA, locale="en-CA",
                                  viewport={"width": 1440, "height": 2000})
        page = ctx.new_page()
        # block media requests: we only read page text
        page.route("**/*", lambda r: r.abort() if r.request.resource_type in ("media",)
                   or "googlevideo.com" in r.request.url else r.continue_())
        page.goto(url, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(6000)
        for _ in range(a.scrolls):
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1200)
        # expand reply threads
        for _ in range(3):
            btns = page.locator("ytd-comment-replies-renderer #more-replies button")
            n = btns.count()
            for i in range(n):
                try:
                    btns.nth(i).click(timeout=2000)
                    page.wait_for_timeout(700)
                except Exception:
                    pass
            more = page.locator("ytd-continuation-item-renderer button")
            for i in range(more.count()):
                try:
                    more.nth(i).click(timeout=2000)
                    page.wait_for_timeout(900)
                except Exception:
                    pass
        page.wait_for_timeout(2000)
        try:
            text = page.inner_text("ytd-comments")
        except Exception:
            text = page.inner_text("body")
        browser.close()
    os.makedirs(fp.CACHE, exist_ok=True)
    h = hashlib.sha1(("comments:" + url).encode()).hexdigest()[:16]
    out = os.path.join(fp.CACHE, f"{h}.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\nKIND: comments with replies expanded\nFETCHED: "
                f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n\n{text}")
    print("cached:", os.path.relpath(out, fp.ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
