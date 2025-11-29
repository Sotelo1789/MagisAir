let route = document.getElementById('id_route');
let depTime = document.getElementById('id_departure_time');
console.log(route);

depTime.addEventListener('change', function() {
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

  fetch('/get-arrival-time/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ route: route.value, departure_time: depTime.value })
  }).then(response => response.json())
		.then(data => {
			console.log(data);
			let durationInput = document.getElementById('id_arrival_time');
			console.log(data.arrival_time);
			durationInput.value = data.arrival_time;
		})
		.catch(error => {console.error('Error fetching data:', error);});
})