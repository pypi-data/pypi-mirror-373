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
                <th scope="col">&nbsp;</th>
                <th scope="col">${sortable("Demandé le", "status_date")}</th>
                <th scope="col">${sortable("Enseigne", "company")}</th>
                <th scope="col">${sortable("Nom du document", "internal_number")}</th>
                <th scope="col">${sortable("Date", "date")}</th>
                <th scope="col">${sortable("Client", "customer")}</th>
                <th scope="col">${sortable("HT", "ht")}</th>
                <th scope="col">${sortable("TVA", "tva")}</th>
                <th scope="col">${sortable("TTC", "ttc")}</th>
                <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
            </thead>
            % endif
            <tbody>
                % if records:
                    % for document in records:
                        <% company = document.get_company() %>
                        <% task_url = api.task_url(document, _query={'come_from': request.current_route_path()}) %>
                        <% tooltip_title = "Cliquer pour voir le document « " + document.name + " »" %>

                        <tr class='status status-${document.status}'>
                            <td class="col_status" title="${api.format_status(document)}">
                                <span class="icon status ${document.global_status}">
                                    ${api.icon(api.status_icon(document))}
                                </span>
                            </td>
                            <td class="col_date">${api.format_date(document.status_date)}</td>
                            <td class="col_text">
                                <a href="${request.route_path('/companies/{id}', id=company.id)}" title="Cliquer pour voir l'enseigne « ${company.full_label} »" aria-label="Cliquer pour voir l'enseigne « ${company.full_label} »">${company.full_label}</a>
                            </td>
                            <td class="col_text">
                                <a href="${task_url}" title="${tooltip_title}" aria-label="${tooltip_title}">
                                    ${document.name} (<small>${document.get_short_internal_number()}</small>)
                                </a>
                                ${request.layout_manager.render_panel('business_type_label', document.business_type)}
                                <small class="description">${format_text(document.description)}</small>
                            </td>
                            <td class="col_date">${api.format_date(document.date)}</td>
                            <td class="col_text">
                                <a href="${request.route_path('/customers/{id}', id=document.customer.id)}" title="Cliquer pour voir le client « ${document.customer.label} »" aria-label="Cliquer pour voir le client « ${document.customer.label} »">${document.customer.label}</a>
                            </td>
                            <td class="col_number"><strong>${api.format_amount(document.ht, precision=5)}&nbsp;€</strong></td>
                            <td class="col_number">${api.format_amount(document.tva, precision=5)}&nbsp;€</td>
                            <td class="col_number">${api.format_amount(document.ttc, precision=5)}&nbsp;€</td>
                            <td class="col_actions width_one">
                                <a class="btn icon only" href="${task_url}" title="${tooltip_title}" aria-label="${tooltip_title}">${api.icon("arrow-right")}</a>
                            </td>
                        </tr>
                    % endfor
                % else:
                    <tr><td class='col_text' colspan='10'>
                        <em>
                        % if 'estimation' in task_types:
                            Aucun devis
                        %else:
                            Aucune facture
                        % endif
                         en attente de validation 
                        % if '__formid__' in request.GET:
                            correspondant à ces critères
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
