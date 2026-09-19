// Verbo — yorug'/to'q mavzu almashtirish (tanlov localStorage'da saqlanadi).
(function () {
  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var btn = document.getElementById("theme-btn");
    if (btn) btn.textContent = theme === "dark" ? "☀️" : "🌙";
  }
  window.toggleTheme = function () {
    var cur = document.documentElement.getAttribute("data-theme") || "light";
    var next = cur === "dark" ? "light" : "dark";
    try { localStorage.setItem("verbo-theme", next); } catch (e) {}
    apply(next);
  };
  // Sahifa yuklanganda tugma matnini to'g'rilash
  document.addEventListener("DOMContentLoaded", function () {
    apply(document.documentElement.getAttribute("data-theme") || "light");
  });
})();
