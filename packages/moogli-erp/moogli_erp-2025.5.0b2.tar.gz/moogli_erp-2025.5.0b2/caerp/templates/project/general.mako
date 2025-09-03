<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_text" />
<%namespace file="/base/utils.mako" import="format_mail" />

<%block name='actionmenucontent'>
% if request.GET.get("action") != "edit" and api.has_permission("context.edit_project", layout.current_project_object):
<div class='main_toolbar action_tools'>
    <div class="layout flex main_actions">
        <div role='group'>
            <a class='btn btn-primary icon' href="${layout.edit_url}">
                ${api.icon('pen')}
                Modifier le dossier
            </a>
        </div>
    </div>
</div>
% endif
</%block>

<%block name="mainblock">
<div id="project_general_tab">
	<h3>Client(s)</h3>
	<div class="layout flex three_cols">
	% for customer in project.customers:
	    <div class="editable">
		    <div class="layout flex">
	    		<h4>${customer.label}</h4>
				<button onclick='openPopup("${request.route_path('/customers/{id}', id=customer.id, _query={'action': 'edit'})}")'
					class='btn icon only unstyled'
					title='Modifier le client ${customer.label} dans une nouvelle fenêtre'
					aria-label='Modifier le client ${customer.label} dans une nouvelle fenêtre'
					>
					${api.icon('pen')}
				</button>
	        </div>
			<address>
				${format_text(customer.full_address)}
			% if customer.email:
				<br>
				${format_mail(customer.email)}
			% endif
			</address>
	    </div>
	% endfor
	</div>
	<div class="separate_top data_display">
		<h3>Informations générales</h3>
		<dl>
			<dt>Type de dossier :</dt><dd>${project.project_type.label}</dd>
			% if project.mode == "ttc":
				<% mode_info = "Mode TTC : vous renseignez les prix TTC et le HT est calculé" %>
				<% mode_icon = "mode-ttc" %>
			% else:
				<% mode_info = "Mode HT : vous renseignez les prix HT et le TTC est calculé" %>
				<% mode_icon = "mode-ht" %>
			% endif
			<dt>Mode de calcul :</dt>
			<dd>
				<span class="icon status mode" title="${mode_info}">
					${api.icon(mode_icon)}
					<span class="screen-reader-text">${mode_info}</span>
				</span>
			</dd>
			% if project.project_type.default_business_type:
				<dt>Type d'affaire par défaut:</dt>
				<dd>${project.project_type.default_business_type.label}</dd>
			% endif
			% if project.business_types:
				<dt>Autre types d'affaire :</dt>
				<dd>${','.join([s.label for s in project.business_types])}</dd>
			% endif
			%if project.description:
				<dt>Description succinte :</dt> <dd>${project.description}</dd>
			% endif
			% if project.starting_date:
				<dt>Début prévu le :</dt><dd>${api.format_date(project.starting_date)}</dd>
			% endif
			% if project.ending_date:
				<dt>Livraison prévue le :</dt><dd>${api.format_date(project.ending_date)}</dd>
			% endif
		</dl>
	% if project.definition:
	    <h3>Définition du dossier</h3>
	    <p>
	        ${format_text(project.definition)|n}
	    </p>
	</div>
	% endif
</div>
</%block>
