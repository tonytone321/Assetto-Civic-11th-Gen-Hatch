#!/usr/bin/env python3
"""Fetch a web page, optionally rendering JavaScript in headless Chromium.

Saves raw HTML and extracted visible text to cache/pages/ (git-ignored) and
prints the text (or a grep of it). Used by research threads so that every
recorded value is checked against the opened page, not a search snippet.

Headless Chromium trusts the egress proxy CA through the NSS store
(~/.pki/nssdb); scripts/setup_env.sh installs it. TLS verification is never disabled.

Usage:
  python3 scripts/fetch_page.py URL [--render] [--grep REGEX] [--context N] [--wait MS]
"""
import argparse
import hashlib
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache", "pages")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
CHROMIUM_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium",
]


def _chromium_path():
    for p in CHROMIUM_CANDIDATES:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return None


ROBOTS_AGENTS = ["Claude-User", "ClaudeBot", "anthropic-ai", "*"]


def robots_allowed(url):
    """Honor robots.txt for Anthropic agents and the wildcard agent.

    Returns (allowed, detail). If robots.txt cannot be read, the fetch is allowed
    (standard robots behaviour) and that is reported.
    """
    import urllib.robotparser
    from urllib.parse import urlsplit
    import requests
    parts = urlsplit(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    try:
        r = requests.get(robots_url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code >= 400:
            return True, f"robots.txt HTTP {r.status_code}"
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(r.text.splitlines())
        for agent in ROBOTS_AGENTS:
            if not rp.can_fetch(agent, url):
                return False, f"robots.txt disallows {agent}"
        return True, "robots.txt allows"
    except Exception as e:  # network error reading robots.txt
        return True, f"robots.txt unreadable ({type(e).__name__})"


def fetch_static(url, timeout=30):
    import requests
    r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "en-CA,en;q=0.9"},
                     timeout=timeout, allow_redirects=True)
    return r.status_code, r.url, r.text


def fetch_rendered(url, wait_ms=4000, timeout=60):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        kw = {"headless": True}
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if proxy:
            kw["proxy"] = {"server": proxy}
        exe = _chromium_path()
        if exe:
            kw["executable_path"] = exe
        browser = p.chromium.launch(**kw)
        ctx = browser.new_context(user_agent=UA, locale="en-CA",
                                  viewport={"width": 1440, "height": 2000})
        page = ctx.new_page()
        resp = page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
        page.wait_for_timeout(wait_ms)
        try:
            page.mouse.wheel(0, 20000)
            page.wait_for_timeout(1000)
        except Exception:
            pass
        html = page.content()
        text = page.inner_text("body")
        status = resp.status if resp else None
        final = page.url
        browser.close()
    return status, final, html, text


def html_to_text(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    text = soup.get_text("\n")
    return re.sub(r"\n\s*\n+", "\n", text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--grep")
    ap.add_argument("--context", type=int, default=150)
    ap.add_argument("--wait", type=int, default=4000)
    ap.add_argument("--max", type=int, default=20000, help="max chars of text to print")
    a = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(a.url.encode()).hexdigest()[:16]
    ok, detail = robots_allowed(a.url)
    if not ok:
        print(f"BLOCKED_BY_ROBOTS {a.url} ({detail}); not fetched")
        return 2
    if a.render:
        status, final, html, text = fetch_rendered(a.url, a.wait)
    else:
        status, final, html = fetch_static(a.url)
        text = html_to_text(html)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(CACHE, key + ".html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(CACHE, key + ".txt"), "w", encoding="utf-8") as f:
        f.write(f"URL: {a.url}\nFINAL: {final}\nSTATUS: {status}\nFETCHED: {stamp}\n\n{text}")
    print(f"STATUS {status} FINAL {final} FETCHED {stamp} CACHE cache/pages/{key}.txt chars={len(text)}")
    if a.grep:
        for m in re.finditer(a.grep, text, flags=re.I):
            s, e = max(0, m.start() - a.context), min(len(text), m.end() + a.context)
            print("---\n" + text[s:e].replace("\n", " | "))
    else:
        print(text[: a.max])


if __name__ == "__main__":
    sys.exit(main())
