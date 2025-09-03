<div class='header'>
    <h4>Factures & Avoirs</h4>
</div>

<div class="separate_bottom">
    <div class="table_container">
        <table class='hover_table'>
            % if invoices:
            <thead>
                <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                <th scope="col" class="col_number">Numéro</th>
                <th scope="col" class="col_text">Nom</th>
                <th scope="col" class="col_text">État</th>
                <th scope="col" class="col_text">Fichiers attachés</th>
                <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
            </thead>
            % endif
            <tbody>
                % if invoices:
                    % for invoice in invoices:
                        <% url = api.task_url(invoice) %>
		                <% onclick = "document.location='{url}'".format(url=url) %>
                		<% tooltip_title = f"Cliquer pour voir la facture « { invoice.name} »" %>
                        <tr>
                            <td class="col_status" title="${api.format_status(invoice)} - ${tooltip_title}"  onclick="${onclick}">
                                <span class="icon status ${invoice.global_status}">
                                	${api.icon(api.status_icon(invoice))} 
                                </span>
                            </td>
                            <td class="col_number document_number" onclick="${onclick}" title="${tooltip_title}">${invoice.official_number}</td>
                            <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${invoice.name}</td>
                            <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${api.format_status(invoice)}</td>
                            <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                                % if getattr(invoice, 'estimation', None) or getattr(invoice, 'cancelinvoices', None) or getattr(invoice, 'invoice', None):
                                    <ul>
                                        % if getattr(invoice, 'estimation', None):
                                            <li>
                                                Devis ${invoice.estimation.name}
                                                % if invoice.estimation.official_number:
                                                    &nbsp;(${invoice.estimation.official_number})
                                                % endif
                                            </li>
                                        % endif
                                        % if getattr(invoice, 'cancelinvoices', None):
                                            % for cancelinvoice in invoice.cancelinvoices:
                                                <li>
                                                    Avoir ${cancelinvoice.name}
                                                    % if cancelinvoice.official_number:
                                                        &nbsp;(${cancelinvoice.official_number})
                                                    % endif
                                                </li>
                                            % endfor
                                        % endif
                                        % if getattr(invoice, 'invoice', None):
                                            <li>
                                                Facture ${invoice.invoice.name}
                                                % if invoice.invoice.official_number:
                                                    &nbsp;(${invoice.invoice.official_number})
                                                % endif
                                            </li>
                                        % endif
                                    </ul>
                                % endif
                            </td>
                            <td class='col_actions width_one'>
                                ${request.layout_manager.render_panel(
                                  'menu_dropdown',
                                  label="Actions",
                                  links=stream_actions(request, invoice),
                                )}
                            </td>
                        </tr>
                    % endfor
                %else:
                    <tr>
                        <td colspan="6" class="col_text"><em>Aucune facture n'a été créée</em></td>
                    </tr>
                % endif
            </tbody>
            % if api.has_permission('context.add_invoice'):
                <tfoot>
                    <td colspan="6" class='col_actions'>
                        <a class='btn' href="${add_url}">
                            ${api.icon('plus')} 
                            Créer une facture
                        </a>
                    </td>
                </tfoot>
            % endif
        </table>
    </div>
</div>
