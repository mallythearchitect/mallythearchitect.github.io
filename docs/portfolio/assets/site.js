/* Malachi Collins: portfolio. Small touches of motion; every page works without this file.
   - Things below the fold fade up as they scroll in (never anything already on screen).
   - Numbers marked data-count count up the first time they're seen.
   - Cards get a soft spotlight that follows the pointer, on devices that can hover.
   Nothing moves for people who ask their device for less motion. */
(() => {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const canHover = window.matchMedia("(hover: hover)").matches;

  if (!reduce && "IntersectionObserver" in window) {
    const SEL = [
      ".band-head", ".bcard", ".pillar", ".lcol", ".apprentice-note", ".subhead",
      ".card", ".ptile", ".tile", ".stat", ".job", ".shot", ".finder", ".bars",
      ".cta", ".section-head", ".project-head", ".flow", ".jump", ".chips", ".label-row",
    ].join(",");
    const fold = window.innerHeight * 0.9;
    const order = new Map();
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        e.target.classList.add("in");
        io.unobserve(e.target);
      }
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.06 });

    document.querySelectorAll(SEL).forEach((el) => {
      if (el.closest(".hero") || el.parentElement.closest(".rv")) return;
      if (el.getBoundingClientRect().top < fold) return;
      const i = order.get(el.parentElement) || 0;
      order.set(el.parentElement, i + 1);
      el.style.setProperty("--d", (Math.min(i, 5) * 0.07).toFixed(2) + "s");
      el.classList.add("rv");
      io.observe(el);
    });

    const counters = document.querySelectorAll("[data-count]");
    const cio = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        cio.unobserve(e.target);
        countUp(e.target);
      }
    }, { threshold: 0.4 });
    counters.forEach((el) => cio.observe(el));
  }

  function countUp(el) {
    const end = Number(el.dataset.count);
    const suffix = el.dataset.suffix || "";
    const prefix = el.dataset.prefix || "";
    if (!Number.isFinite(end)) return;
    const final = el.textContent;
    const start = performance.now();
    const dur = 1400;
    const step = (now) => {
      const t = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = prefix + Math.round(end * eased).toLocaleString("en-US") + suffix;
      if (t < 1) requestAnimationFrame(step);
      else el.textContent = final;
    };
    requestAnimationFrame(step);
  }

  if (canHover) {
    document.querySelectorAll(".bcard, .pillar, .lcol, .lic, .card, .ptile, .tile").forEach((el) => {
      el.classList.add("spot");
      el.addEventListener("pointermove", (e) => {
        const r = el.getBoundingClientRect();
        el.style.setProperty("--mx", (e.clientX - r.left) + "px");
        el.style.setProperty("--my", (e.clientY - r.top) + "px");
      });
    });
  }
})();
