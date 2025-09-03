<%inherit file="${context['main_template'].uri}" />

<%block name='mainblock'>
<% invoice = request.context %>
    <div id="invoice_accounting_tab">
        <% url=request.route_path('/export/treasury/invoices/{id}', id=invoice.id, _query={'force': True}) %>
            % if invoice.exported:
            <div class='content_vertical_padding'>
                <span class="icon status valid">${api.icon('check')}</span>
                Cette facture a été exportée vers la comptabilité.
            </div>
            % if invoice.exports:
            <div class='content_vertical_padding'>
                <ul>
                    % for export in invoice.exports:
                    <li>Exporté le ${api.format_datetime(export.datetime)}
                        par ${api.format_account(export.user)}</li>
                    % endfor
                </ul>
            </div>
            % endif
            % if api.has_permission('global.manage_accounting'):
            <div class='content_vertical_padding'>
                <a class='btn' href="${url}">
                    ${api.icon('file-export')}
                    Forcer la génération d’écritures pour cette facture
                </a>
            </div>
            % endif
            % else:
            <div class='content_vertical_padding'>
                <span class="icon status neutral">${api.icon('clock')}</span>
                Cette facture n'a pas encore été exportée vers la comptabilité
            </div>
            % if api.has_permission('global.manage_accounting'):
            <div class='content_vertical_padding'>
                <a class='btn btn-primary' href="${url}">
                    ${api.icon('file-export')}
                    Générer les écritures pour cette facture
                </a>
            </div>
            % endif
            % endif
    </div>
</%block>