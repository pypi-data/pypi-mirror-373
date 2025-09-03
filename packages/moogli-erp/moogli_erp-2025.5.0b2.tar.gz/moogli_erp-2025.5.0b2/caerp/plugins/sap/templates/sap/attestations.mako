<%doc>
Template listant les attestations SAP :
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="show_tags_label" />
<%namespace file="/base/utils.mako" import="company_internal_msg" />
<%namespace file="/base/utils.mako" import="company_list_badges" />
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
  <div class='layout flex main_actions'>
      % if api.has_permission('global.view_sap'):
          <a
              class='btn btn-primary'
              title="Générer ou re-Générer des attestations fiscales"
              aria-label="Générer ou re-Générer des attestations fiscales"
              href="${request.route_path('/sap/attestations/generate')}"
          >
              ${api.icon('file-alt')}
              Générer des attestations
          </a>
      % endif
      <a
          class='btn'
          title="Exporter les attestations affichées dans un unique PDF (s’ouvrira dans une nouvelle fenêtre)"
          aria-label="Exporter les attestations affichées dans un unique PDF (s’ouvrira dans une nouvelle fenêtre)"
          href="#"
          onclick='window.openPopup("${bulk_pdf_export_url}")'
      >
          ${api.icon('file-export')}
          Export massif PDF
      </a>
  </div>
</div>
</%block>



<%block name='content'>
	<div class="alert alert-info">
        <span class="icon">${api.icon('info-circle')}</span>
        ${help_message}
    </div>

${searchform()}


  <div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        % if len(records) == 0:
	        <table>
                <tbody>
                    <td class="col_text"><em>Aucune attestation ne correspond à votre recherche</em></td>
                </tbody>

        % else:
	        <table class="hover_table">
                <thead>
                    <tr>
                        <th scope='col' class='col_text'>${sortable("Année", "year")}</th>
                        <th scope='col' class='col_text'>${sortable("Enseigne", "company")}</th>
                        <th scope="col" class="col_text">${sortable("Client", 'customer')}</th>
                        <th scope="col" class="col_text">${sortable("Montant attesté", 'amount')}</th>
                        <th scope="col" class="col_datetime">${sortable("Générée le", 'updated_at')}</th>
                        <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                    </tr>
                </thead>
                <tbody>
                    % for attestation in records:
                        <% company_url = request.route_path('/companies/{id}', id=attestation.customer.company_id) %>
                        <% customer_url = request.route_path('/customers/{id}', id=attestation.customer_id) %>
                        <%
                        if attestation.files:
                            onclick = f"document.location='{pdf_url(attestation)}'"
                            clickable_attrs = f'title="Cliquer pour voir l’attestation en PDF" aria-label="Cliquer pour voir l’attestation en PDF" onclick="{onclick}"'
                        else:
                            clickable_attrs = ''
                        %>
                        <tr>
                            <td ${clickable_attrs|n}  class="col_text">
                                ${attestation.year}
                            </td>
                            <td class="col_text"><a href="${company_url}" title="Cliquer pour voir l’enseigne « ${attestation.company.name} »" aria-label="Cliquer pour voir l’enseigne « ${attestation.company.name} »">
                                ${attestation.company.name}
                            </a></td>
                            <td class="col_text"><a href="${customer_url}" title="Cliquer pour voir le client « ${attestation.customer.name} »" aria-label="Cliquer pour voir le client « ${attestation.customer.name} »">
                                ${attestation.customer.name}
                            </a></td>
                            <td ${clickable_attrs|n} class="col_number">
                                ${api.format_amount(attestation.amount, precision=5)} €
                            </td>
                            <td ${clickable_attrs|n} class="col_datetime">
                                ${attestation.updated_at}
                            </td>
                            ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(attestation))}
                        </tr>
                    % endfor
                </tbody>
            % endif
        </table>
    </div>
    ${pager(records)}
</div>
</%block>
