$(document).ready(function() {
	var similarBookIds = $(".similar-book-id");
	var options = {
		method: 'GET',
		mode: 'same-origin'
	};
	var isLoading = true;
	var index = 0;

	// $('.collection-header.similar').append(
	// 	$('<span class="new badge blue" data-badge-caption="results">' + similarBookIds.length + '</span>')
	// );

	Array.from(similarBookIds.slice(0, 5)).forEach(function(paraTag) {
		fetch('/book-meta?book_id=' + paraTag.id, options)
			.then(function(response) {
				return response.json();
			})
			.then(function(data) {
				var authors = [];
				for (var id in data.authors) {
					authors.push(data.authors[id]);
				}
				if (isLoading) {
					isLoading = false;
					$('#similar-books').css('overflow-y', 'auto');
					$('#similar-books').html('');
				}
				var similarBook = $(
					'<a href="/book/' + data.id + '" class="collection-item avatar">' +
						'<img src="'+ data.small_image_url +'" alt="" class="circle">' +
						'<span class="title">' + data.title + '</span>' +
						'<p class="author">by ' + authors[0].name + '</p>' +
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

	var bookReviewsContainer = $("#reviews"),
		url = bookReviewsContainer.attr("data-url"),
		isbn = bookReviewsContainer.attr("data-isbn");

	console.log('called');

	var isLoadingReviews = true;
	fetch('/reviews?isbn=' + isbn + '&url=' + url, options)
		.then(function(response) {
			console.log('called inside');
			return response.json();
		})
		.then(function(data) {
			console.log(data);
			if (isLoadingReviews) {
				isLoadingReviews = false;
				bookReviewsContainer.html('');
			}
			data.amazon.forEach(function(review) {
				var reviewNode = $(
					'<div class="card-panel">' +
						'<p class="review-title">' + review.title + '</p>' +
						'<p class="review-details">' + review.author + ' | rating: ' + review.rating + ' | ' + review.date + '</p>' +
						'<br>' +
						'<p class="review-body">' + review.body + '</p>' +
					'</div>'
				);

				if (review.sentiment > 0.5) {
					reviewNode.append($(
						'<span class="right sentiment" style="color:green;">Positive</span>'
					));
				} else {
					reviewNode.append($('<span class="right sentiment" style="color:red;">Negative</span>'));
				}
				bookReviewsContainer.append(reviewNode);
			});
			data.goodreads.forEach(function(review) {
				var reviewNode = $(
					'<div class="card-panel">' +
						'<p class="review-title">' + review.title + '</p>' +
						'<p class="review-details">' + review.author + ' | rating: ' + review.rating + ' | ' + review.date + '</p>' +
						'<br>' +
						'<p class="review-body">' + review.body + '</p>' +
					'</div>'
				);

				if (review.sentiment > 0.5) {
					reviewNode.append($('<span class="right sentiment" style="color:green;">Positive</span>'));
				} else {
					reviewNode.append($('<span class="right sentiment" style="color:red;">Negative</span>'));
				}
				bookReviewsContainer.append(reviewNode);
			});
		})
		.catch(function(err) {
			Materialize.toast('Error while loading reviews !', 4000)
			console.log(err);
		});

});