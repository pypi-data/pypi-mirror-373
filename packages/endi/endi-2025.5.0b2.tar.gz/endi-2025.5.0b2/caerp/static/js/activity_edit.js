// Handles automatic record of activity form

$(function() {
    var previous_record = ""
    var delay = 10000 // 10s
    var previous_record_date = new Date()

    $("#icn-terminate").click(function() {
        $("#record_formclosed").click();
    })
    $("#icn-save").click(function() {
        $("#record_formrecord").click();
    })
    $("#icn-pdf").click(function() {
        $("#record_formpdf").click();
    })
                         
    window.setTimeout(sendForm, delay);  // every 60s

    function sendForm() {
        // get the action-url of the form
        var actionurl = $("#record_form").attr("action");

        // do your request an handle the results
        tinyMCE.triggerSave(true);

        // simulate record button press
        var record = $("#record_form").serialize() + "&record=record"

        if (record == previous_record) {
            console.log("no changes")
            window.setTimeout(sendForm, delay)
            return
        }

        $.ajax({
            url: actionurl,
            type: 'post',
            dataType: 'html',
            data: record,
            success: function(data) {
                console.log("automatic record ok")
                previous_record = record
                window.setTimeout(sendForm, delay)

                previous_record_date = new Date()
                let locale_date = previous_record_date.toLocaleDateString()
                let locale_time = previous_record_date.toLocaleTimeString()
                status_line = `Sauvegarder et continuer\nCe rendez-vous est enregistré automatiquement.\nDernier enregistrement le  ${locale_date} à ${locale_time}.`

                $('#icn-save').attr('title', status_line)
                $('#icn-save').attr('aria-label', status_line)
            },
            error: function(data) {
                console.log("automatic record ko")
                window.setTimeout(sendForm, delay)

                let locale_date = previous_record_date.toLocaleDateString()
                let locale_time = previous_record_date.toLocaleTimeString()
                status_line = `Sauvegarder et continuer\nÉchec du dernier enregistrement.\nDernier enregistrement réussi le ${locale_date} à ${locale_time}.`

                $('#icn-save').attr('title', status_line)
                $('#icn-save').attr('aria-label', status_line)
            }
        });
    }
})
