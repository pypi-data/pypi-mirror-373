<%inherit file="${context['main_template'].uri}" />

<%block name="mainblock">
<div id="task_preview_tab" class="layout flex content_vertical_padding limited_width width60 pdf_viewer">
    <div class="preview">
        <div class="pdfpreview">
            <!-- App Mn TaskPreview.js -->
        </div>
    </div>
</div>
<script>
    $(() => pdf_preview.render('${url}', showControls=false));
</script>
</%block>
