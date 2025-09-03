/*
    Script to exec on default layout pages startup (not OPA)
*/

function format_company_select_labels(state) {
    /*
        N'affiche que le texte avant le premier '##'
        dans les items du sélecteur d'enseigne
        (ce qui est après ne sert que pour rechercher)
    */
    return state.text.split("##")[0];
}

$(function () {

    // Popups initialisation
    $('.caerp-utils-widgets-popup').each(function () {
        setPopUp($(this).attr("id"), $(this).attr("data-title"));
    });

    // Initialisation of company select menu (if needed)
    var company_select_tag = $('#company-select-menu');
    if (!_.isUndefined(company_select_tag)) {
        company_select_tag.select2({
            templateSelection: format_company_select_labels,
            templateResult: format_company_select_labels,
            language: $.fn.select2.amd.require("select2/i18n/fr"),
        });
        company_select_tag.change(
            function () { window.location = $(this).val(); }
        );
    }

    // Handle size of the main menu (mini/maxi)
    if (getCookie('caerp__menu_mini') == "true") {
        resize("menu", document.getElementById('menu_size_btn'));
    }

    // Keep user menu open if needed
    $('#user_menu:has(.current_item)').show();

    // Hack to prevent deform sequence widgets to display title twice
    $('.deform-seq').prev('label').hide();

    // Hack to open the dropdown that contain the current menu
    $('.current_item').parent().siblings('button').click();

    // End of page loading
    removeClass(document.body, 'preload');

});
