<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <div role='group'>
            % if api.has_permission('context.add_supplier'):
                <button class='btn btn-primary' onclick="toggleModal('supplier_add_form'); return false;">
                    ${api.icon("plus")}
                    Ajouter<span class="no_mobile">&nbsp;un fournisseur</span>
                </button>
                <a class='btn' href="${request.route_path('company_suppliers_import_step1', id=request.context.id)}">
                    ${api.icon("file-import")}
                    Importer<span class="no_mobile">&nbsp;des fournisseurs</span>
                </a>
            % endif
        </div>
        <%
        ## We build the link with the current search arguments
        args = request.GET
        url = request.route_path('suppliers.csv', id=request.context.id, _query=args)
        %>
        <a class='btn icon_only_mobile' href='${url}' title="Export au format CSV">
            ${api.icon("file-csv")}
            CSV
        </a>
    </div>
</div>
</%block>

<%block name='content'>

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        % if records:
        <table class="hover_table">
            <thead>
                <tr>
                    <th scope="col" class="col_date">${sortable("Créé le", "created_at")}</th>
                    <th scope="col">${sortable("Code", "code")}</th>
                    <th scope="col" class="col_text">${sortable("Nom du fournisseur", "label")}</th>
                    <th scope="col" class="col_text">${sortable("Nom du contact principal", "lastname")}</th>
                    <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                </tr>
            </thead>
            <tbody>
        % else:
        <table>
            <tbody>
				<tr>
					<td class="col_text">
						<em>Aucun fournisseur n’a été référencé</em>
					</td>
				</tr>
       % endif
                   % for supplier in records:
                        <tr class='tableelement' id="${supplier.id}">
                            <% url = request.route_path("supplier", id=supplier.id) %>
                            <% onclick = "document.location='{url}'".format(url=url) %>
                            <% tooltip_title = "Cliquer pour voir ou modifier le fournisseur « " + supplier.label + " »" %>
                            <td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(supplier.created_at)}</td>
                            <td onclick="${onclick}" title="${tooltip_title}">${supplier.code}</td>
                            <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                                ${supplier.label}
                                % if supplier.archived:
                                    <br />
                                    <small title="Ce fournisseur a été archivé">
                                    	<span class='icon tag'>${api.icon('archive')} Fournisseur archivé</span></small>
                                % endif
                            </td>
                            <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                                ${supplier.get_name()}
                            </td>
                            ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(supplier))}
                        </tr>
                    % endfor
            </tbody>
        </table>
	</div>
	${pager(records)}
</div>

<section id="supplier_add_form" class="modal_view size_middle" style="display: none;">
    <div role="dialog" id="supplier-forms" aria-modal="true" aria-labelledby="supplier-forms_title">
        <div class="modal_layout">
            <header>
                <button class="icon only unstyled close" title="Fermer cette fenêtre" aria-label="Fermer cette fenêtre" onclick="toggleModal('supplier_add_form'); return false;">
                    ${api.icon("times")}
                </button>
                <h2 id="supplier-forms_title">Ajouter un fournisseur</h2>
            </header>
            <div class="modal_content_layout" id="companyForm">
                ${forms[0][1].render()|n}
            </div>
        </div>
    </div>
</section>
</%block>

<%block name='footerjs'>
$(function(){
    $('input[name=search]').focus();
});
</%block>
