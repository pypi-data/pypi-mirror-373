<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="company_list_badges"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <div role='group'></div>
        <div role='group'>
            <a class='btn' href='${export_xls_url}' title="Export au format Excel (xlsx)" aria-label="Export au format Excel (xlsx)">
                ${api.icon('file-excel')} Excel
            </a>
            <a class='btn' href='${export_ods_url}' title="Export au format Open Document (ods)" aria-label="Export au format Open Document (ods)">
                ${api.icon('file-spreadsheet')} ODS
            </a>
        </div>
    </div>
</div>
</%block>

<%block name='content'>

<div class='search_filters'>
    ${form|n}
</div>

<%
# Compute totals
total_amount = 0
total_tva_amount = 0
for data in records:
    total_amount += data.amount
    total_tva_amount += data.amount * (max(data.tva.value,0)/10000)
%>
    
<div>
    <div class="table_container scroll_hor">
        <button class="fullscreen_toggle small" title="Afficher le tableau en plein écran" aria-label="Afficher le tableau en plein écran" onclick="toggleTableFullscreen(this);return false;">
            ${api.icon('expand')}
            ${api.icon('compress')}
            <span>Plein écran</span>
        </button>
        <table class="hover_table">
            <thead>
                <tr>
                    <th scope="col" class="col_date">Date</th>
                    <th scope="col" class="col_text">Enseigne</th>
                    <th scope="col" class="col_text">Facture</th>
                    <th scope="col" class="col_text">Client</th>
                    <th scope="col" class="col_text">Mode</th>
                    <th scope="col" class="col_number">Montant</th>
                    <th scope="col" class="col_number">Taux TVA</th>
                    <th scope="col" class="col_number">Montant TVA</th>
                </tr>
                <tr class="row_recap">
                    <th class="col_text min10" colspan=5>TOTAL (${records.count()} encaissements)</th>
                    <th class="col_number">${api.format_amount(total_amount, precision=5)}&nbsp;€</th>
                    <th class="col_number">&nbsp;</th>
                    <th class="col_number">${api.format_amount(total_tva_amount, precision=5)}&nbsp;€</th>
                </tr>
            </thead>
            <tbody>
                % for data in records:
                    <tr>
                        <td class="col_date">${api.format_date(data.date)}</td>
                        <td class="col_text">
                            <% company_url = request.route_path('/companies/{id}', id=data.invoice.company.id) %>
                            <a href="${company_url}">${data.invoice.company.full_label}</a> 
                            <small>${company_list_badges(data.invoice.company)}</small>
                        </td>
                        <td class="col_text document_number">
                            <a href="${api.task_url(data.invoice)}">${data.invoice.official_number}</a>
                        </td>
                        <td class="col_text">${data.invoice.customer.label}</td>
                        <td class="col_text">${data.mode}</td>
                        <td class="col_number">${api.format_amount(data.amount, precision=5)}&nbsp;€</td>
                        <td class="col_number">
                            <small>${api.format_float(data.tva.rate, 2)}&nbsp;%</small>
                        </td>
                        <td class="col_number">
                            ${api.format_amount(data.get_tva_amount(), precision=5)}&nbsp;€
                        </td>
                    </tr>
                % endfor
            </tbody>
        </table>
    </div>
</div>

</%block>
