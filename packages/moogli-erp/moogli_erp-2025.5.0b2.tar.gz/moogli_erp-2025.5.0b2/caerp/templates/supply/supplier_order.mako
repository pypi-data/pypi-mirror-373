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
    <% supplier_order = request.context %>
    <div>
	    <div class='layout flex two_cols hidden-print'>
            <div>
                <h3>
                    ${request.layout_manager.render_panel('status_title', context=request.context)}
                </h3>
                <ul class="document_summary content_vertical_padding">
                    <li>
                    Fournisseur :
                    % if supplier_order.supplier:
                        <a
                            href="${request.route_path('supplier', id=supplier_order.supplier_id)}"
                            title="Voir le fournisseur"
                            aria-label="Voir le fournisseur"
                            ## Used in supplier_order MainView.js
                            data-backbone-var="supplier_id"
                            >${supplier_order.supplier.label}</a>
                    % else:
                    Indéfini
                    % endif
                    </li>
                    </li>
                    % if supplier_order.status == 'valid':
                    <li>
                    Facture fournisseur :
                        % if supplier_order.supplier_invoice:
                            <% invoice = supplier_order.supplier_invoice %>
                            <a href="${request.route_path('/supplier_invoices/{id}', id=invoice.id)}">
                                ${invoice.name} de ${api.format_amount(invoice.total)}&nbsp;€
                            </a>
                        % else:
                            Aucune pour l'instant
                        % endif
                    </li>
                    % endif
                    % if supplier_order.internal and api.has_permission('company.view', supplier_order.source_estimation):
                    <li>
                    Devis interne associé :
                        <a
                            href="${request.route_path('/estimations/{id}/general', id=supplier_order.source_estimation.id)}"
                            title="Voir le devis associé"
                            aria-label="Voir le devis associé"
                            >${supplier_order.source_estimation.name}</a>
                    </li>
                    % endif
                </ul>
            </div>
            <!-- will get replaced by backbone -->
            <div class="status_history"></div>
        </div>
</%block>
<%block name='content'>
    <div id="js-main-area"></div>
</%block>
<%block name='footerjs'>
${format_js_appoptions(js_app_options)}
</%block>
