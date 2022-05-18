const API_ADDRESS = ''

function render(achievements) {
  $('#achievements').empty();
  achievementsList = JSON.parse(achievements);
  achievementsList.forEach(e => {
    const icon = e.achieved == '1' ? e.icon : e.icongray;
    $('#achievements').append(`<div id="${e.apiname}"></div>`);
    achievement = $(`#${e.apiname}`);
    achievement.append(`<img src='${icon}'>`);
    achievement.addClass('achievement');
    achievement.attr("data-title", e.displayName);
    achievement.attr("data-description", e.description.replace(/\.$/, ''));
    achievement.attr('data-percentage', Math.round(e.percent * 1000)/1000)
    if(e.achieved == '1') achievement.addClass('achieved');
    if(e.hidden == '1') achievement.addClass('hidden');
  });
  filter_achievements();
}

function filter_achievements() {
  const term = $('#text_filter').val();
  $('#achievements div.achievement').removeClass('filtered');
  if(term != '') {
    $(`#achievements div.achievement:not([data-title*=${term} i], [data-description*=${term} i])`).addClass('filtered');
  }
}

function retrieve_achievements_for_player() {
  const player_id = $('#player_id').val();
  $.get(API_ADDRESS + '/achievements/' + player_id)
    .done(render)
    .fail(() => $('#achievements').text('Achievements failed to retrieve.'));
}

function readyFn() {
  $('#text_filter').on('input', filter_achievements);
  $('#player_id').on('input', retrieve_achievements_for_player);
  retrieve_achievements_for_player();
}

$(document).ready(readyFn);
