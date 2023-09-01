// index.js

document.addEventListener("DOMContentLoaded", function () {
    // Logic to handle DOMContentLoaded event
    const registerButton = document.getElementById("register-button");
    const loginButton = document.getElementById("login-button");
  
    // Attach click event listeners to the register and login buttons
    registerButton.addEventListener("click", function () {
      window.location.href = "{{ url_for('register') }}";
    });
  
    loginButton.addEventListener("click", function () {
      window.location.href = "{{ url_for('login') }}";
    });
  });
  