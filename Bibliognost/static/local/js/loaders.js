$(document).ready(function() {
	var similarBookIds = $(".similar-book-id");
	var options = {
		method: 'GET',
		mode: 'same-origin'
	};
	var isLoading = true;

	$('.collection-header.similar').append(
		$('<span class="new badge blue" data-badge-caption="results">' + similarBookIds.length + '</span>')
	);

	Array.from(similarBookIds).forEach(function(paraTag) {
		fetch('/book-meta?book_id=' + paraTag.id, options)
			.then(function(response) {
				return response.json();
			})
			.then(function(data) {
				console.log(data.id);
				if (isLoading) {
					isLoading = false;
					$('#similar-books').html('');
				}
				var similarBook = $(
					'<a href="/book/' + data.id + '" class="collection-item avatar">' +
						'<img src="'+ data.small_image_url +'" alt="" class="circle">' +
						'<span class="title">' + data.title + '</span>' +
						'<p class="author">by ' + data.author + '</p>' +
					'</a>'
				);
				if (data.publication_year) {
					similarBook.append($('<p class="right-align pub-year">' + data.publication_year + '</p>'));
				}
				$('#similar-books').append(similarBook);
			})
			.catch(function(err) {
				Materialize.toast('Error while loading similar books !', 4000)
				console.log(err);
			});
	});
});