// game_interface.js
document.addEventListener('DOMContentLoaded', function () {
    const clickForm = document.getElementById('click-form');
    const clickCount = document.getElementById('click-count');

    // Prevent the default form submission behavior
    clickForm.addEventListener('submit', function (event) {
        event.preventDefault();
        handleClick();
    });

    // Handle button click
    function handleClick() {
        // Make an asynchronous request to the server to handle the button click
        fetch('{{ url_for('click_button') }}', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the click count on the page
                clickCount.textContent = data.clicks;
            } else {
                alert('Game session has ended.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});
