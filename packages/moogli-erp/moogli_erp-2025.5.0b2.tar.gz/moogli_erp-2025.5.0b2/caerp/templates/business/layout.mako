<%inherit file="/layouts/default.mako" />

<%block name="headtitle">
<h1>
    ${layout.current_business_object.business_type.label} : ${layout.current_business_object.name}
</h1>
</%block>

<%block name="content">
<% business = layout.current_business_object %>
<div class="totals grand-total">
	<div class="layout flex">
		<div>
			<p>
				<strong>Nom :</strong> 
				${business.name}
				% if api.has_permission("context.edit_business", business):
				<a
					class="btn icon only unstyled"
					href="${layout.edit_url}"
					title="Modifier le nom de cette affaire"
					aria-label="Modifier le nom de cette affaire"
				>
                    ${api.icon('pen')}
				</a>
				% endif
			</p>
			<p>
				<strong>Client :</strong>
				<% customer = business.get_customer() %>
				<a href="${request.route_path('/customers/{id}', id=customer.id)}"><big>${customer.label}</big></a>
			</p>
			<p class="content_vertical_double_padding"
				title="${api.format_indicator_status(business.status)}"
				aria-label="${api.format_indicator_status(business.status)}"
				>
				<span class="icon status ${api.indicator_status_css(business.status)}">
                    ${api.icon(api.indicator_status_icon(business.status))}
				</span>
				&nbsp;
				% if business.status == 'success':
					Cette affaire est complète
				% else:
					<% url = request.route_path('/businesses/{id}/overview', id=request.context.id, _anchor='indicator-table') %>
					% if business.status == 'danger':
						Des obligations ne sont pas satisfaites dans cette affaire
					% else:
						Des recommendations ne sont pas satisfaites dans cette affaire
					% endif
					&nbsp;
					<a class="btn btn_small" href="${url}" title="Voir la liste détaillée des éléments manquants">
						${api.icon('search')} Voir le détail
					</a>
				% endif
			</p>
		</div>
		<div>
            ${request.layout_manager.render_panel('business_metrics_totals', instance=business, tva_on_margin=business.business_type.tva_on_margin)}
		</div>
	</div>
</div>
<div>
    <div class='tabs'>
		<%block name='rightblock'>
			${request.layout_manager.render_panel('tabs', layout.businessmenu)}
		</%block>
    </div>
    <div class='tab-content'>
		<%block name='mainblock'></%block>
   </div>
</div>
</%block>
