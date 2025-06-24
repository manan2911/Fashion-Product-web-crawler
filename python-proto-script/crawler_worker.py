import aiohttp
import asyncio
import gzip
import io
import json
import re
import time
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import tldextract

# ─── CONFIG ─────────────────────────────────────────────────────────────────────
CONCURRENCY                   = 12
TIMEOUT                       = 15
USER_AGENT                    = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
}
MIN_SITEMAP_URLS_FOR_COMPLETE = 50
MAX_DEPTH                     = 3
MAX_VISITED                   = 2000

DOMAIN_PATTERNS = {
    "tatacliq.com":     [re.compile(r"/p-mp[0-9a-z]{9,}$")],
    "westside.com":     [re.compile(r"/products/[^/?#]+")],
    "nykaafashion.com": [re.compile(r"/p/[0-9]+$")],
    "virgio.com":       [re.compile(r"/products/[^/?#]+$")],
}

# ─── HELPERS ────────────────────────────────────────────────────────────────────
def get_domain(url: str) -> str:
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"

def is_product_url(url: str, domain: str) -> bool:
    path = urlparse(url).path
    return any(pat.search(path) for pat in DOMAIN_PATTERNS.get(domain, []))

async def fetch_bytes(session, url: str):
    print(f"[fetch_bytes] GET {url}")
    try:
        async with session.get(url, timeout=TIMEOUT, ssl=False) as r:
            data = await r.read()
            print(f"[fetch_bytes] ← {r.status}, {len(data)} bytes")
            return data if r.status == 200 else None
    except Exception as e:
        print(f"[fetch_bytes] ERROR {url}: {e}")
    return None

async def fetch_text(session, url: str):
    print(f"[fetch_text] GET {url}")
    try:
        async with session.get(url, timeout=TIMEOUT, ssl=False) as r:
            text = await r.text()
            print(f"[fetch_text] ← {r.status}, {len(text)} chars")
            if r.status == 200 and "text/html" in r.headers.get("Content-Type",""):
                return text
    except Exception as e:
        print(f"[fetch_text] ERROR {url}: {e}")
    return None

def decompress(data: bytes) -> bytes:
    if data[:2] == b'\x1f\x8b':
        print("[decompress] gzipped sitemap")
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as f:
            return f.read()
    return data

def parse_sitemap(raw: bytes) -> dict:
    """
    Parses a sitemap or sitemap-index.  
    Returns a dict with:
      - 'sitemaps': list of child-sitemap URLs
      - 'locs':     list of <loc> page URLs
    """
    xml = decompress(raw)
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        print(f"[parse_sitemap] XML error: {e}")
        return {"sitemaps": [], "locs": []}

    sitemaps = []
    locs     = []
    for elem in root:
        tag = elem.tag.split("}")[-1].lower()
        loc = elem.find("{*}loc")
        if loc is None or not loc.text:
            continue
        url = loc.text.strip()
        if tag == "sitemap":
            sitemaps.append(url)
        elif tag == "url":
            locs.append(url)
    print(f"[parse_sitemap] found {len(sitemaps)} child sitemaps, {len(locs)} URLs")
    return {"sitemaps": sitemaps, "locs": locs}

def discover_root_sitemaps(netloc: str, robots_txt: str) -> list[str]:
    found = set()
    # 1) any "Sitemap:" lines in robots.txt
    for line in robots_txt.splitlines():
        if line.lower().startswith("sitemap:"):
            found.add(line.split(":",1)[1].strip())
    # 2) common names
    base = f"https://{netloc}"
    for path in ("/sitemap.xml", "/sitemap_index.xml"):
        found.add(base + path)
    return list(found)

# ─── CRAWLER ─────────────────────────────────────────────────────────────────────
class Crawler:
    def __init__(self, start_url: str):
        self.start_url     = start_url.rstrip("/")
        p                  = urlparse(self.start_url)
        self.scheme        = p.scheme
        self.start_netloc  = p.netloc             # e.g. "www.nykaafashion.com"
        self.domain        = get_domain(self.start_url)
        self.products      = set()
        self.seen_sitemaps = set()
        self.visited       = set()

    async def harvest_sitemaps(self):
        print(f"[harvest_sitemaps] for {self.start_netloc} ({self.domain})")

        # Nykaa Fashion: normalize host and force V2 index
        host = self.start_netloc
        if "nykaafashion.com" in host:
            host = "www.nykaa.com"

        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector, headers=USER_AGENT) as sess:
            # fetch robots.txt
            robots_url = f"{self.scheme}://{host}/robots.txt"
            robots     = await fetch_text(sess, robots_url) or ""

            # initial sitemap queue
            queue = discover_root_sitemaps(host, robots)
            if self.domain == "nykaafashion.com":
                queue.append(f"{self.scheme}://{host}/sitemap-v2/sitemap-index.xml")

            # BFS through sitemaps
            while queue:
                sm = queue.pop(0)
                if sm in self.seen_sitemaps:
                    continue
                self.seen_sitemaps.add(sm)
                print(f"[harvest_sitemaps] fetch sitemap: {sm}")

                raw = await fetch_bytes(sess, sm)
                if not raw:
                    continue

                parsed = parse_sitemap(raw)
                # enqueue children
                queue.extend(parsed["sitemaps"])
                # collect product locs
                for url in parsed["locs"]:
                    if is_product_url(url, self.domain):
                        print(f"[harvest_sitemaps] 🚀 {url}")
                        self.products.add(url)

        print(f"[harvest_sitemaps] total products: {len(self.products)}")

    async def crawl_html(self, session, url: str, depth=0):
        if url in self.visited or depth > MAX_DEPTH or len(self.visited) >= MAX_VISITED:
            return
        print(f"[crawl_html] Depth {depth} → {url}")
        self.visited.add(url)

        html = await fetch_text(session, url)
        if not html:
            return

        if is_product_url(url, self.domain):
            print(f"[crawl_html] 🛒 {url}")
            self.products.add(url)

        soup = BeautifulSoup(html, "html.parser")
        tasks = []
        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"].split("#")[0])
            if urlparse(href).netloc == self.start_netloc and href not in self.visited:
                tasks.append(self.crawl_html(session, href, depth+1))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def run(self) -> list[str]:
        t0 = time.time()

        # 1) Sitemap harvest
        await self.harvest_sitemaps()

        # 2) HTML fallback if too few results
        if len(self.products) < MIN_SITEMAP_URLS_FOR_COMPLETE:
            print(f"[run] only {len(self.products)} found—falling back to HTML crawl")
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector, headers=USER_AGENT) as sess:
                await self.crawl_html(sess, self.start_url)

        elapsed = time.time() - t0
        print(f"[run] 🏁 Found {len(self.products)} products in {elapsed:.1f}s")
        return sorted(self.products)

# ─── ENTRY POINT ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python crawler_worker.py https://<domain>/")
        sys.exit(1)

    start = sys.argv[1]
    products = asyncio.run(Crawler(start).run())
    print(json.dumps({start: products}, indent=2))
