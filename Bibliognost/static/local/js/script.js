$(document).ready(function() {

	$('.collapsible').collapsible();

	var searchBooks = function(searchTerm) {
		var options = {
			method: 'GET',
			mode: 'same-origin'
		};
		fetch('/search?q=' + searchTerm, options)
			.then(function(response) {
				return response.text();
			})
			.then(function(data) {
				$('#search-results').html('');
				console.log(data);
				$('#search-results').html(data);
			})
			.catch(function(err) {
				Materialize.toast('Error while searching for book !', 4000)
				console.log(err);
			});
	};

	var onSearchKeyUp = function(event) {
		$('#search-results').css('display', 'inherit');
		var searchTerm = event.target.value;

		if (searchTerm.length >= 3) {
			searchBooks(searchTerm);
		} else {
			$('#search-results').css('display', 'none');
		}
	};

	var throttledBooksSearch = _.throttle(onSearchKeyUp, 2000, { 'trailing': true });

	$('#search').on('keyup', throttledBooksSearch);
});