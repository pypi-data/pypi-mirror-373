<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="format_text"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        <table class="top_align_table hover_table">
            % if records:
            <thead>
                <th scope="col" class="col_status col_text"></th>
                <th scope="col">${sortable("Demandé le", "status_date")}</th>
                <th scope="col" class="col_text">${sortable("Enseigne", "company")}</th>
                <th scope="col">${sortable("Date", "date")}</th>
                <th scope="col" class="col_text">${sortable("N° de facture du fournisseur", "remote_invoice_number")}</th>
                <th scope="col" class="col_text">${sortable("Fournisseur", "supplier")}</th>
                <th scope="col" class="col_number">HT</th>
                <th scope="col" class="col_number">TVA</th>
                <th scope="col" class="col_number">TTC</th>
                <th scope="col" class="col_number" title="Part réglée par la CAE">${sortable("Part CAE", "cae_percentage")}</th>
                <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
            </thead>
            % endif
            <tbody>
                % if records:
                    % for supplier_invoice in records:
                        <% company = supplier_invoice.company %>
                        <% url = request.route_path('/supplier_invoices/{id}', id=supplier_invoice.id, _query={'come_from': request.current_route_path()}) %>
                        <% tooltip_title = "Cliquer pour voir cette commande" %>

                        <tr class='tableelement' id="${supplier_invoice.id}">
                            <td class="col_status" title="${api.format_status(supplier_invoice)}">
                                <span class="icon status ${supplier_invoice.status}">
                                    ${api.icon(api.status_icon(supplier_invoice))}
                                </span>
                            </td>
                            <td class="col_date">${api.format_date(supplier_invoice.status_date)}</td>
                            <td class="col_text">
                                <a href="${request.route_path('/companies/{id}', id=company.id)}" title="Cliquer pour voir l'enseigne « ${company.full_label} »" aria-label="Cliquer pour voir l'enseigne « ${company.full_label} »">${company.full_label}</a>
                            </td>
                            <td class="col_date">${api.format_date(supplier_invoice.date)}</td>
                            <td class="col_text">
                                <a href="${url}" title="${tooltip_title}" aria-label="${tooltip_title}">${supplier_invoice.remote_invoice_number}</a>
                            </td>
                            <td class="col_text">${supplier_invoice.supplier.label}</td>
                            <td class="col_number">${api.format_amount(supplier_invoice.total_ht)}&nbsp;€</td>
                            <td class="col_number">${api.format_amount(supplier_invoice.total_tva)}&nbsp;€</td>
                            <td class="col_number">${api.format_amount(supplier_invoice.total)}&nbsp;€</td>
                            <td class="col_number">${supplier_invoice.cae_percentage}&nbsp;%</td>
                            <td class="col_actions width_one">
                                <a class="btn icon only" href="${url}" title="${tooltip_title}" aria-label="${tooltip_title}">${api.icon("arrow-right")}</a>
                            </td>
                        </tr>
                    % endfor
                % else:
                    <tr><td class='col_text' colspan='11'>
                        <em>
                        % if '__formid__' in request.GET:
                            Aucune facture fournisseur en attente de validation correspondant à ces critères
                        % else:
                            Aucune facture fournisseur en attente de validation
                        % endif
                        </em>
                    </td></tr>
                % endif
            </tbody>
        </table>
    </div>
    ${pager(records)}
</div>
</%block>
