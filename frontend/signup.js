document.getElementById('signup-form').addEventListener('submit', async function (event) {
  event.preventDefault();  // Prevent the default form submission

  const firstName = document.getElementById('first-name').value;
  const lastName = document.getElementById('last-name').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  const data = {
    first_name: firstName,
    last_name: lastName,
    email: email,
    password: password,
  };

  // Print the entered data to the console
  console.log("Entered data:", data);

  try {
    const response = await fetch('http://localhost:8000/api/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',  // Send data as JSON
      },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      const result = await response.json();
      document.getElementById('response-message').textContent = 'Signup successful!';
      
      // Redirect the user to the dashboard after a short delay
      setTimeout(function () {
        window.location.href = '/dashboard.html';  // Change the URL to your dashboard file
      }, 1000);  // Redirect after 1 second delay
    } else {
      const errorData = await response.json();
      document.getElementById('response-message').textContent = `Error: ${errorData.message}`;
    }
  } catch (error) {
    document.getElementById('response-message').textContent = `Error: ${error.message}`;
  }
});
