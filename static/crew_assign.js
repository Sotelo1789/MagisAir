var crew = document.getElementById('id_crew')
var addMember = document.getElementById('create');

crew.addEventListener('change', function() {
		const selectedCrewId = this.value;
		console.log(selectedCrewId);

		if (selectedCrewId) {
			addMember.classList.add('hidden')
		} else {
			addMember.classList.remove('hidden')
		}

	});