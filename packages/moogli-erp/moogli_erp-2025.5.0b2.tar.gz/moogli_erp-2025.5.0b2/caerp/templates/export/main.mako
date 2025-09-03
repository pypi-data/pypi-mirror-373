<%inherit file="${context['main_template'].uri}" />

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
	<div class='layout flex main_actions'>
	    <a class='btn' href='/export/export_log'>
            ${api.icon('info-circle')}
            Historique des exports comptables
	    </a>
	</div>
</div>
</%block>

<%block name='content'>
<div>
	% if help_message is not None:
		<div class="alert alert-info">
            <span class="icon">${api.icon('info-circle')}</span>
			${help_message|n}
		</div>
	% endif

	<div>
		<ul class="nav nav-tabs" role="tablist">
			<% current = request.params.get('__formid__', list(forms.keys())[0]) %>
			% for form_name, form_datas in forms.items():
				<li role="presentation" class="${'active' if form_name==current else ''}">
					<a href="#${form_name}-container" aria-controls="${form_name}-container" id="${form_name}-tabtitle" role="tab" data-toggle="tab" tabindex='-1'>
						<%
						tab_title = form_datas['title']
						tab_title = tab_title.replace("Exporter les factures fournisseurs ", "")
						tab_title = tab_title.replace("Exporter les paiements fournisseurs ", "")
						tab_title = tab_title.replace("Exporter les factures ", "")
						tab_title = tab_title.replace("Exporter les encaissements des factures ", "")
						tab_title = tab_title.replace("Exporter les encaissements ", "")
						tab_title = tab_title.replace("Exporter les paiements des notes de dépenses", "")
						tab_title = tab_title.replace("Exporter les paiements ", "")
						tab_title = tab_title.replace("Exporter les ", "")
						tab_title = tab_title.replace("Exporter des ", "")
						tab_title = tab_title.strip().capitalize()

						%>
						${tab_title}
					</a>
				</li>
			% endfor
		</ul>
	</div>

	<div class='tab-content'>
		% for form_name, form_datas in forms.items():
			<div role="tabpanel" id="${form_name}-container" aria-labelledby="${form_name}-tabtitle" class="tab-pane fade ${'in active' if form_name==current else ''}">
				% if form_name == current and check_messages is not None:
					<div class="alert alert-info">
                        <span class="icon">${api.icon('info-circle')}</span>
                        ${check_messages['title']}
					</div>
					% if check_messages['errors']:
						<div class="alert alert-danger">
							<p class='text-danger'>
								<span class="icon">${api.icon('danger')}</span>
							% for message in check_messages['errors']:
								<b>*</b> ${message|n}<br />
							% endfor
							</p>
						</div>
					% endif
				% endif
				${form_datas['form']|n}
			</div>
		% endfor
	</div>

    <div>
        <%
            export_type = request.path.split('/')[-1]
        %>
        ## FIXME generate table header and cells thanks to headers
        ## as defined in export/sage.py instead of hardcoding them ?
        ## This refactoring should be done when displaying recorded export #2089
        % if preview_items is not None:
            <div class="alert alert-info">
                <span class="icon">${api.icon('info-circle')}</span>
			        Ceci est une prévisualisation, il n'est pas garanti que
                    l'export final soit exactement le même (d'autres écritures
                    pourraient être passées entre cette prévisualisation et
                    l'export définitif).
		    </div>

            <div><br />${len(preview_items)} Résultat(s)</div>

            <div class='table_container'>
            <table class="top_align_table hover_table">
                <thead>
                    <tr>
                % for column in writer.headers:
                    <th scope="col" class="col_text">${column['label']}</th>
                % endfor
                </tr>
                </thead>
                <tbody>
                    % for item in preview_items:
                        <tr class='tableelement'>
						% for header, value in get_value_from_writer(writer, item):
							<td class="col_${header.get('typ', 'text')}">${value}</td>
						% endfor
                        </tr>
                    % endfor
                </tbody>
            </table>
            </div>
        % endif
    </div>
</div>
</%block>

