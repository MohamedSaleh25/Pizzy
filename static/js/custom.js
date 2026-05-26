(function ($) {
	"use strict";

	/* ..............................................
	   Loader 
	   ................................................. */
	$(window).on('load', function () {
		$('.preloader').fadeOut();
		$('#preloader').delay(550).fadeOut('slow');
		$('body').delay(450).css({
			'overflow': 'visible'
		});
	});

	/* ..............................................
	   Fixed Menu
	   ................................................. */

	$(window).on('scroll', function () {
		if ($(window).scrollTop() > 50) {
			$('.main-header').addClass('fixed-menu');
		} else {
			$('.main-header').removeClass('fixed-menu');
		}
	});

	/* ..............................................
	   Gallery
	   ................................................. */

	$('#slides-shop').superslides({
		inherit_width_from: '.cover-slides',
		inherit_height_from: '.cover-slides',
		play: 5000,
		animation: 'fade',
	});

	$(".cover-slides ul li").append("<div class='overlay-background'></div>");

	/* ..............................................
	   Map Full
	   ................................................. */

	$(document).ready(function () {
		$(window).on('scroll', function () {
			if ($(this).scrollTop() > 100) {
				$('#back-to-top').fadeIn();
			} else {
				$('#back-to-top').fadeOut();
			}
		});
		$('#back-to-top').click(function () {
			$("html, body").animate({
				scrollTop: 0
			}, 600);
			return false;
		});
	});

	/* ..............................................
	   Special Menu
	   ................................................. */

	var Container = $('.container');
	Container.imagesLoaded(function () {
		var portfolio = $('.special-menu');
		portfolio.on('click', 'button', function () {
			$(this).addClass('active').siblings().removeClass('active');
			var filterValue = $(this).attr('data-filter');
			$grid.isotope({
				filter: filterValue
			});
		});
		var $grid = $('.special-list').isotope({
			itemSelector: '.special-grid'
		});
	});

	/* ..............................................
	   BaguetteBox
	   ................................................. */

	baguetteBox.run('.tz-gallery', {
		animation: 'fadeIn',
		noScrollbars: true
	});

	/* ..............................................
	   Offer Box
	   ................................................. */

	$('.offer-box').inewsticker({
		speed: 3000,
		effect: 'fade',
		dir: 'ltr',
		font_size: 13,
		color: '#ffffff',
		font_family: 'Montserrat, sans-serif',
		delay_after: 1000
	});

	/* ..............................................
	   Tooltip
	   ................................................. */

	$(document).ready(function () {
		$('[data-toggle="tooltip"]').tooltip();
	});

	/* ..............................................
	   Owl Carousel Instagram Feed
	   ................................................. */

	$('.main-instagram').owlCarousel({
		loop: true,
		margin: 0,
		dots: false,
		autoplay: true,
		autoplayTimeout: 3000,
		autoplayHoverPause: true,
		navText: ["<i class='fas fa-arrow-left'></i>", "<i class='fas fa-arrow-right'></i>"],
		responsive: {
			0: {
				items: 2,
				nav: true
			},
			600: {
				items: 4,
				nav: true
			},
			1000: {
				items: 8,
				nav: true,
				loop: true
			}
		}
	});

	/* ..............................................
	   Featured Products
	   ................................................. */

	var featuredProductsBox = $('.featured-products-box');
	var featuredProductsCount = featuredProductsBox.find('.item').length;
	featuredProductsBox.owlCarousel({
		loop: featuredProductsCount > 4,
		margin: 0,
		dots: false,
		autoplay: true,
		autoplayTimeout: 3000,
		autoplayHoverPause: true,
		navText: ["<i class='fas fa-arrow-left'></i>", "<i class='fas fa-arrow-right'></i>"],
		responsive: {
			0: {
				items: 1,
				nav: true
			},
			600: {
				items: 3,
				nav: true
			},
			1000: {
				items: 4,
				nav: true
			}
		}
	});

	/* ..............................................
	   Scroll
	   ................................................. */

	$(document).ready(function () {
		$(window).on('scroll', function () {
			if ($(this).scrollTop() > 100) {
				$('#back-to-top').fadeIn();
			} else {
				$('#back-to-top').fadeOut();
			}
		});
		$('#back-to-top').click(function () {
			$("html, body").animate({
				scrollTop: 0
			}, 600);
			return false;
		});
	});


	/* ..............................................
	   Slider Range
	   ................................................. */

$(function () {
  const slider = $("#slider-range");
  const minInput = $("#min_price");
  const maxInput = $("#max_price");

  const selectedMin = parseInt(slider.data("selected-min")) || 1000;
  const selectedMax = parseInt(slider.data("selected-max")) || 3000;

  slider.slider({
    range: true,
    min: 0,
    max: 10000,
    values: [selectedMin, selectedMax],
    slide: function (event, ui) {
      $("#amount").val("$" + ui.values[0] + " - $" + ui.values[1]);
      minInput.val(ui.values[0]);
      maxInput.val(ui.values[1]);
    }
  });

  $("#amount").val("$" + selectedMin + " - $" + selectedMax);
});



	/* ..............................................
	   Filter and AJAX Load
	   ................................................. */

	$(document).on('click', '.category-link', function(e) {
		e.preventDefault();
		const url = $(this).attr('href');
		const $this = $(this);

		$.ajax({
			type: 'GET',
			url: url,
			headers: {
				'X-Requested-With': 'XMLHttpRequest'
			},
			success: function(response) {
				const $newHtml = $(response);
				const newProducts = $newHtml.find('#product-list-container');
				const currentProducts = $('#product-list-container');

				if (newProducts.length) {
					currentProducts.html(newProducts.html());
				}

				$('.category-link').removeClass('active');
				$this.addClass('active');

				history.pushState(null, '', url);
			},
			error: function(xhr, status, error) {
				console.error('Error loading products:', error);
			}
		});
	});

	$(document).on('change', 'input[name="occasion"]', function() {
		const params = new URLSearchParams(window.location.search);
		params.delete('occasion');
		$('input[name="occasion"]:checked').each(function() {
			params.append('occasion', $(this).val());
		});

		const currentUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');

		$.ajax({
			type: 'GET',
			url: currentUrl,
			headers: {
				'X-Requested-With': 'XMLHttpRequest'
			},
			success: function(response) {
				const $newHtml = $(response);
				const newProducts = $newHtml.find('#product-list-container');
				const currentProducts = $('#product-list-container');

				if (newProducts.length) {
					currentProducts.html(newProducts.html());
				}

				history.pushState(null, '', currentUrl);
			},
			error: function(xhr, status, error) {
				console.error('Error loading occasion products:', error);
			}
		});
	});

	window.addEventListener('popstate', function() {
		location.reload();
	});

}(jQuery));


