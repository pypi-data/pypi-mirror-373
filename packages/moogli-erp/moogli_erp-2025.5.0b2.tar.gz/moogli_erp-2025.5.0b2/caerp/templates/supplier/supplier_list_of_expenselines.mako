<%inherit file="${context['main_template'].uri}" />

<%block name='mainblock'>
<div class="table_container" id="expenselines_tab">

<%namespace file="/base/pager.mako" import="sortable"/>

% if records:
<table class="hover_table">
    <thead>
        <tr>
			<th scope="col" class="col_status col_text"></th>
            <th scope="col" class="col_date">${sortable("Date", "date")}</th>
            <th scope="col" class="col_text">${sortable("Type", "type")}</th>
            <th scope="col" class="col_number">HT</th>
            <th scope="col" class="col_number">TVA</th>
            <th scope="col" class="col_number">TTC</th>
            <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
        </tr>
    </thead>
    <tbody>
% else:
<table>
    <tbody>
		<tr>
			<td class='col_text'>
				<em>
					Aucune dépense associée.
				</em>
			</td>
		</tr>
% endif
	% for line in records:
		<tr class='tableelement'>
            <% sheet_url = request.route_path('/expenses/{id}', id=line.sheet_id) %>
            <% sheet = line.sheet %>
			<% onclick = "document.location='{url}'".format(url=sheet_url) %>
			<% tooltip_title = f"Cliquer pour voir ou modifier la note de dépense de {sheet.month} {sheet.year}" %>

			<td class="col_status" onclick="${onclick}"
                title="${api.format_status(sheet)} - ${tooltip_title}"
            >
                <span class="icon status ${api.status_css_class(sheet)}">
                    ${api.icon(api.status_icon(sheet))}
                </span>
			</td>
			<td class="col_date" onclick="${onclick}"title="${tooltip_title}">
                ${api.format_date(line.date)}
            </td>
			<td class="col_text" onclick="${onclick}" title="${tooltip_title}">
				${line.expense_type.label}
			</td>
			<td class="col_number" onclick="${onclick}" title="${tooltip_title}">
				${api.format_amount(line.total_ht)}&nbsp;€
			</td>
			<td class="col_number" onclick="${onclick}" title="${tooltip_title}">
				${api.format_amount(line.total_tva)}&nbsp;€
			</td>
			<td class="col_number" onclick="${onclick}" title="${tooltip_title}">
				${api.format_amount(line.total)}&nbsp;€
			</td>
            <td class="col_actions width_two">
                <div class="btn-group">
                    <a href="${sheet_url}" title="Voir ou modifier" aria-label="Voir ou modifier la note de dépenses de {sheet.month} {sheet.year}" class="btn icon only">
                        ${api.icon('arrow-right')}&nbsp;Voir ou modifier la note de dépenses de {sheet.month} {sheet.year}
                    </a>
                </div>
            </td>
		</tr>
	% endfor
	</tbody>
</table>

</div>
</%block>
