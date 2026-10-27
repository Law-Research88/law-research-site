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
    var run = function () {
      if (!input.value) { out.hidden = true; return; }
      var p = input.value.split("-");
      var start = new Date(+p[0], +p[1] - 1, +p[2]);
      var end = plus(start, 42); // termijn begint de dag na bekendmaking en duurt zes weken
      var moved = false;
      while (isFree(end)) { end = plus(end, 1); moved = true; }
      out.innerHTML = "<small>Uw bezwaar moet uiterlijk binnen zijn op</small><strong>" + fmt.format(end) +
        "</strong><small>" + (moved ? "De termijn eindigde in een weekend of op een feestdag en schuift daarom op naar de eerstvolgende werkdag. " : "") +
        "Wacht niet tot de laatste dag: stuur uw bezwaar liefst aangetekend of via het officiële digitale loket.</small>";
      out.hidden = false;
    };
    input.addEventListener("change", run);
    input.addEventListener("input", run);
  }
})();
