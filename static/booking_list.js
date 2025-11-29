document.addEventListener("DOMContentLoaded", () => {
  const toggleButtons = document.querySelectorAll("[data-booking-toggle]");
  toggleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.getAttribute("data-booking-toggle");
      const details = document.querySelector(`[data-booking-details="${id}"]`);
      if (details) {
        const isHidden = details.hasAttribute("hidden");
        if (isHidden) {
          details.removeAttribute("hidden");
        } else {
          details.setAttribute("hidden", "");
        }

        document
          .querySelectorAll(`[data-booking-toggle="${id}"]`)
          .forEach((btn) => {
            const label = btn.querySelector(".booking-toggle__label");
            const icon = btn.querySelector(".booking-toggle__icon");
            if (label && icon) {
              label.textContent = details.hasAttribute("hidden")
                ? "View Full Details"
                : "Hide Details";
              icon.textContent = details.hasAttribute("hidden") ? "⌄" : "⌃";
            } else if (!btn.classList.contains("booking-toggle--secondary")) {
              btn.textContent = details.hasAttribute("hidden")
                ? "View Full Details"
                : "Hide Details";
            }
          });
      }
    });
  });
});
