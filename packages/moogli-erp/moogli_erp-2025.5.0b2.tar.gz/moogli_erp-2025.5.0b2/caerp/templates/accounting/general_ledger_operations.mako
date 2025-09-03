<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
  <div class="layout flex main_actions">
    <div class="btn-group"><!-- pas de boutons principaux --></div>
    <div class="btn-group">
      <%
        ## We build the link with the current search arguments
        args = request.GET
        url_csv = request.route_path('grand_livre.{extension}', extension='csv', id=request.context.id, _query=args)
        url_xls = request.route_path('grand_livre.{extension}', extension='xls', id=request.context.id, _query=args)
        url_ods = request.route_path('grand_livre.{extension}', extension='ods', id=request.context.id, _query=args)
        %>
      <a class='btn icon_only_mobile' href='${url_csv}' title="Exporter les éléments de la liste au format csv" aria-label="Exporter les éléments de la liste au format csv">
        ${api.icon("file-csv")}
        CSV
      </a>
      <a class='btn icon_only_mobile' href='${url_xls}' title="Exporter les éléments de la liste au format Excel (xlsx)" aria-label="Exporter les éléments de la liste au format Excel (xlsx)">
        ${api.icon("file-excel")}
        Excel
      </a>
      <a class='btn icon_only_mobile' href='${url_ods}' title="Exporter les éléments de la liste au format Open Document (ods)" aria-label="Exporter les éléments de la liste au format Open Document (ods)">
        ${api.icon("file-spreadsheet")}
        ODS
      </a>
    </div>
  </div>
</div>
</%block>



<%block name='content'>

${searchform()}

<div>
    <div>${records.item_count} Résultat(s)</div>
    <div class='table_container'>
    % if records:
        <table class="hover_table">
            <thead>
                <tr>
                    <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                    <th scope="col">${sortable("Compte général", "general_account")}</th>
                    <th scope="col" class="col_text">Nom du compte</th>
                    <th scope="col" class="col_date">${sortable("Date", "date")}</th>
                    <th scope="col" class="col_text">Libellé</th>
                    <th scope="col" class="col_number">Débit</th>
                    <th scope="col" class="col_number">Crédit</th>
                    <th scope="col" class="col_number">Solde</th>
                </tr>
            </thead>
            <tbody>
			% for entry in records:
				<tr class='tableelement operation-associated-${bool(entry.company_id)}' id='${entry.id}'>
					<td class="col_status">
						% if entry.company_id:
							<span class="icon status valid" title="Écritures associées à une enseigne" aria-label="Écritures associées à une enseigne">
                                ${api.icon('link')}
							</span>
						% else:
							<span class="icon status caution" title="Écritures n’ayant pas pu être associées à une enseigne" aria-label="Écritures n’ayant pas pu être associées à une enseigne">
                                ${api.icon('exclamation-triangle')}
							</span>
						% endif
					</td>
					<td>${entry.general_account}</td>
                    <td
                    class="col_text">${get_wording_dict().get(entry.general_account, '')}</td>
					<td class="col_date">${api.format_date(entry.date)}</td>
					<td class="col_text">${entry.label}</td>
					<td class="col_number">${api.format_float(entry.debit, precision=2)|n} €</td>
					<td class="col_number">${api.format_float(entry.credit, precision=2)|n} €</td>
					<td class="col_number">${api.format_float(entry.balance, precision=2)|n} €</td>
				</tr>
			% endfor
            </tbody>
        </table>
    % else:
        <table>
	        <tbody>
                <tr>
                    <td class='col_text'><em>Aucun fichier n’a été traité</em></td>
                </tr>
            </tbody>
        </table>
    % endif
    </div>
    ${pager(records)}
</div>
</%block>
