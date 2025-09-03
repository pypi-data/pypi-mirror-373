<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>


<%block name='mainblock'>
<% customer =  layout.current_customer_object %>

<div id="customer_invoices_tab">
	<div class='layout flex two_cols content_vertical_padding separate_bottom_dashed'>
		<div role='group' class='align_right'>
			<%
			## We build the link with the current search arguments
			args = request.GET
			url_xls = request.route_path('/customers/{id}/invoices.{extension}', extension='xls', id=request.context.id, _query=args)
			url_ods = request.route_path('/customers/{id}/invoices.{extension}', extension='ods', id=request.context.id, _query=args)
			url_csv = request.route_path('/customers/{id}/invoices.{extension}', extension='csv', id=request.context.id, _query=args)
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
          tva_on_margin_display=customer.has_tva_on_margin_business(),
        )}
    </div>
    ${pager(records)}
</div>

</%block>
