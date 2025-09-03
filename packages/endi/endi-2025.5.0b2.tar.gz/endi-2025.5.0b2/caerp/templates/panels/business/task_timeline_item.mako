## Task d'une affaire représenté dans la timeline
## Context : Task
## 
<li> 
    <blockquote class="${status_css}">
        <span class="icon status ${status_css}" role="presentation">
            ${api.icon(icon)}
        </span>
        <div>
            <h5>
            ${title}
            %if subtitle:
                <small>${subtitle}</small>
            %endif
            </h5>
            <div class='layout flex'>
                <p>
                    ${date_string | n} : 
                    ${api.format_amount(task.ht, precision=5) | n}&nbsp;€&nbsp;HT 
                    <small>(${api.format_amount(task.ttc, precision=5) | n}&nbsp;€&nbsp;TTC)</small>
                    <br />
                    ${description}
                </p>
                <div class="btn-container">
                % for link in main_links:
                    ${request.layout_manager.render_panel(link.panel_name, context=link)}
                % endfor
                </div>
            </div>
        </div>
    </blockquote>
</li>
