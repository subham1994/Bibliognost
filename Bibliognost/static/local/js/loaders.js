$(document).ready(function() {
	/**
	 * Line chart setup
	 */
	var sentiments = [];
	var labels = [];

	var initLineChart = function(labels, sentiments) {
		var ctx = $("#line-chart");
		$("#loader").css('display', 'none');
		var data = {
			labels: labels,
			datasets: [
				{
					label: "Predicted Sentiment",
					fill: true,
					lineTension: 0.1,
					backgroundColor: "rgba(52, 152, 219, 0.4)",
					borderColor: "rgba(52, 152, 219, 1)",
					borderCapStyle: 'butt',
					borderDash: [],
					borderDashOffset: 0.0,
					borderJoinStyle: 'miter',
					pointBorderColor: "rgba(52, 152, 219, 1)",
					pointBackgroundColor: "#fff",
					pointBorderWidth: 1,
					pointHoverRadius: 5,
					pointHoverBackgroundColor: "rgba(52, 152, 219, 1)",
					pointHoverBorderColor: "rgba(220,220,220,1)",
					pointHoverBorderWidth: 2,
					pointRadius: 1,
					pointHitRadius: 10,
					data: sentiments,
					spanGaps: false,
				}
			]
		};
		var myLineChart = new Chart(ctx, {
			type: 'line',
			data: data
		});
	};

	/**
	 * Review loader
	 */
	var bookReviewsContainer = $("#reviews");
	var url = bookReviewsContainer.attr("data-url");
	var isbn = bookReviewsContainer.attr("data-isbn");

	var options = {
		method: 'GET',
		mode: 'same-origin'
	};

	var buildRatingIcons = function(rating) {
		if (rating <= 0) {
			return '';
		}
		var ratingIcons = '';
		for (var i = 0; i < rating; i++) {
			ratingIcons += '<i class="tiny material-icons" style="color: #f1c40f;">star</i>';
		}
		return ratingIcons;
	};

	var buildReviewNode = function(review) {
		var reviewNode = $(
			'<div class="card-panel">' +
				'<p class="review-title">' + review.title + '</p>' +
				buildRatingIcons(review.rating) +
				'<p class="review-details">' + review.author + ' | ' + review.date + '</p>' +
				'<br>' +
				'<p class="review-body">' + review.body + '</p>' +
			'</div>'
		);

		if (review.sentiment > 0.5) {
			reviewNode.append($('<span class="right sentiment" style="color:#0eac51;">Positive</span>'));
		} else {
			reviewNode.append($('<span class="right sentiment" style="color:#D73C2C;">Negative</span>'));
		}

		bookReviewsContainer.append(reviewNode);
	};

	fetch('/reviews?isbn=' + isbn + '&url=' + url, options)
		.then(function(response) {
			return response.json();
		})
		.then(function(data) {
			bookReviewsContainer.html('');
			var index = 1;
			data.amazon.forEach(function(review) {
				sentiments.push(review.sentiment);
				labels.push('#' + index + ', Rating(' + review.rating + ')');
				index++;
				buildReviewNode(review);
			});
			data.goodreads.forEach(function(review) {
				sentiments.push(review.sentiment);
				labels.push('#' + index + ', Rating(' + review.rating + ')');
				index++;
				buildReviewNode(review);
			});
			initLineChart(labels, sentiments);
		})
		.catch(function(err) {
			Materialize.toast('Error while loading reviews !', 4000)
			console.log(err);
		});

	/**
	 * similar books loader
	 */
	var similarBookIdNodes = $(".similar-book-id");
	var similarBookIds = []

	// push ids to the Array
	Array.from(similarBookIdNodes.slice(0, 5)).forEach(function(paraTag) {
		similarBookIds.push(paraTag.id);
	});

	var hideLoadingIndicator = function(selector) {
		$(selector).html('');
	};

	var buildSimilarBookNode = function(bookData) {
		var authors = [];
		for (var id in bookData.authors) {
			authors.push(bookData.authors[id]);
		}
		var similarBook = $(
			'<a href="/book/' + bookData.id + '" class="collection-item avatar">' +
				'<img src="'+ bookData.small_image_url +'" alt="" class="circle">' +
				'<span class="title">' + bookData.title + '</span>' +
				'<p class="author">by ' + authors[0].name + '</p>' +
			'</a>'
		);
		if (bookData.publication_year) {
			similarBook.append($('<p class="right-align pub-year">' + bookData.publication_year + '</p>'));
		}
		return similarBook;
	};


	// fetch details for all similar books at once
	fetch('/book-meta?book_ids=' + similarBookIds.join(), options)
		.then(function(response) {
			return response.json();
		})
		.then(function(similarBooksList) {
			hideLoadingIndicator('#similar-books');
			$('#similar-books').css('overflow-y', 'auto');
			similarBooksList.forEach(function(similarBookData) {
				$('#similar-books').append(buildSimilarBookNode(similarBookData));
			});
		})
		.catch(function(err) {
			Materialize.toast('Error while loading similar books !', 4000)
			console.log(err);
		});
});