<%inherit file="/layouts/default.mako" />

<%block name="headtitle">
<h1>Dossier : ${layout.current_project_object.name}</h1>
</%block>

<%block name='actionmenucontent'>
</%block>

<%block name='content'>
<% project =  layout.current_project_object %>
<div class="totals grand-total">
	<div class="layout flex">
		<div>
			<p><strong>Nom :</strong> ${project.name}</p>
			% if project.description:
				<p><strong>Description succinte :</strong> ${project.description}</p>
			% endif
            % if project.project_type.name != 'default':
                <p><strong>Type de dossier :</strong> ${project.project_type.label}</p>
            % endif
            % if project.code:
                <p><strong>Code du dossier :</strong> ${project.code}</p>
            % endif
            <%block name='projecttitle'>
                <% customers_list = layout.current_project_object.customers %>
                % if len(customers_list) == 1:
                    <p>
                        <strong>Client :</strong>
                        <a href="${request.route_path('/customers/{id}', id=customers_list[0].id)}">${customers_list[0].label}</a>
                    </p>
                % elif len(customers_list) < 6:
                    <p>
                        <strong>Clients :</strong>
                        ${', '.join([
                            f"<a href='{request.route_path('/customers/{id}', id=customer.id)}'>{customer.label}</a>" 
                            for customer in customers_list
                        ])|n}
                    </p>
                % else:
                    <p>
                        <strong>Clients :</strong>
				
                        <span id="short_customers_list">
                            ${', '.join([
                                f"<a href='{request.route_path('/customers/{id}', id=customer.id)}'>{customer.label}</a>" 
                                for customer in customers_list[:3]
                            ])|n}
                            <a href="#" title="Voir tous les clients" onclick="display_full_customers_list();">
                                et ${len(customers_list)-3} autres clients <span class="screen-reader-text">Voir tous les clients</span>
                            </a>
                        </span>
                        <span id="full_customers_list" style="display:none;">
                            ${', '.join([
                                f"<a href='{request.route_path('/customers/{id}', id=customer.id)}'>{customer.label}</a>" 
                                for customer in customers_list
                            ])|n}
                        </span>
                    </p>
                % endif
            </%block>
            % if project.mode == 'ttc':
                <p>
                    <strong>Mode de calcul :</strong>
                    <span class="icon status mode" title="Mode TTC : vous renseignez les prix TTC et le HT est calculé">
                        ${api.icon('mode-ttc')}
                    	<span class="screen-reader-text">Mode TTC : vous renseignez les prix TTC et le HT est calculé</span>
                    </span>
                </p>
            % endif
		</div>
		<div>
            ${request.layout_manager.render_panel(
                'business_metrics_totals', 
                instance=project, 
                tva_on_margin=getattr(project.project_type.default_business_type, "tva_on_margin", False))
            }
		</div>
	</div>
</div>

<div>
    <div class='tabs'>
        <%block name='rightblock'>
        ${request.layout_manager.render_panel('tabs', layout.projectmenu)}
        </%block>
    </div>
    <div class='tab-content'>
        <%block name='mainblock'>
        </%block>
    </div>
</div>

<script>
function display_full_customers_list() {
    document.getElementById('short_customers_list').style.display='none';
    document.getElementById('full_customers_list').style.display='inline';
    return false;
}
</script>
</%block>
