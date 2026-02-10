// Main JS file for global utility functions

document.addEventListener("DOMContentLoaded", function () {
  // Clock
  const clockElement = document.getElementById("clock");
  if (clockElement) {
    setInterval(() => {
      const now = new Date();
      clockElement.textContent = now.toLocaleTimeString("ar-SA", {
        hour: "2-digit",
        minute: "2-digit",
      });
    }, 1000);
  }

  // Auto-hide alerts after 5 seconds
  const alerts = document.querySelectorAll(".auto-hide");
  if (alerts.length > 0) {
    setTimeout(() => {
      alerts.forEach((alert) => {
        alert.style.transition = "opacity 0.5s ease";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
      });
    }, 5000);
  }

  // Initialize theme from localStorage
  const themeController = document.querySelector(".theme-switch");
  if (themeController) {
    const currentTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", currentTheme);
    themeController.checked = currentTheme === "dark";

    themeController.addEventListener("change", (e) => {
      const theme = e.target.checked ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", theme);
      localStorage.setItem("theme", theme);
    });
  }
});
