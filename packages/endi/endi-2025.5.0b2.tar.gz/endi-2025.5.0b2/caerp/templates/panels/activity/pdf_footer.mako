<%namespace file="/base/utils.mako" import="format_text" />
<footer class='activity_footer'>
% if has_img:
<img src="${img_url}" />
% endif
% if has_text:
<div class='row pdf_footer'>
${format_text(text)}
</div>
% endif
</footer>
