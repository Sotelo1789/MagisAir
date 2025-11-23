// var passengerSelect = document.getElementById('passenger');
var flightSelect = document.getElementById('flight');
var priceInput = document.getElementById('price');

flightSelect.addEventListener('change', function() {
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  fetch('/get-flight-price/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ flight_no: flightSelect.value })
  })
    .then(response => response.json())
    .then(data => {
      console.log(data);
      priceInput.value = parseFloat(data.message).toFixed(2);
    })
    .catch(error => {console.error('Error fetching data:', error);});
});
