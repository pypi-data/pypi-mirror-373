<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_text" />
<%namespace file="/base/utils.mako" import="format_customer" />
<%namespace file="/base/utils.mako" import="table_btn"/>

<%block name='afteractionmenu'>
<div class='layout flex dashboard'>
	% if 'welcome' in request.config and request.config['welcome']:
		<div class="alert alert-info">
			${format_text(request.config['welcome'], breaklines=False)}
		</div>
	% endif
</div>
</%block>

<%block name='content'>
<% num_elapsed = elapsed_invoices.count() %>
<div class='layout flex dashboard'>
	<div class="columns">
		<div class='dash_elem'>
			<h2>
				<span class='icon'>${api.icon('star')}</span>
				<span>Raccourcis</span>
			</h2>
			<div class='panel-body'>
                % if shortcuts_msg:
				<div class="alert alert-info">
					<p>
						<span class="icon">${api.icon('info-circle')}</span>
                        ${shortcuts_msg}
					</p>
				</div>
                % endif
				<ul class="layout flex favourites">
                    % for button in shortucts_buttons:
					<li>
						<a class="btn btn-primary" title="${button.title}" href="${button.url}">
							${api.icon(button.icon)}
							${button.text}
						</a>
					</li>
                    % endfor
				</ul>
			</div>
		</div>
	% if num_elapsed:
		<div class="dash_elem" id='unpaid_invoices_container'>
			<h2>
				<span class='icon invalid'>${api.icon('euro-slash')}</span>
				<a href="${request.route_path('/companies/{id}/invoices', id=company.id, _query=dict(__formid__='deform', paid_status='notpaid'))}" title="Voir toutes les factures impayées" aria-label="Voir toutes les factures impayées">
					<span>Factures impayées</span>
					${api.icon('arrow-right')}
				</a>
			</h2>
			<div>
				<p class='message neutral'>
					<span class="icon" role="presentation">${api.icon('info-circle')}</span>
					Vous avez
					% if num_elapsed == 1:
					une facture impayée
					% else:
					${num_elapsed} factures impayées
					% endif
					 depuis plus de 45 jours
				</p>
				<table class='hover_table'>
					<thead>
						<th scope="col" class='col_text'>
							Nom
						</th>
						<th scope="col" class="col_text">
							Client
						</th>
						<th scope="col" class="col_number">
							Montant
						</th>
					</thead>
					<tbody>
						% for invoice in elapsed_invoices:
						<% url = request.route_path("/invoices/{id}/general", id=invoice.id) %>
						<% onclick = "document.location='{url}'".format(url=url) %>
	                    <% tooltip_title = "Cliquer pour voir la facture « " + invoice.name + " »" %>
						<tr>
							<td class="col_text"><a href="${url}" title="${tooltip_title}" aria-label="${tooltip_title}">${invoice.name}</a></td>
							<td class="col_text" onclick="${onclick}" title="${tooltip_title}">
								${format_customer(invoice.customer, False)}
							</td>
							<td  class="col_number" onclick="${onclick}" title="${tooltip_title}">
								${api.format_amount(invoice.ttc, precision=5)}&nbsp;€
							</td>
						</tr>
						% endfor
					</tbody>
				</table>
			</div>
		</div>
	% endif
        ${panel('company_recent_tasks')}
        % if request.has_module('accompagnement'):
	    <div id='event_container'>
	    ${panel('company_coming_events')}
	    ${panel('cae_coming_workshops')}
	    </div>
        % endif
    </div>
</div>
</%block>
