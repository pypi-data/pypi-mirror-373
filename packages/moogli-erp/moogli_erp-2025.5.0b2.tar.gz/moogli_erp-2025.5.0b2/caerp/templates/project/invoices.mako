<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
% if api.has_permission("context.edit_project", layout.current_project_object):
<div class='main_toolbar action_tools'>
	<div class='layout flex main_actions'>
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

<%block name='mainblock'>
<div id="project_invoices_tab">
	<div class='layout flex two_cols content_vertical_padding separate_bottom_dashed'>
		<div role="group">
	    % if api.has_permission('context.add_invoice'):
    		<a class='btn btn-primary icon' href='${add_url}'>
		        ${api.icon('file-invoice-euro')}
		        Créer une facture
    		</a>
	    % endif	
		</div>
		<div role='group' class='align_right'>
			<%
			## We build the link with the current search arguments
			args = request.GET
			url_xls = request.route_path('/projects/{id}/invoices.{extension}', extension='xls', id=request.context.id, _query=args)
			url_ods = request.route_path('/projects/{id}/invoices.{extension}', extension='ods', id=request.context.id, _query=args)
			url_csv = request.route_path('/projects/{id}/invoices.{extension}', extension='csv', id=request.context.id, _query=args)
			%>
			<a class='btn icon_only_mobile' onclick="window.openPopup('${url_xls}');" href='javascript:void(0);' title="Export au format Excel (xlsx) dans une nouvelle fenêtre" aria-label="Export au format Excel (xlsx) dans une nouvelle fenêtre">
				${api.icon('file-excel')}
				Excel
			</a>
			<a class='btn icon_only_mobile' onclick="window.openPopup('${url_ods}');" href='javascript:void(0);' title="Export au format Open Document (ods) dans une nouvelle fenêtre" aria-label="Export au format Open Document (ods) dans une nouvelle fenêtre">
				${api.icon('file-spreadsheet')}
				ODS
			</a>
			<a class='btn icon_only_mobile' onclick="window.openPopup('${url_csv}');" href='javascript:void(0);' title="Export au format csv dans une nouvelle fenêtre" aria-label="Export au format csv dans une nouvelle fenêtre">
				${api.icon('file-csv')}
				CSV
			</a>
		</div>
    </div>

    ${searchform()}

    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        ${request.layout_manager.render_panel(
          'task_list',
          records,
          datatype="invoice",
          is_admin_view=is_admin,
          is_project_view=True,
          tva_on_margin_display=request.context.project_type.is_tva_on_margin(),
        )}
    </div>
    ${pager(records)}
</div>

</%block>
