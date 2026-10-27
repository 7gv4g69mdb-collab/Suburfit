"""Download each URL in doc_urls.txt; save PDFs as text (pdftotext) and web pages as plain text in docs/."""
import os, re, subprocess, urllib.request, html
HERE = os.path.dirname(__file__); OUT = os.path.join(HERE, "docs"); os.makedirs(OUT, exist_ok=True)
for url in open(os.path.join(HERE, "doc_urls.txt")):
    url = url.strip()
    if not url or url.startswith("#"): continue
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", url.split("://", 1)[1])[-120:]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (suburb-fit research)"})
        data = urllib.request.urlopen(req, timeout=90).read()
    except Exception as e:
        print("FAIL", url, e); continue
    if data[:4] == b"%PDF":
        p = os.path.join(OUT, "tmp.pdf"); open(p, "wb").write(data)
        subprocess.run(["pdftotext", "-layout", p, os.path.join(OUT, name + ".txt")], check=False); os.remove(p)
    else:
        t = re.sub(r"(?is)<(script|style).*?</\1>", " ", data.decode("utf-8", "ignore"))
        links = re.findall(r'href="([^"]+\.pdf[^"]*)"', t)
        t = html.unescape(re.sub(r"<[^>]+>", " ", t)); t = re.sub(r"[ \t]+", " ", t); t = re.sub(r"\n\s*\n+", "\n", t)
        open(os.path.join(OUT, name + ".txt"), "w").write(t + "\n\nPDF LINKS:\n" + "\n".join(links))
    print("OK", url, len(data))
