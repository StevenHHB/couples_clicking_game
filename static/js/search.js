// search.js

document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const messageElement = document.getElementById('message');
  
    searchForm.addEventListener('submit', async (event) => {
      event.preventDefault();
  
      const username = document.getElementById('username').value;
  
      // Make a request to the server to search for the username
      const response = await fetch('/search', {
        method: 'POST',
        body: JSON.stringify({ username }),
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      const data = await response.json();
  
      if (data.success) {
        messageElement.textContent = 'Significant other added!';
      } else {
        messageElement.textContent = 'User not found';
      }
    });
  });
  