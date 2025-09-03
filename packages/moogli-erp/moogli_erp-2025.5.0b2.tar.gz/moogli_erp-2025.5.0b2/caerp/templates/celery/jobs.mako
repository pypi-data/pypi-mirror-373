<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="table_btn"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
    % if records:
        <table class="top_align_table hover_table">
            <thead>
                <tr>
                    <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                    <th scope="col" class="col_number">${sortable("Date d'exécution", "created_at")}</th>
                    <th scope="col" class="col_text">Type de tâche</th>
                    <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                </tr>
            </thead>
            <tbody>
	% else:
		<table class="top_align_table">
			<tbody>
				<tr>
					<td class="col_text"><em>Aucune tâche disponible</em></td>
				</tr>
	% endif
                % for job in records:
                    <% url = request.route_path('job', id=job.id) %>
                    <% onclick = "document.location='{url}'".format(url=url) %>
                    <% tooltip_title = "Cliquer pour voir la tâche" %>
                    <tr>
                        <td class="col_status" onclick="${onclick}" title="${tooltip_title}">
							<span class="icon status ${job.status}">
                                <%
                                job_icon = "check"
                                if(job.status == "planned"):
                                    job_icon = "clock"
                                if(job.status == "failed"):
                                    job_icon = "exclamation-triangle"
                                %>
								${api.icon(job_icon)}
							</span>
                        </td>
                        <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                            ${api.format_datetime(job.created_at)}
                        </td>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                            ${job.label}
                        </td>
                        <td class="col_actions width_two">
                            <% view_url = request.route_path('job', id=job.id) %>
                            ${table_btn(view_url, "Voir", "Voir la tâche", icon='arrow-right', css_class='btn icon only')}
                            <% del_url = request.route_path('job', id=job.id, _query=dict(action="delete")) %>
                            ${table_btn(del_url, "Supprimer",  "Supprimer cette entrée d'historique", icon='trash-alt', \
                            onclick="return confirm('Êtes vous sûr de vouloir supprimer cette entrée d'historique ?')", css_class="btn icon only negative")}
                        </td>
                    </tr>
                % endfor
            </tbody>
        </table>
    </div>
    ${pager(records)}
</div>
</%block>
