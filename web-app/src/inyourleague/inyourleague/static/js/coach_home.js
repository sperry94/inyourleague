$(function() {
  $('.teamcard').click(function (e) {
    $('.teamcard').removeClass('border-dark');

    // show the events for that team only

    $(e.target).closest('.teamcard').addClass('border-dark');
  })
});