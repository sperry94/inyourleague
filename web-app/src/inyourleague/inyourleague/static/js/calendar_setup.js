$(function() {
  $('#startTimeInput, #endTimeInput').val('');

  $('.iyl-datetimepicker').datetimepicker({
    icons: {
      time: 'far fa-clock',
      date: 'far fa-calendar',
      up: 'fa fa-arrow-up',
      down: 'fa fa-arrow-down'
    }
  });

  $('#calendarSection').fullCalendar({
    customButtons: {
      createEventButton: {
        text: 'Create Event',
        click: function() {
          $('#createEventModal').modal('show');
        }
      }
    },
    header : {
      left: 'title',
      right: 'createEventButton today, prev,next'
    },
    selectable: true,
    select: function (start, end) {
      console.log(start.format())
      $('#startTimeInput').val(start.format('MM/DD/YYYY hh:mm A'));
      // subtracting one day, as FullCalendar returns the subsequent day of the selection
      $('#endTimeInput').val(end.subtract(1, 'days').format('MM/DD/YYYY hh:mm A'));
    },
    unselect: function (start, end) {
      $('#startTimeInput, #endTimeInput').val('');
    },
    unselectCancel: '.fc-createEventButton-button, #createEventModal *',
    themeSystem: 'bootstrap4'
  });

  $('.teamcard').click(function (e) {
    const $selectedTeamCard = $(e.target).closest('.teamcard');

    const alreadySelected = $selectedTeamCard.hasClass('border-dark');

    $('.teamcard').removeClass('border-dark');

    // show the events for that team only

    if(!alreadySelected)
      $selectedTeamCard.addClass('border-dark');
  });
});