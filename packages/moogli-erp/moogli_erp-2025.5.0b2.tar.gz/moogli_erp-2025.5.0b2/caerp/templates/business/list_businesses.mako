<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

${searchform()}

<div>
    % if records.item_count > 0:
        <div>
            ${records.item_count} Résultat(s)
        </div>
        <div class="align_right">
            <small>Les montants sont exprimés TTC</small>
        </div>
        <div class='table_container'>
            ${request.layout_manager.render_panel('business_list', records, is_admin_view=is_admin)}
        </div>
        ${pager(records)}
    % else:
        <div class="content_vertical_double_padding"><em>Aucune affaire pour le moment</em></div>
        <div class="alert alert-info">
            <span class="icon">${api.icon('info-circle')}</span>
            Une affaire est un cadre de facturation qui regroupe l'ensemble des devis et factures 
            liés à la même prestation, ainsi que les éventuels documents associés.
            <br/><br/>
            Les affaires sont créées automatiquement quand on est dans un contexte de facturation 
            "complexe" (formation, chantier, etc.) ou lorsqu'un devis est facturé en plusieurs fois 
            (par exemple avec un acompte). Dans les autres situations la facturation se fait sans affaire.
        </div>
    % endif
</div>

</%block>
