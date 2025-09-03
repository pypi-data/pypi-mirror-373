<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='afteractionmenu'>
% if current_grid is not None and current_grid.rows:
    <% measures = current_grid.rows %>
    <div class='layout flex two_cols'>
        <div class="align_center vertical_align_center">
            % if highlight_entry:
            <h4>${highlight_entry[0].label | n}</h4>
            <div class='oversized_text'>
                ${api.format_float(highlight_entry[1], precision=2) | n}&nbsp;€
            </div>
            % endif
			<div>
	            ${current_grid.label | n}
	            % if last_grid.grid.id != current_grid.grid.id:
					<br>
	                <small><a href="${request.route_path("/companies/{id}/accounting/treasury_measure_grids", id=request.context.company.id)}">
                    Voir le dernier état de trésorerie
    	            </a></small>
        	    % endif
			</div>
        </div>
        <div class='table_container'>
            <table>
                % for typ, value in measures:
                    % if typ.is_total:
                        <tr class="row_recap row_total">
                            <th scope="row" class="col_text">
                                <h3>
                    % else:
                        <tr>
                            <td class="col_text">
                    % endif
                    ${typ.label | n}
                    % if typ.is_total:
                            </h3>
                        </th>
                    % else:
                        </td>
                    % endif
                        <td class='col_number'>${api.format_float(value, precision=2)|n}&nbsp;€</td>
                    </tr>
                % endfor
            </table>
        </div>
    </div>
% else:
    <div class='alert'><h4>Aucun état de trésorerie n'est disponible</h4></div>
% endif
</%block>

<%block name='content'>
<div class='text_block separate_top'>
    <h2>Historique des états de trésorerie</h2>
</div>

${searchform()}

% if records is not None:
<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container limited_width width30'>
	% if records:
		<table class="hover_table">
			<thead>
				<tr>
					<th scope="col" class="col_date">${sortable("Date", "date")}</th>
					<th scope="col" class="col_number">
                    % if highlight_entry:
                    ${highlight_entry[0].label | n}
                    % endif
                    </th>
					<th scope="col" class="col_actions width_one" title="Actions"><span class="screen-reader-text">Actions</span></th>
				</tr>
			</thead>
	% else:
		<table>
			<tbody>
				<tr>
					<td class="col_text">
						<em>Aucun état ne correspond à votre requête</em>
					</td>
				</tr>
	% endif
			<tbody>
			% for record in records:
				<% url = request.route_path("/treasury_measure_grids/{id}", id=record.id) %>
				<% tooltip_title = "Cliquer pour voir cet état de trésorerie" %>
				<% onclick = "document.location='{url}'".format(url=url) %>
				<tr
					 onclick="${onclick}"
					 title="${tooltip_title}"
				% if record.id == current_grid.grid.id:
					class="highlighted"
				% endif
				>
					<td class="col_date">
						${api.format_date(record.date)}
					</td>
					<td class="col_number">
                    % if highlight_entry:
						<% first_measure = record.get_measure_by_type(highlight_entry[0].id) %>
						% if first_measure is not None:
							${api.format_amount(first_measure.value, precision=0)}&nbsp;€
						% else:
							-
						% endif
                    % endif
					</td>
					${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(record))}
				</tr>
			% endfor
			</tbody>
		</table>
    </div>
    ${pager(records)}
</div>
% endif
</%block>
