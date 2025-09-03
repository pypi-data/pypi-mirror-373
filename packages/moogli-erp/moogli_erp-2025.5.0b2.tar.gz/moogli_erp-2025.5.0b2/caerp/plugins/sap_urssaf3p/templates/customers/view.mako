<%inherit file="/customers/view.mako" />

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class="layout flex main_actions">
    ${request.layout_manager.render_panel('action_buttons', links=layout.stream_main_actions())}

        <div role="group">
            % if request.context.urssaf_data:
            <img alt="Logo URSSAF" src="${request.static_url('caerp:static/svg/urssaf_logo.svg')}" width="110" height="34" />
            % endif
            
            ${request.layout_manager.render_panel('action_buttons', links=list(more_actions))}
        </div>
        ${request.layout_manager.render_panel('action_buttons', links=layout.stream_other_actions())}
    </div>
</div>
</%block>

<%block name='after_summary'>
<div class="data_display content_vertical_padding">
    % if request.context.type == 'individual':
    <h3>
        Avance immédiate
        <img alt="Logo URSSAF" src="${request.static_url('caerp:static/svg/urssaf_logo.svg')}" width="110" height="34" />
    </h3>
    % endif
    % if request.context.urssaf_data:
    <dl>
        <div>
            <dt>Identification</dt>
            <dd><br>
                Né le ${api.format_date(request.context.urssaf_data.birthdate)}<br>
                % if request.context.urssaf_data.birthplace_country_code == '99100':
à ${request.context.urssaf_data.birthplace_city} - ${request.context.urssaf_data.birthplace_department} - France
                % else:
à ${request.context.urssaf_data.birthplace_city} - ${request.context.urssaf_data.birthplace_country}
                % endif
            </dd>
        </div>
        <div>
            <dt>Coordonnées bancaires</dt>
            <dd><br>
                Titulaire : ${request.context.bank_account_owner}
                <br>
                IBAN : ${request.context.bank_account_iban}
                <br>
                BIC : ${request.context.bank_account_bic}
            </dd>
        </div>
    </dl>
    % elif request.context.type == 'individual':
    <div class="alert alert-info">
        <p>
            <span class="icon">${api.icon('info-circle')}</span>
            Pour pouvoir inscrire ce client à l’avance immédiate, vous devez ajouter de nouvelles informations à sa
            fiche.
        </p>
    </div>
    <a 
        href="${request.current_route_path(_query={'action': 'edit'})}"
        class="btn" 
        title="Renseigner les informations permettant d’inscrire ce client à avance immdiate" 
        aria-label="Renseigner les informations permettant d’inscrire ce client à avance immdiate">
        Renseigner les informations 
    </a>
    % endif
</div>
</%block>