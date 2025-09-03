<%namespace file="/base/utils.mako" import="format_text" />
<footer class='workshop_footer'>
% if has_img:
<div class="pdf_footer_img">
    <img src="${img_url}" alt="Logo de pied de page" />
</div>
% endif
% if has_text:
<div class='row pdf_footer'>
${format_text(text)}
</div>
% endif
</footer>

