document.getElementById('signup-form').addEventListener('submit', async function (event) {
  event.preventDefault();  // Prevent the default form submission

  const username= document.getElementById('username').value;
  const password2 = document.getElementById('password2').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  const data = {
    username: username,
    email: email,
    password: password,
    password2: password2
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
