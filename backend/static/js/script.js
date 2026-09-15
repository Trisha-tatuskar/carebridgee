// Generic frontend behaviours and input validation

document.addEventListener("DOMContentLoaded", function () {
  console.log("CareBridge scripts loaded.");

  // ===== NAV: Warn when clicking locked links before login =====
  const lockedLinks = document.querySelectorAll("[data-requires-login='true']");
  lockedLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      alert("Please login first to use this option.");
      window.location.href = "/login/";
    });
  });

  // ===== GENERIC FORM VALIDATION =====
  const formsToValidate = [
    "#loginForm",
    "#registerForm",
    "#volunteerForm",
    "#donationForm",
    "#emergencyForm",
  ];

  formsToValidate.forEach((selector) => {
    const form = document.querySelector(selector);
    if (!form) return;

    form.addEventListener("submit", function (e) {
      const inputs = form.querySelectorAll("input, textarea, select");
      let valid = true;
      let firstInvalid = null;

      inputs.forEach((input) => {
        const value = (input.value || "").trim();

        // Skip buttons
        if (input.type === "submit" || input.type === "button") return;

        // Required check
        if (!value) {
          valid = false;
          if (!firstInvalid) firstInvalid = input;
          input.classList.add("cb-input-error");
          return;
        } else {
          input.classList.remove("cb-input-error");
        }

        // Email pattern
        if (
          (input.type === "email" || input.name.toLowerCase().includes("email")) &&
          value
        ) {
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(value)) {
            valid = false;
            if (!firstInvalid) firstInvalid = input;
            alert("Please enter a valid email address.");
          }
        }

        // Phone validation (10+ digits)
        if (
          input.type === "tel" ||
          input.name.toLowerCase().includes("phone") ||
          input.name.toLowerCase().includes("mobile")
        ) {
          const digits = value.replace(/\D/g, "");
          if (digits.length < 10) {
            valid = false;
            if (!firstInvalid) firstInvalid = input;
            alert("Please enter a valid phone number (at least 10 digits).");
          }
        }

        // Password length
        if (
          input.type === "password" ||
          input.name.toLowerCase().includes("password")
        ) {
          if (value.length < 6) {
            valid = false;
            if (!firstInvalid) firstInvalid = input;
            alert("Password should be at least 6 characters long.");
          }
        }
      });

      // Special check for confirm password in register form
      if (selector === "#registerForm") {
        const pwd1 =
          form.querySelector("input[name*='password1']") ||
          form.querySelector("input[name*='password']");
        const pwd2 =
          form.querySelector("input[name*='password2']") ||
          form.querySelector("input[name*='confirm']");
        if (pwd1 && pwd2 && pwd1.value && pwd2.value) {
          if (pwd1.value !== pwd2.value) {
            valid = false;
            alert("Passwords do not match.");
            firstInvalid = firstInvalid || pwd2;
          }
        }
      }

      if (!valid) {
        e.preventDefault();
        if (firstInvalid) firstInvalid.focus();
      }
    });
  });
});
