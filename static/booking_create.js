const tripTypeInputs = document.querySelectorAll('input[name="trip_type"]');
const returnDateInput = document.getElementById('return_date');
const returnField = document.getElementById('return-field');

function toggleReturnDate() {
	const selected = document.querySelector('input[name="trip_type"]:checked');
	const isRoundTrip = selected && selected.value === 'round_trip';
	returnDateInput.disabled = !isRoundTrip;
	if (!isRoundTrip) {
		returnDateInput.value = '';
		returnField.classList.add('is-hidden');
	} else {
		returnField.classList.remove('is-hidden');
	}
}

tripTypeInputs.forEach((input) => {
	input.addEventListener('change', () => {
		document.querySelectorAll('.toggle-chip').forEach((chip) => chip.classList.remove('active'));
		input.parentElement.classList.add('active');
		toggleReturnDate();
	});
});

toggleReturnDate();