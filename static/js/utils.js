$(document).ready(function(){
	// Hide details
	$(".details").hide();
	//$(".hide-details").hide();
		
	$(".show-details").click(function(){
		$(this).next(".details").slideToggle("slow");
		return false;
	});	
});

$(document).ready(function(){
	
	$(".accordion h3:first").addClass("active");
	$(".accordion div:not(:first)").hide();

	$(".accordion h3").click(function(){
		$(this).next("div").slideToggle("slow")
		.siblings("div:visible").slideUp("slow");
		$(this).toggleClass("active");
		$(this).siblings("h3").removeClass("active");
	});

});

$(document).ready(function() {
		$('.datepicker').datepicker();
	});
