<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>
${searchform()}
<div>
    <div class='separate_bottom content_vertical_padding'>
    	<strong>
			<% nb_users = records.item_count %>
			% if nb_users == 0:
				Aucun utilisateur
			%elif nb_users == 1:
				1 utilisateur
			%else:
				${nb_users} utilisateurs
			% endif
			 sur ${api.month_name(selected_month)} ${selected_year}
		</strong>
	</div>
    <div class='table_container'>
		<table class="hover_table">
			<thead>
				<tr>
					<th scope="col" class="col_text">${sortable("Nom", "lastname")}</th>
					<th scope="col" class="col_text">${sortable("Prénom", "firstname")}</th>
					<th scope="col" class="col_text">${sortable("E-mail", "email")}</th>
					<th scope="col" class="col_date">${sortable("Dernière connexion", "month_last_connection")}</th>
			</thead>
			<tbody>
				% if records:
					% for connection in records:
						<tr>
							<td class="col_text">${connection.user.lastname}</td>
							<td class="col_text">${connection.user.firstname}</td>
							<td class="col_text">${connection.user.email}</td>
							<td class="col_date">${connection.month_last_connection}</td>
						</tr>
					% endfor
				% else:
					<tr><td colspan=4><em>Aucune connexion sur cette période</em></td></tr>
				% endif
			</tbody>
		</table>
	</div>
	${pager(records)}
</div>
</%block>
