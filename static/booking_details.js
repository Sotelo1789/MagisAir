document.addEventListener('DOMContentLoaded', function() {
	let topDiv = document.getElementById('top-div');
	const baggagePrice = topDiv.dataset.baggage;
	const insurancePrice = topDiv.dataset.insurance;
	const flightsCost = topDiv.dataset.flights_cost;
	const selectedID = topDiv.dataset.selected_id;
	const initialBaggage = topDiv.dataset.intial_baggage;

	let baggageCount = initialBaggage ? parseInt(initialBaggage) : 0;
	let selectedPassengerId = (selectedID ? selectedID : null);

	let passengerSelected = false;
	document.querySelectorAll('[id^="passenger-"]').forEach(passenger => {
		if (passenger.classList.contains('selected')) {
			passengerSelected = true;
		}
	})
	console.log(passengerSelected);

	if (!passengerSelected) {
		let btn = document.getElementById('confirm-btn')
		btn.style.opacity = '0.5';
		btn.disabled = true;
	}

	if (selectedPassengerId)
		setTimeout(function() {
			selectPassenger(selectedPassengerId);
		}, 100);

	function updateBaggage(delta) {
		baggageCount = Math.max(0, baggageCount + delta);
		document.getElementById('baggage-count').textContent = baggageCount;
		document.getElementById('baggage-count-input').value = baggageCount;
		updateTotals();
	}

	function selectPassenger(passengerId) {
		document.querySelectorAll('[id^="passenger-"]').forEach(el => {
			if (el.id === 'passenger-' + passengerId) return;

			el.classList.remove('selected');
			el.style.borderColor = '#e5e7eb';
			el.style.backgroundColor = '';
			el.style.opacity = '1';
			el.style.color = '';

			var passengerSubText = el.querySelector('#passenger_id')
			if (passengerSubText) {
				passengerSubText.classList.add('text-slate-500');
				passengerSubText.style.color = '';
			}
		});

		const passengerEl = document.getElementById('passenger-' + passengerId);
		if (passengerEl) {
			passengerEl.classList.add('selected');
			passengerEl.style.borderColor = '#0369a1';
			passengerEl.style.backgroundColor = '#0369a1';
			passengerEl.style.opacity = '1';
			passengerEl.style.color = '#ffffff';

			var passengerSubText = passengerEl.querySelector('#passenger_id')
			if (passengerSubText) {
				passengerSubText.classList.remove('text-slate-500');
				passengerSubText.style.color = '#dbeafe';
			}

			selectedPassengerId = passengerId;
			const passengerInput = document.getElementById('selected-passenger-id');
			if (passengerInput) {
				passengerInput.value = passengerId;
			}

			const confirmBtn = document.getElementById('confirm-btn');
			if (confirmBtn) {
				confirmBtn.disabled = false;
				confirmBtn.style.opacity = '';
			}
		}
	}

	const bookingForm = document.getElementById('booking-form');
	if (bookingForm) {
		bookingForm.addEventListener('submit', function(e) {
			const passengerId = document.getElementById('selected-passenger-id').value;
			if (!passengerId) {
				e.preventDefault();
				alert('Please select a passenger before confirming the booking.');
				return false;
			}
			const confirmBtn = document.getElementById('confirm-btn');
			if (confirmBtn) {
				confirmBtn.disabled = true;
				confirmBtn.textContent = 'Processing...';
			}
			return true;
		});
	}

	function updateTotals(obj) {
		const hasInsurance = document.getElementById('has-insurance').checked;

		const baggageTotal = baggageCount * baggagePrice;

		document.getElementById('baggage-total').textContent = 'Php ' + baggageTotal.toFixed(2);
		document.getElementById('baggage-count-display').textContent = baggageCount;

		if (baggageCount > 0) {
			document.getElementById('baggage-row').style.display = 'flex';
			document.getElementById('baggage-breakdown').textContent = 'Php ' + baggageTotal.toFixed(2);
		} else {
			document.getElementById('baggage-row').style.display = 'none';
		}

		const insuranceTotal = hasInsurance ? insurancePrice : 0;
		document.getElementById('insurance-total').textContent = 'Php ' + parseFloat(insuranceTotal).toFixed(2);

		if (hasInsurance) {
			document.getElementById('insurance-row').style.display = 'flex';
			document.getElementById('insurance-breakdown').textContent = 'Php ' + parseFloat(insuranceTotal).toFixed(2);
		} else {
			document.getElementById('insurance-row').style.display = 'none';
		}

		const total = flightsCost + baggageTotal + insuranceTotal;
		document.getElementById('total-price').textContent = 'Php ' + parseFloat(total).toFixed(2);

		obj.parentElement.style.borderColor = obj.checked ? '#10b981' : '#e5e7eb';
		obj.parentElement.style.backgroundColor = obj.checked ? '#f0fdf4' : '#f8fafc';
	}

	window.updateBaggage = updateBaggage;
	window.selectPassenger = selectPassenger;
	window.updateTotals = updateTotals;

	updateTotals();
});

function travelMouseOver(obj) {
	obj.style.borderColor='#10b981';
	obj.style.backgroundColor='#f0fdf4';
}

function travelMouseOut(obj) {
	if (!document.getElementById('has-insurance').checked) {
		obj.style.borderColor='#e5e7eb';
		obj.style.backgroundColor='#f8fafc';
	}
}

function passengerMouseOver(obj) {
	obj.style.borderColor='#0369a1';
	obj.style.opacity='0.5'
}

function passengerMouseOut(obj) {
	if(!obj.classList.contains('selected')) {
		obj.style.borderColor='#e5e7eb';
		obj.style.opacity='1';
	} else {
		obj.style.opacity='1';
	}
}