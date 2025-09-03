<%doc>
Template for holidays search
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
<div class='content_vertical_padding limited_width width40'>
    ${form|n}
</div>
%if start_date and end_date:
<div class='content_vertical_padding limited_width width40'>
	<h2>Congés entre le ${api.format_date(start_date)} et le ${api.format_date(end_date)}</h2>
	<p class='content_vertical_padding'>${len(holidays)} Résultat(s)</p>

	<div class='table_container'>
		<table>
		% if len(holidays) > 0:
			<thead>
				<tr>
					<th scope="col" class="col_text">Nom de l’entrepreneur</th>
					<th scope="col" class="col_date" title="Date de début"><span class="screen-reader-text">Date de </span>Début</th>
					<th scope="col" class="col_date" title="Date de fin"><span class="screen-reader-text">Date de </span>Fin</th>
				</tr>
			</thead>
			<tbody>
			% for holiday in holidays:
				%if holiday.user:
				<tr>
					<td class="col_text">
						${api.format_account(holiday.user)}
					</td>
					<td class="col_date">
					${api.format_date(max(holiday.start_date, start_date))}
					</td>
					<td class="col_date">
					${api.format_date(min(holiday.end_date, end_date))}
					</td>
				</tr>
				% endif
			% endfor
			</tbody>
		%else:
			<tbody>
				<tr>
					<td class='col_text'>
					<em>Aucun congés n’ont été déclarés sur cette période</em>
					</td>
				</tr>
			</tbody>
		</table>
		%endif
	</div>
</div>
% endif
</%block>
