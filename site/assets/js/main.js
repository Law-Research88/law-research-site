/* Law & Research — interactie (geen externe bibliotheken nodig) */
(function () {
  "use strict";

  /* Mobiel menu */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.style.overflow = open ? "hidden" : "";
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      }
    });
  }
  document.querySelectorAll(".nav-sub-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.closest(".has-sub");
      var open = li.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  document.addEventListener("click", function (e) {
    document.querySelectorAll(".has-sub.open").forEach(function (li) {
      if (!li.contains(e.target)) {
        li.classList.remove("open");
        li.querySelector(".nav-sub-toggle").setAttribute("aria-expanded", "false");
      }
    });
  });

  /* Jaartal in footer */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* Rustig infaden bij scrollen */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* Nieuwsfilter (type + rechtsgebied) */
  var list = document.querySelector("[data-news-list]");
  if (list) {
    var state = { type: "alle", gebied: "alle", thema: "alle" };
    var params = new URLSearchParams(location.search);
    ["type", "gebied", "thema"].forEach(function (k) { if (params.get(k)) state[k] = params.get(k); });
    var empty = document.querySelector("[data-news-empty]");
    var apply = function () {
      var shown = 0;
      list.querySelectorAll(".news-item").forEach(function (item) {
        var ok = (state.type === "alle" || item.dataset.type === state.type) &&
                 (state.gebied === "alle" || item.dataset.gebied === state.gebied) &&
                 (state.thema === "alle" || (item.dataset.thema || "").split(" ").indexOf(state.thema) !== -1);
        item.hidden = !ok;
        if (ok) shown++;
      });
      document.querySelectorAll("[data-filter]").forEach(function (chip) {
        chip.setAttribute("aria-pressed", state[chip.dataset.filter] === chip.dataset.value ? "true" : "false");
      });
      if (empty) empty.hidden = shown > 0;
    };
    document.querySelectorAll("[data-filter]").forEach(function (chip) {
      chip.addEventListener("click", function () {
        state[chip.dataset.filter] = chip.dataset.value;
        apply();
        var q = new URLSearchParams();
        if (state.type !== "alle") q.set("type", state.type);
        if (state.gebied !== "alle") q.set("gebied", state.gebied);
        if (state.thema !== "alle") q.set("thema", state.thema);
        history.replaceState(null, "", location.pathname + (q.toString() ? "?" + q : "") + location.hash);
      });
    });
    apply();
  }

  /* Tabbladen (particulier / ondernemer) */
  document.querySelectorAll("[data-tabs]").forEach(function (wrap) {
    var buttons = wrap.querySelectorAll("[data-tab]");
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        buttons.forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
        wrap.querySelectorAll(".tab-panel").forEach(function (p) { p.hidden = p.id !== btn.dataset.tab; });
      });
    });
  });

  /* Formulieren via Formspree (werkt op elke statische hosting) */
  document.querySelectorAll("form[data-form]").forEach(function (form) {
    var status = form.querySelector(".form-status");
    var btn = form.querySelector("button[type=submit]");
    var show = function (msg, ok) {
      status.textContent = msg;
      status.className = "form-status " + (ok ? "ok" : "err");
      status.hidden = false;
    };
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form.action.indexOf("JOUW_FORM_ID") !== -1) {
        show("Dit formulier is nog niet gekoppeld. Mail ons zolang rechtstreeks via info@law-research.nl.", false);
        return;
      }
      if (!form.checkValidity()) { form.reportValidity(); return; }
      btn.disabled = true;
      var label = btn.textContent;
      btn.textContent = "Bezig met verzenden…";
      fetch(form.action, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error();
          form.reset();
          show(form.dataset.success || "Bedankt! Uw bericht is verzonden. Wij nemen zo snel mogelijk contact met u op.", true);
        })
        .catch(function () {
          show("Het verzenden is niet gelukt. Probeer het opnieuw of mail naar info@law-research.nl.", false);
        })
        .then(function () { btn.disabled = false; btn.textContent = label; });
    });
  });

  /* Rekenhulp bezwaartermijn (art. 6:7 en 6:8 Awb + Algemene termijnenwet) */
  var calc = document.getElementById("bezwaar-calc");
  if (calc) {
    var input = calc.querySelector("input[type=date]");
    var out = calc.querySelector(".tool-result");
    var pad = function (n) { return (n < 10 ? "0" : "") + n; };
    var key = function (d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); };
    var easter = function (y) { // anonieme Gregoriaanse berekening
      var a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4,
          f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30,
          i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7,
          m = Math.floor((a + 11 * h + 22 * l) / 451), month = Math.floor((h + l - 7 * m + 114) / 31),
          day = ((h + l - 7 * m + 114) % 31) + 1;
      return new Date(y, month - 1, day);
    };
    var plus = function (d, n) { var x = new Date(d); x.setDate(x.getDate() + n); return x; };
    var holidays = function (y) {
      var e = easter(y), kd = new Date(y, 3, 27);
      if (kd.getDay() === 0) kd = new Date(y, 3, 26); // Koningsdag op zondag → zaterdag
      return [new Date(y, 0, 1), plus(e, 1), plus(e, 39), plus(e, 50), kd, new Date(y, 4, 5),
              new Date(y, 11, 25), new Date(y, 11, 26)].map(key);
    };
    var isFree = function (d) {
      return d.getDay() === 0 || d.getDay() === 6 || holidays(d.getFullYear()).indexOf(key(d)) !== -1;
    };
    var fmt = new Intl.DateTimeFormat("nl-NL", { weekday: "long", day: "numeric", month: "long", year: "numeric" });

    /* Beslisboom: wie nam het besluit, waar gaat het over, en wat is de route? */
    var RB = "de rechtbank (sector bestuursrecht) in uw regio";
    var CRVB = "hoger beroep bij de Centrale Raad van Beroep";
    var RVS = "hoger beroep bij de Afdeling bestuursrechtspraak van de Raad van State";
    var HOF = "hoger beroep bij het gerechtshof, en daarna eventueel cassatie bij de Hoge Raad";
    var route = function (bezwaar, beroep, hoger, tip) { return { steps: [bezwaar, beroep, hoger].filter(Boolean), tip: tip || "", termijn: true }; };
    var TREE = {
      gemeente: { label: "Gemeente", types: {
        bijstand: ["Bijstand (Participatiewet)", route("Bezwaar maken bij het college van burgemeester en wethouders van uw gemeente.", "Beroep bij " + RB + ".", "Daarna eventueel " + CRVB + ".", "Wordt uw uitkering stopgezet of teruggevorderd en kunt u niet wachten? Vraag de rechter dan ook om een voorlopige voorziening.")],
        bijzonder: ["Bijzondere bijstand", route("Bezwaar maken bij het college van burgemeester en wethouders van uw gemeente.", "Beroep bij " + RB + ".", "Daarna eventueel " + CRVB + ".", "Bewaar bonnen, offertes en rekeningen: die heeft u nodig om de kosten aan te tonen.")],
        zorg: ["Wmo of Jeugdwet (zorg en ondersteuning)", route("Bezwaar maken bij het college van burgemeester en wethouders van uw gemeente.", "Beroep bij " + RB + ".", "Daarna eventueel " + CRVB + ".")],
        belasting: ["WOZ-waarde of gemeentelijke belasting", route("Bezwaar maken bij de heffingsambtenaar van de gemeente (soms een samenwerkingsverband, zoals een belastingkantoor van meerdere gemeenten).", "Beroep bij " + RB + ".", "Daarna eventueel " + HOF + ".")],
        anders: ["Ander besluit (bijvoorbeeld een vergunning of handhaving)", route("Bezwaar maken bij het college van burgemeester en wethouders van uw gemeente.", "Beroep bij " + RB + ".", "Daarna eventueel " + RVS + ".", "Bij sommige vergunningen is er geen bezwaar, maar gaat u direct in beroep bij de rechtbank. Kijk onderaan het besluit.")]
      } },
      uwv: { label: "UWV", route: route("Bezwaar maken bij het UWV (dat kan ook digitaal via Mijn UWV).", "Beroep bij " + RB + ".", "Daarna eventueel " + CRVB + ".", "Dit geldt onder meer voor de WW, de WIA, de Ziektewet en de Wajong.") },
      provincie: { label: "Provincie", route: route("Bezwaar maken bij Gedeputeerde Staten van de provincie.", "Beroep bij " + RB + ".", "Daarna eventueel " + RVS + ".", "Bij sommige besluiten is er geen bezwaar, maar gaat u direct in beroep. Kijk onderaan het besluit.") },
      belastingdienst: { label: "Belastingdienst", types: {
        aanslag: ["Belastingaanslag (bijvoorbeeld inkomstenbelasting)", route("Bezwaar maken bij de inspecteur van de Belastingdienst.", "Beroep bij " + RB + ".", "Daarna eventueel " + HOF + ".")],
        toeslag: ["Toeslag (huur-, zorg- of kinderopvangtoeslag, kindgebonden budget)", route("Bezwaar maken bij Dienst Toeslagen.", "Beroep bij " + RB + ".", "Daarna eventueel " + RVS + ".", "Moet u een toeslag terugbetalen? U kunt ook een betalingsregeling vragen; dat staat los van uw bezwaar.")]
      } },
      duo: { label: "DUO", route: route("Bezwaar maken bij DUO.", "Beroep bij " + RB + ".", "Daarna eventueel " + CRVB + ".", "Dit geldt voor studiefinanciering, het studievoorschot en de terugbetaling van uw studieschuld.") },
      school: { label: "School, hogeschool of universiteit", types: {
        examen: ["Hogeschool of universiteit: tentamen, examen of bindend studieadvies", { steps: ["Beroep instellen bij het College van beroep voor de examens (CBE) van uw hogeschool of universiteit.", "Daarna eventueel beroep bij het College van Beroep voor het Hoger Onderwijs (CBHO) in Den Haag."], tip: "Ook hier geldt meestal een termijn van zes weken. Het CBE probeert vaak eerst een schikking.", termijn: true }],
        hoger: ["Hogeschool of universiteit: ander besluit (inschrijving, toelating, collegegeld)", { steps: ["Bezwaar maken bij de hogeschool of universiteit (meestal via het loket voor bezwaar en beroep).", "Daarna eventueel beroep bij het College van Beroep voor het Hoger Onderwijs (CBHO) in Den Haag."], tip: "Dit geldt voor bekostigde (door de overheid betaalde) hogescholen en universiteiten. Bij een particuliere opleiding gelden andere regels.", termijn: true }],
        school: ["Basisschool, middelbare school of mbo", { steps: ["Meestal is dit geen bestuursrecht. Kijk in de klachtenregeling, het examenreglement of de schoolgids.", "Bij een mbo-examen kunt u meestal beroep instellen bij de commissie van beroep voor de examens van de school."], tip: "De termijnen staan in het reglement van de school en zijn vaak korter dan zes weken.", termijn: false }]
      } },
      anders: { label: "Andere overheidsinstantie", route: route("Bezwaar maken bij de instantie die het besluit heeft genomen (bijvoorbeeld de SVB of de IND).", "Daarna beroep bij " + RB + ".", "", "Bij wie u bezwaar maakt en welke termijn geldt, staat altijd onderaan het besluit.") }
    };
    var orgBox = calc.querySelector('[data-bb="org"]');
    var typeBox = calc.querySelector('[data-bb="type"]');
    var subStep = calc.querySelector("[data-bb-sub]");
    var pick = { org: null, type: null };
    var chip = function (value, label, group) {
      return '<button class="chip" type="button" data-value="' + value + '" data-group="' + group + '" aria-pressed="false">' + label + "</button>";
    };
    orgBox.innerHTML = Object.keys(TREE).map(function (k) { return chip(k, TREE[k].label, "org"); }).join("");
    var press = function (box, value) {
      box.querySelectorAll(".chip").forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.value === value)); });
    };
    var deadline = function () {
      if (!input.value) return null;
      var p = input.value.split("-");
      var end = plus(new Date(+p[0], +p[1] - 1, +p[2]), 42); // termijn begint de dag na bekendmaking en duurt zes weken
      var moved = false;
      while (isFree(end)) { end = plus(end, 1); moved = true; }
      return { end: end, moved: moved };
    };
    var run = function () {
      var org = pick.org && TREE[pick.org];
      var r = org && (org.route || (pick.type && org.types[pick.type] && org.types[pick.type][1]));
      var d = deadline();
      if (!d && !r) { out.hidden = true; return; }
      var html = "";
      if (d && (!r || r.termijn)) {
        html += "<small>Uw bezwaar- of beroepschrift moet uiterlijk binnen zijn op</small><strong>" + fmt.format(d.end) + "</strong>";
        if (d.moved) html += "<small>De termijn eindigde in een weekend of op een feestdag en schuift daarom op naar de eerstvolgende werkdag.</small>";
      } else if (!d && r && r.termijn) {
        html += "<small>Vul bij vraag 1 de datum van het besluit in, dan rekenen wij uw uiterste datum uit.</small>";
      }
      if (r) {
        html += '<ol class="bb-route">' + r.steps.map(function (s) { return "<li>" + s + "</li>"; }).join("") + "</ol>";
        if (r.tip) html += "<small>" + r.tip + "</small>";
        if (r.termijn) html += '<p class="bb-actions"><a class="btn btn--light" href="pro-forma-bezwaarschrift.html">Pro forma bezwaarschrift invullen</a> <a class="btn btn--ghost" href="contact.html?onderwerp=bestuursrecht">Leg uw vraag voor</a></p>';
        else html += '<p class="bb-actions"><a class="btn btn--light" href="contact.html?onderwerp=bestuursrecht">Leg uw vraag voor</a></p>';
      } else if (org && org.types) {
        html += "<small>Kies bij vraag 3 waar het besluit over gaat.</small>";
      } else {
        html += "<small>Kies bij vraag 2 wie het besluit heeft genomen, dan ziet u bij wie u bezwaar of beroep instelt.</small>";
      }
      if (d && !(r && r.termijn === false)) html += "<small>Wacht niet tot de laatste dag: stuur het liefst aangetekend of via het officiële digitale loket.</small>";
      out.innerHTML = html;
      out.hidden = false;
    };
    orgBox.addEventListener("click", function (e) {
      var b = e.target.closest(".chip"); if (!b) return;
      pick.org = b.dataset.value; pick.type = null; press(orgBox, pick.org);
      var t = TREE[pick.org].types;
      if (t) {
        typeBox.innerHTML = Object.keys(t).map(function (k) { return chip(k, t[k][0], "type"); }).join("");
        subStep.hidden = false;
      } else { typeBox.innerHTML = ""; subStep.hidden = true; }
      run();
    });
    typeBox.addEventListener("click", function (e) {
      var b = e.target.closest(".chip"); if (!b) return;
      pick.type = b.dataset.value; press(typeBox, pick.type); run();
    });
    input.addEventListener("change", run);
    input.addEventListener("input", run);
  }
})();
