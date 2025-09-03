   <div class="content_vertical_padding">
        <div class="timeline">
            <ul>
                % for item in items:
                    ${request.layout_manager.render_panel(
                        "timeline_item", 
                        context=item, 
                        business=request.context
                    )}
                % endfor
            </ul>
        </div>
    </div>
