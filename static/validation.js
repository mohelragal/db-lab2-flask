document.addEventListener("DOMContentLoaded", () => {
  const showErrors = (container, errors) => {
    if (!container) return;
    container.replaceChildren();
    errors.forEach((message) => {
      const p = document.createElement("p");
      p.className = "field-error";
      p.textContent = message;
      container.appendChild(p);
    });
  };

  const register = document.querySelector("#register-form");
  if (register) {
    register.addEventListener("submit", (event) => {
      const errors = [];
      const name = register.elements.name.value.trim();
      const email = register.elements.email.value.trim();
      const password = register.elements.password.value;
      const confirm = register.elements.confirm_password.value;
      if (!name) errors.push("Name is required");
      if (!email) errors.push("Email is required");
      if (!password) errors.push("Password is required");
      if (!confirm) errors.push("Confirm password is required");
      else if (password !== confirm) errors.push("Passwords do not match");
      if (errors.length) {
        event.preventDefault();
        showErrors(document.querySelector("#client-errors"), errors);
      }
    });
  }

  const login = document.querySelector("#login-form");
  if (login) {
    login.addEventListener("submit", (event) => {
      const errors = [];
      if (!login.elements.email.value.trim()) errors.push("Email is required");
      if (!login.elements.password.value) errors.push("Password is required");
      if (errors.length) {
        event.preventDefault();
        showErrors(document.querySelector("#client-errors"), errors);
      }
    });
  }

  const add = document.querySelector("#add-form");
  if (add) {
    add.addEventListener("submit", (event) => {
      const title = add.elements.title.value.trim();
      const errors = [];
      if (!title) errors.push("Title is required");
      else if (title.length > 200) errors.push("Title is too long");
      if (errors.length) {
        event.preventDefault();
        showErrors(document.querySelector("#client-errors"), errors);
      }
    });
  }
});
