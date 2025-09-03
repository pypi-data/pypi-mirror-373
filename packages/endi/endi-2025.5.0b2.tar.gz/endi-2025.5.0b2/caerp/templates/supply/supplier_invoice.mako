<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_text" />
<%namespace file="/base/utils.mako" import="format_js_appoptions" />
<%block name="headtitle">
    ${request.layout_manager.render_panel('task_title_panel', title=title)}
</%block>
<%block name='actionmenucontent'>
    <div class='main_toolbar action_tools' id='js_actions'></div>
</%block>
<%block name="beforecontent">
    <% supplier_invoice = request.context %>
    <% multi_order = len(supplier_invoice.supplier_orders) > 1 %>
    <div>
	    <div class='layout flex two_cols hidden-print'>
            <div>
                <h3>
                    <span class="icon status ${supplier_invoice.global_status}">
                        ${api.icon(api.status_icon(supplier_invoice))}
                    </span>
                    ${api.format_status_sentence(supplier_invoice)}
                </h3>
                <ul class="document_summary content_vertical_padding">
                    <li class="hidden-print">
                        ${api.format_supplier_invoice_status(supplier_invoice)}
                    </li>
                    <li>
                    Fournisseur :
                    % if supplier_invoice.supplier:
                        <a
                            href="${request.route_path('supplier', id=supplier_invoice.supplier_id)}"
                            title="Voir le fournisseur"
                            aria-label="Voir le fournisseur"
                            ## Used in supplier_invoice MainView.js
                            data-backbone-var="supplier_id"
                            >${supplier_invoice.supplier.label}</a>
                    % else:
                    Indéfini
                    % endif
                    </li>
                    % if internal_source_document_link:
                    <li>
                    ${request.layout_manager.render_panel(internal_source_document_link.panel_name, context=internal_source_document_link)}
                    </li>
                    % endif
                    

                    % if api.has_permission('global.manage_accounting'):
                        % if supplier_invoice.status == 'valid':
                            <li>
                                Numéro de pièce :
                                <strong>${supplier_invoice.official_number}</strong>
                            </li>
                        % endif
                        <li>
                            % if supplier_invoice.exported:
                                Ce document a déjà été exporté vers le
                                logiciel de comptabilité
                                % if supplier_invoice.exports:
                                    <ul>
                                    % for export in supplier_invoice.exports:
                                        <li>Exporté le
                                        ${api.format_datetime(export.datetime)}
                                        par ${api.format_account(export.user)}
                                        </li>
                                    % endfor
                                    </ul>
                                % endif
                            % else:
                                Ce document n'a pas encore été exporté vers le logiciel de comptabilité
                            % endif
                        </li>
                    % endif
                </ul>
            </div>
            <!-- will get replaced by backbone -->
            <div class="status_history"></div>
        </div>
    </div>
</%block>
<%block name='content'>
    <div id="js-main-area"></div>
</%block>
<%block name='footerjs'>
${format_js_appoptions(js_app_options)}
</%block>
