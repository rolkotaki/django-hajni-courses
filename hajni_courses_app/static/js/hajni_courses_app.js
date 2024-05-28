/**
 * Sets the style of the active navigation menu item to active.
 */
$(document).ready(function() {
    $('#topnav a').click(function(e) {
        $('#topnav a').removeClass('active_menu');
        $('#topnav button').removeClass('active_menu');
        if (['nav_personal_data'].includes($(this).attr('id'))) {
            sessionStorage.setItem('active_menu', 'user_dropdown_button');
        } else {
            sessionStorage.setItem('active_menu', $(this).attr('id'));
        }
    });
    const activeMenuId = sessionStorage.getItem('active_menu');
    $('#' + activeMenuId).addClass('active_menu');
});
