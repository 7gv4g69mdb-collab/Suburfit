import sys
SP=sys.argv[1]
src=open('/home/claude/suburb-fit/index.html').read()
jspdf=open(SP+'/jspdf-src/dist/jspdf.umd.min.js').read()
qr=open(SP+'/qrlib/qrcode.min.js').read()
src=src.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>','<script>'+jspdf.replace('</script','<\\/script')+'</script>')
src=src.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>','<script>'+qr.replace('</script','<\\/script')+'</script>')
shim=r'''<script>
/* Standalone mode: stands in for the Claude page features. Saved clients, branding and brokers are kept in this browser only; downloads use the browser. */
(function () {
  if (window.claude && window.claude.use) return;
  const KEY = "suburbfit-store";
  let store = {}; try { store = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {}
  const persist = () => { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} };
  const listeners = [];
  const notify = () => listeners.forEach(f => f());
  const snap = path => ({ exists: path in store, data: () => JSON.parse(JSON.stringify(store[path])) });
  const doc = path => ({ id: path.split("/").pop(), path,
    set: async d => { store[path] = JSON.parse(JSON.stringify(d)); persist(); notify(); },
    delete: async () => { delete store[path]; persist(); notify(); },
    get: async () => snap(path),
    onSnapshot: (n) => { const f = () => n(snap(path)); listeners.push(f); setTimeout(f, 0); return () => {}; } });
  const col = path => { let ord = null; const q = {
    where: () => q, limit: () => q, orderBy: (k, dir) => { ord = [k, dir]; return q; }, doc: id => doc(path + "/" + id),
    _docs: () => { let d = Object.keys(store).filter(k => k.startsWith(path + "/") && k.split("/").length === path.split("/").length + 1).map(k => ({ id: k.split("/").pop(), data: () => JSON.parse(JSON.stringify(store[k])) }));
      if (ord) d.sort((a, b) => ((a.data()[ord[0]] || 0) - (b.data()[ord[0]] || 0)) * (ord[1] === "desc" ? -1 : 1)); return d; },
    get: async () => ({ docs: q._docs() }),
    onSnapshot: (n) => { const f = () => n({ docs: q._docs() }); listeners.push(f); setTimeout(f, 0); return () => {}; } }; return q; };
  const downloads = { save: async ({ filename, data }) => {
    const blob = data instanceof Blob ? data : new Blob([data]);
    const url = URL.createObjectURL(blob), a = document.createElement("a");
    a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 30000); return { status: "saved" }; } };
  const user = { canEdit: () => true, isOwner: () => true };
  window.claude = { use: async name => name === "db" ? { doc, collection: col } : name === "downloads" ? downloads : name === "user" ? user : null };
  window.__standalone = true;
})();
</script>
'''
src=src.replace('<script>\n(function () {', shim+'<script>\n(function () {',1) if '<script>\n(function () {' in src else None
assert src
# Default the QR page link to wherever this file is hosted
src=src.replace('$("oaPage").value = $("oaPage").value || brand.pageUrl || "";','$("oaPage").value = $("oaPage").value || brand.pageUrl || (window.__standalone && /^https?:/.test(location.href) ? location.href.replace(/#.*$/, "") : "");')
src=src.replace("Saved clients are kept in this page's storage on claude.ai and only you and your editors can see them. Open the page in claude.ai as its owner to use them.","Saved clients are kept in this browser only.")
out='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<style>*,*::before,*::after{box-sizing:border-box}body{margin:0}</style>\n</head>\n<body>\n'+src+'\n</body>\n</html>\n'
open('index.html','w').write(out); print(len(out))
