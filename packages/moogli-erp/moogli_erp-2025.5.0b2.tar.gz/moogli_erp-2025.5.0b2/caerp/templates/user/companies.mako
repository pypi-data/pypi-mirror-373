<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="company_disabled_msg"/>
<%namespace file="/base/utils.mako" import="table_btn"/>
<%namespace file="/base/utils.mako" import="company_list_badges" />
<%block name="mainblock">
<div class="table_container">
	% if companies:
    <table class="top_align_table hover_table">
        <thead>
            <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
            <th scope="col" class="col_text">Nom</th>
            <th scope="col" class="col_text"><span class="icon">${api.icon('envelope')}</span>Adresse e-mail</th>
            <th scope="col" class="col_text">Entrepreneur(s)</th>
            <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
        </thead>
        <tbody>
% else:
    <table class="top_align_table">
        <tbody>
			<tr>
				<td class="col_text"><em>Ce compte n’est rattaché à aucune enseigne</em></td>
			</tr>
% endif
		% for company in companies:
			<% url = request.route_path('/companies/{id}', id=company.id) %>
			<% onclick = "document.location='{url}'".format(url=url) %>
			<% tooltip_title = "Cliquer pour voir ou modifier l’enseigne « " + company.name + " »" %>
			<tr>
			% if not company.active:
				<td class="col_status" onclick="${onclick}" title="Enseigne désactivée - ${tooltip_title}">
					<span class="icon status invalid">
						${api.icon("lock")}
					</span>
				</td>
			% else:
				<td class="col_status" onclick="${onclick}" title="Enseigne active - ${tooltip_title}">
					<span class="icon status valid">
						${api.icon("check")}
					</span>
				</td>
			% endif
				<td class="col_text" onclick="${onclick}" title="${tooltip_title}">
					${company.name} 
					<br>
					<small>(${company.code_compta})</small>
					% if not company.active:
					${company_disabled_msg()}
					% endif
				</td>
				<td class="col_text">
					<a href="mailto:${company.email}" title="Cliquer pour envoyer un e-mail à cette adresse" aria-label="Cliquer pour envoyer un e-mail à cette adresse">
						${company.email}
					</a>
				</td>
				<td class="col_text">
					<ul>
						% for employee in company.employees:
							<li>
								<a href="${request.route_path('/users/{id}', id=employee.id)}" title="Cliquer pour voir l’entrepreneur" aria-label="Cliquer pour voir l’entrepreneur">
								${api.format_account(employee)}
								</a>
							</li>
						% endfor
					</ul>
				</td>
				<td class='col_actions width_one'>
				${request.layout_manager.render_panel('menu_dropdown', label="Actions", links=stream_actions(company))}
				</td>
			</tr>
		% endfor
        </tbody>
    </table>
</div>
<div class="content_vertical_padding">
<h3>Associer</h3>
<a href="${request.route_path('/users/{id}/companies/associate', id=user.id)}"
	class='btn btn-primary'
	title="Associer à une enseigne existante dans MoOGLi"
	aria-label="Associer à une enseigne existante dans MoOGLi">
	${api.icon("building")}
	À une enseigne existante
</a>
<a href="${request.route_path('/companies', _query=dict(action='add', user_id=user.id))}"
	class='btn btn-primary'
	title="Associer à une nouvelle enseigne"
	aria-label="Associer à une nouvelle enseigne">
	${api.icon("plus")}
	À une nouvelle enseigne
</a>
</div>
</%block>
