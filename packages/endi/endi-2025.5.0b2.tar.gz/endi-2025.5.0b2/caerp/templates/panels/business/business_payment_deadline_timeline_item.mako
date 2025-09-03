## Business PPayment deadline représenté comme item d'une timeline
## Context : WrappedDeadline
## 
<li
% if wrapped_deadline.is_sold:
class='pay_off'
% endif
> 
    <blockquote class="${status_css} ${time_css}">
        <span class="icon status ${status_css}" role="presentation">
            ${api.icon(icon)}
        </span>
        <div>
        % for link in more_links:
            ${request.layout_manager.render_panel(link.panel_name, context=link)}
        % endfor
            <h5>
                ${title}
            </h5>
            <div class="layout flex">
            <p>
               ${description | n} 
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