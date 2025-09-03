<%doc>
Submit buttons for special form renderings
</%doc>
<button type="${elem.type_}" name="${elem.name}" value="${elem.value}"
    title="${elem.title}" aria-label="${elem.title}"
% if elem.js:
    onclick="${elem.js}"
% endif
% if elem.css:
 class="${elem.css}"
% endif
>
% if elem.icon:
% if hasattr(elem.icon, "__iter__"):
% for icon in elem.icon:
    ${api.icon(icon)}
% endfor
% else:
    ${api.icon(elem.icon)}
% endif
% endif
${elem.label}
</button>
