/* Law & Research: pro forma bezwaarschrift invullen en downloaden als Word (.docx) of PDF.
   Alles gebeurt in de browser: er worden geen gegevens verstuurd of opgeslagen. */
(function () {
  "use strict";
  var form = document.getElementById("bezwaar-form");
  if (!form) return;
  var preview = document.getElementById("bezwaar-preview");
  var status = document.getElementById("bezwaar-status");
  var MONTHS = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"];

  var val = function (name) { var el = form.elements[name]; return el ? (el.type === "checkbox" ? el.checked : el.value.trim()) : ""; };
  var nlDate = function (iso) {
    if (!iso) return "";
    var p = iso.split("-");
    return parseInt(p[2], 10) + " " + MONTHS[parseInt(p[1], 10) - 1] + " " + p[0];
  };
  var pad = function (n) { return (n < 10 ? "0" : "") + n; };
  var today = new Date();
  if (!form.elements.datum.value) form.elements.datum.value = today.getFullYear() + "-" + pad(today.getMonth() + 1) + "-" + pad(today.getDate());

  /* Lege verplichte velden tonen in het voorbeeld als [omschrijving] */
  var ph = function (name, label) { return val(name) || "[" + label + "]"; };
  var phDate = function (name, label) { return nlDate(val(name)) || "[" + label + "]"; };

  /* De brief als lijst van regels; {b: true} = vet, "" = lege regel */
  function letter() {
    var L = [];
    var add = function (t, b) { L.push({ t: t, b: !!b }); };
    add(ph("naam", "uw naam")); add(ph("adres", "straat en huisnummer")); add(ph("postcode_plaats", "postcode en woonplaats"));
    if (val("contact")) add(val("contact"));
    add("");
    add(ph("ontvanger", "naam van de instantie")); add(ph("ontvanger_adres", "adres van de instantie"));
    add("");
    add(ph("plaats", "plaats") + ", " + phDate("datum", "datum"));
    add("");
    add("Betreft: pro forma bezwaarschrift tegen uw besluit van " + phDate("besluit_datum", "datum besluit") + ", kenmerk " + ph("kenmerk", "kenmerk"), true);
    add("");
    add("Geachte heer, mevrouw,");
    add("");
    add("Hierbij maak ik bezwaar tegen uw besluit van " + phDate("besluit_datum", "datum besluit") + " met kenmerk " + ph("kenmerk", "kenmerk") + ", over " + ph("onderwerp", "onderwerp van het besluit") + ". Een kopie van het besluit is bijgevoegd.");
    add("");
    var reden = val("reden");
    add("Ik ben het niet eens met dit besluit." + (reden ? " " + reden.replace(/\s+/g, " ") + (/[.!?]$/.test(reden) ? "" : ".") : ""));
    add("");
    add("Ik dien dit bezwaarschrift pro forma in om de bezwaartermijn veilig te stellen. De gronden van mijn bezwaar vul ik nog aan. Ik verzoek u mij daarvoor een redelijke termijn te geven van ten minste vier weken.");
    if (val("stukken")) { add(""); add("Ik verzoek u mij een kopie te sturen van alle stukken die op dit besluit betrekking hebben."); }
    if (val("horen")) { add(""); add("Ik wil graag worden gehoord over mijn bezwaar."); }
    add("");
    add("Met vriendelijke groet,");
    add(""); add(""); add("");
    add("(handtekening)");
    add(ph("naam", "uw naam"));
    add("");
    add("Bijlage: kopie van het besluit");
    return L;
  }

  var esc = function (s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); };
  function render() {
    var lines = letter();
    preview.innerHTML = lines.map(function (l) {
      if (!l.t) return "<p class=\"gap\"></p>";
      var t = esc(l.t).replace(/\[[^\]]+\]/g, "<mark>$&</mark>");
      return l.b ? "<p><strong>" + t + "</strong></p>" : "<p>" + t + "</p>";
    }).join("");
    var d = val("besluit_datum");
    var out = document.getElementById("bezwaar-deadline");
    if (d) {
      var x = new Date(d + "T12:00:00"); x.setDate(x.getDate() + 42);
      out.textContent = "Uiterste datum (indicatie): " + x.getDate() + " " + MONTHS[x.getMonth()] + " " + x.getFullYear() +
        ". Valt die dag in het weekend of op een feestdag, dan schuift de termijn op naar de eerstvolgende werkdag.";
      out.hidden = false;
    } else { out.hidden = true; }
  }
  form.addEventListener("input", render);
  form.addEventListener("change", render);
  render();

  function check() {
    var missing = [];
    form.querySelectorAll("[required]").forEach(function (el) {
      var ok = el.value.trim() !== "";
      el.setAttribute("aria-invalid", ok ? "false" : "true");
      if (!ok) missing.push(form.querySelector("label[for=" + el.id + "]").textContent.replace(" *", "").replace("(verplicht)", "").trim());
    });
    if (missing.length) {
      status.textContent = "Vul eerst de verplichte velden in: " + missing.join(", ") + ".";
      status.className = "form-status err"; status.hidden = false;
      form.querySelector("[aria-invalid=true]").focus();
      return false;
    }
    status.hidden = true;
    return true;
  }

  function save(blob, name) {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
    status.textContent = "Het bestand is gedownload. Controleer de brief, onderteken hem en verstuur hem op tijd.";
    status.className = "form-status ok"; status.hidden = false;
  }
  var fileBase = function () { return "pro-forma-bezwaarschrift-" + (val("kenmerk") || "besluit").replace(/[^A-Za-z0-9-]+/g, "-").slice(0, 40); };

  /* ---------- Word (.docx): minimale OOXML in een ZIP zonder compressie ---------- */
  var CRC = (function () { var t = [], c; for (var n = 0; n < 256; n++) { c = n; for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
  function crc32(b) { var c = 0xFFFFFFFF; for (var i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 0xFF] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; }
  function zip(files) {
    var enc = new TextEncoder(), parts = [], central = [], offset = 0;
    var u16 = function (n) { return [n & 255, (n >>> 8) & 255]; };
    var u32 = function (n) { return [n & 255, (n >>> 8) & 255, (n >>> 16) & 255, (n >>> 24) & 255]; };
    files.forEach(function (f) {
      var name = enc.encode(f[0]), data = enc.encode(f[1]), crc = crc32(data);
      var common = [].concat(u16(20), u16(0x0800), u16(0), u16(0), u16(0x21), u32(crc), u32(data.length), u32(data.length), u16(name.length), u16(0));
      var local = new Uint8Array([].concat(u32(0x04034b50), common));
      parts.push(local, name, data);
      central.push(new Uint8Array([].concat(u32(0x02014b50), u16(20), common, u16(0), u16(0), u16(0), u32(0), u32(offset))), name);
      offset += local.length + name.length + data.length;
    });
    var size = central.reduce(function (s, p) { return s + p.length; }, 0);
    var end = new Uint8Array([].concat(u32(0x06054b50), u16(0), u16(0), u16(files.length), u16(files.length), u32(size), u32(offset), u16(0)));
    return new Blob(parts.concat(central, [end]), { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
  }
  function docx() {
    var x = function (s) { return esc(s).replace(/"/g, "&quot;"); };
    var body = letter().map(function (l) {
      return "<w:p><w:pPr><w:spacing w:after=\"0\"/></w:pPr>" + (l.t ? "<w:r>" + (l.b ? "<w:rPr><w:b/></w:rPr>" : "") + "<w:t xml:space=\"preserve\">" + x(l.t) + "</w:t></w:r>" : "") + "</w:p>";
    }).join("");
    var doc = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\"><w:body>" + body +
      "<w:sectPr><w:pgSz w:w=\"11906\" w:h=\"16838\"/><w:pgMar w:top=\"1418\" w:right=\"1418\" w:bottom=\"1418\" w:left=\"1418\" w:header=\"709\" w:footer=\"709\" w:gutter=\"0\"/></w:sectPr></w:body></w:document>";
    var styles = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><w:styles xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii=\"Arial\" w:hAnsi=\"Arial\" w:cs=\"Arial\"/><w:sz w:val=\"22\"/><w:lang w:val=\"nl-NL\"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after=\"0\" w:line=\"276\" w:lineRule=\"auto\"/></w:pPr></w:pPrDefault></w:docDefaults></w:styles>";
    return zip([
      ["[Content_Types].xml", "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"><Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/><Default Extension=\"xml\" ContentType=\"application/xml\"/><Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/><Override PartName=\"/word/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml\"/></Types>"],
      ["_rels/.rels", "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/></Relationships>"],
      ["word/_rels/document.xml.rels", "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/></Relationships>"],
      ["word/document.xml", doc],
      ["word/styles.xml", styles]
    ]);
  }

  /* ---------- PDF: A4, Helvetica, met regelafbreking ---------- */
  var W = [278,278,355,556,556,889,667,191,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,278,278,584,584,584,556,1015,667,667,722,722,667,611,778,722,278,500,667,556,833,722,778,667,778,722,667,611,722,667,944,667,667,611,278,278,278,469,556,333,556,556,500,556,556,278,556,556,222,222,500,222,833,556,556,556,556,333,500,278,556,500,722,500,500,500,334,260,334,584];
  var width = function (s, size, bold) { var w = 0; for (var i = 0; i < s.length; i++) { var c = s.charCodeAt(i); w += (c >= 32 && c <= 126 ? W[c - 32] : 556) * (bold ? 1.05 : 1); } return w * size / 1000; };
  function wrap(text, size, bold, max) {
    var words = text.split(" "), out = [], line = "";
    words.forEach(function (w) { var t = line ? line + " " + w : w; if (width(t, size, bold) > max && line) { out.push(line); line = w; } else line = t; });
    out.push(line); return out;
  }
  function pdfStr(s) {
    var o = "";
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i), ch = s[i];
      if (c === 0x20AC) c = 128; else if (c === 0x2018 || c === 0x2019) c = 39; else if (c === 0x201C || c === 0x201D) c = 34; else if (c === 0x2013 || c === 0x2014) c = 45;
      if (ch === "(" || ch === ")" || ch === "\\") o += "\\" + ch;
      else if (c >= 32 && c <= 126) o += String.fromCharCode(c);
      else if (c < 256) o += "\\" + ("00" + c.toString(8)).slice(-3);
      else o += "?";
    }
    return o;
  }
  function pdf() {
    var size = 11, lead = 15.5, left = 70, top = 780, bottom = 70, max = 595 - 2 * left;
    var pages = [[]], y = top;
    letter().forEach(function (l) {
      var rows = l.t ? wrap(l.t, size, l.b, max) : [""];
      rows.forEach(function (r) {
        if (y < bottom) { pages.push([]); y = top; }
        if (r) pages[pages.length - 1].push("BT /" + (l.b ? "F2" : "F1") + " " + size + " Tf " + left + " " + y.toFixed(1) + " Td (" + pdfStr(r) + ") Tj ET");
        y -= l.t ? lead : lead * 0.7;
      });
    });
    var objs = [], kids = [];
    objs[1] = "<< /Type /Catalog /Pages 2 0 R >>";
    objs[3] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>";
    objs[4] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>";
    pages.forEach(function (p, i) {
      var pn = 5 + i * 2, cn = pn + 1, content = p.join("\n");
      kids.push(pn + " 0 R");
      objs[pn] = "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents " + cn + " 0 R >>";
      objs[cn] = "<< /Length " + content.length + " >>\nstream\n" + content + "\nendstream";
    });
    objs[2] = "<< /Type /Pages /Kids [" + kids.join(" ") + "] /Count " + pages.length + " >>";
    var out = "%PDF-1.4\n", xref = [];
    for (var n = 1; n < objs.length; n++) { xref[n] = out.length; out += n + " 0 obj\n" + objs[n] + "\nendobj\n"; }
    var start = out.length;
    out += "xref\n0 " + objs.length + "\n0000000000 65535 f \n";
    for (n = 1; n < objs.length; n++) out += ("000000000" + xref[n]).slice(-10) + " 00000 n \n";
    out += "trailer\n<< /Size " + objs.length + " /Root 1 0 R >>\nstartxref\n" + start + "\n%%EOF\n";
    var bytes = new Uint8Array(out.length);
    for (var i = 0; i < out.length; i++) bytes[i] = out.charCodeAt(i) & 255;
    return new Blob([bytes], { type: "application/pdf" });
  }

  document.getElementById("download-docx").addEventListener("click", function () { if (check()) save(docx(), fileBase() + ".docx"); });
  document.getElementById("download-pdf").addEventListener("click", function () { if (check()) save(pdf(), fileBase() + ".pdf"); });
})();
