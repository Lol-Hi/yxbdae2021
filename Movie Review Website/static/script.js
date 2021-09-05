$( document ).ready( function() {
  // Check rating entered
  $(".stars").click( function() {
    var rating = $(this).val(); //Retrieve the rating provided by the user from the stars
    $('#hidden-stars').val(rating); //Transfer the rating to the hidden field
    //To achieve the effect that all the stars before the selected star are active
    //while those that are after the selected star are not
    if (rating >= 1) {
      //Active for any rating higher than or equal to 1
      $('#1-label').addClass('active');
      $('#1-star').prop('checked', true);
    } else {
      //Not active for anything less than 1 (doesn't really happen though)
      $('#1-label').removeClass('active');
      $('#1-star').prop('checked', false);
    };
    if (rating >= 2) {
      //Active for any rating higher than or equal to 2
      $('#2-label').addClass('active');
      $('#2-star').prop('checked', true);
    } else {
      //Not active for anything less than 2
      $('#2-label').removeClass('active');
      $('#2-star').prop('checked', false);
    };
    if (rating >= 3) {
      //Active for any rating higher than or equal to 3
      $('#3-label').addClass('active');
      $('#3-star').prop('checked', true);
    } else {
      //Not active for anything less than 3
      $('#3-label').removeClass('active');
      $('#3-star').prop('checked', false);
    };
    if (rating >= 4) {
      //Active for any rating higher than or equal to 4
      $('#4-label').addClass('active');
      $('#4-star').prop('checked', true);
    } else {
      //Not highlighted for anything less than 4
      $('#4-label').removeClass('active');
      $('#4-star').prop('checked', false);
    };
    if (rating >= 5) {
      //Active for any rating higher than or equal to 5
      $('#5-label').addClass('active');
      $('#5-star').prop('checked', true);
    } else {
      //Not highlighted for anything less than 5
      $('#5-label').removeClass('active');
      $('#5-star').prop('checked', false);
    };
    if (rating >= 6) {
      //Active for any rating higher than or equal to 6
      $('#6-label').addClass('active');
      $('#6-star').prop('checked', true);
    } else {
      //Not highlighted for anything less than 6
      $('#6-label').removeClass('active');
      $('#6-star').prop('checked', false);
    };
    if (rating >= 7) {
      //Active for any rating higher than or equal to 7
      $('#7-label').addClass('active');
      $('#7-star').prop('checked', true);
    } else {
      //Not highlighted for anything less than 7
      $('#7-label').removeClass('active');
      $('#7-star').prop('checked', false);
    };
    if (rating >= 8) {
      //Active for any rating higher than or equal to 8
      $('#8-label').addClass('active');
      $('#8-star').prop('checked', true);
    } else {
      //Not highlighted for anything less than 8
      $('#8-label').removeClass('active');
      $('#8-star').prop('checked', false);
    };
    if (rating >= 9) {
      //Active for any rating higher than or equal to 9
      $('#9-label').addClass('active');
      $('#9-star').prop('checked', true);
    } else {
      //Not highlighted for anything less than 9
      $('#9-label').removeClass('active');
      $('#9-star').prop('checked', false);
    };
    if (rating == 10) {
      //Active for any rating higher than or equal to 10
      $('#10-label').addClass('active');
      $('#10-star').prop('checked', true);
    } else {
      //Not highlighted for anything less than 10
      $('#10-label').removeClass('active');
      $('#10-star').prop('checked', false);
    };
  });
});
