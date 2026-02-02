---
title: "Contact"
draft: false
showDate: false
showDateUpdated: false
showAuthor: false
slug: "contact"
---

<form id="contact-form" class="contact-form"
      action="https://formspree.io/f/xzdgvqgj"
      method="POST">

  <div class="form-field">
    <label for="name">Full Name</label>
    <input id="name" type="text" name="name" required />
  </div>

  <div class="form-field">
    <label for="organisation">Organisation</label>
    <input id="organisation" type="text" name="organisation" />
  </div>

  <div class="form-field">
    <label for="email">E-mail Address</label>
    <input id="email" type="email" name="email" required />
  </div>

  <div class="form-field">
    <label for="message">Message</label>
    <textarea id="message" name="message" rows="5" required></textarea>
  </div>

  <button type="submit" class="btn-primary">
    Send message
  </button>

  <p id="contact-form-status" class="form-status"></p>
</form>

<script>
  var form = document.getElementById("contact-form");
  
  async function handleSubmit(event) {
    event.preventDefault();
    var status = document.getElementById("contact-form-status");
    var data = new FormData(event.target);
    fetch(event.target.action, {
      method: form.method,
      body: data,
      headers: {
          'Accept': 'application/json'
      }
    }).then(response => {
      if (response.ok) {
        status.innerHTML = "Thank you for your message!";
        form.reset()
      } else {
        response.json().then(data => {
          if (Object.hasOwn(data, 'errors')) {
            status.innerHTML = data["errors"].map(error => error["message"]).join(", ")
          } else {
            status.innerHTML = "Oops! There was a problem submitting your form"
          }
        })
      }
    }).catch(error => {
      status.innerHTML = "Oops! There was a problem submitting your form"
    });
  }
  form.addEventListener("submit", handleSubmit)
</script>
