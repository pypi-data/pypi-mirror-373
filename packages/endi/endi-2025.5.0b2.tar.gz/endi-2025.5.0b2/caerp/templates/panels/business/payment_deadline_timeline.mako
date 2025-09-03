   % if items is not UNDEFINED and len(items) > 0:
   <div class="content_vertical_padding separate_top">
        % if estimation is not None:
            % if show_totals:
            <h3>Facturation du devis ${estimation.internal_number}</h3>
            <p>
                <em>
                    Reste à facturer : 
                    ${api.format_amount(to_invoice_ht, precision=5) | n}&nbsp;€ HT 
                    <small>(${api.format_amount(to_invoice_ttc, precision=5) | n}&nbsp;€ TTC)</small>
                </em>
            </p>
            % endif
        % else:
        <h3>Facturation sans devis</h3>
        % endif 
        <div class="timeline">
            <ul>
                % for item in items:
                    % if not getattr(item, "disabled", False):
                        ${request.layout_manager.render_panel(
                            "timeline_item", 
                            context=item, 
                            business=request.context
                        )}                    
                    % endif
                % endfor
            </ul>
        </div>
    </div>
    % endif
