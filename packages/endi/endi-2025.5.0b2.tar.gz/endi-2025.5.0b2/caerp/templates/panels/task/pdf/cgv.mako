<%namespace file="/base/utils.mako" import="format_text" />
% if cae_cgv or company_cgv:
<div class='cgv-container'>
    % if cae_cgv:
        <div id="cgv" class='pdf_cgv'>
            ${format_text(cae_cgv, False)}
        </div>
    % endif
    % if company_cgv:
        <div class='pdf_cgv'>
            ${format_text(company_cgv, False)}
        </div>
    % endif
</div>
% endif
