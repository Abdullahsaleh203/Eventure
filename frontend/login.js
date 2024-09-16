document.addEventListener('DOMContentLoaded', () => {
  // Select the login form
  const loginForm = document.querySelector('.form.login form');

  // Handle form submission
  loginForm.addEventListener('submit', async function (event) {
    event.preventDefault();  // Prevent the default form submission

    // Get input values
    const email = loginForm.querySelector('input[type="text"]').value;
    const password = loginForm.querySelector('input[type="password"]').value;

    // Prepare the data
    const data = {
      email: email,
      password: password,
    };

    try {
      // Send login request
      const response = await fetch('/api/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',  // Send data as JSON
        },
        body: JSON.stringify(data),
      });

      // Check if the response is OK
      if (response.ok) {
        const result = await response.json();
        console.log('Login successful:', result);
        document.getElementById('response-message').textContent = 'Login successful!';
        
        // Redirect to dashboard or another page
        setTimeout(() => {
          window.location.href = '/dashboard.html';  // Change to your desired URL
        }, 1000);  // Redirect after 1 second delay
      } else {
        const errorData = await response.json();
        document.getElementById('response-message').textContent = `Error: ${errorData.message}`;
      }
    } catch (error) {
      document.getElementById('response-message').textContent = `Error: ${error.message}`;
    }
  });
});
