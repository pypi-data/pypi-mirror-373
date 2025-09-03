<%namespace file="/base/utils.mako" import="format_mail" />
<%namespace file="/base/utils.mako" import="format_phone" />
<%namespace file="/base/utils.mako" import="format_text" />

<div class="layout flex content_vertical_padding">
    % if third_party.is_company():
        <span class="user_avatar">${api.icon('building')}</span>
        <div>
            <h3>
                ${third_party.label}
            </h3>
            <small><em>Personne morale</em></small>
        </div>
    % elif third_party.is_internal():
        <span class="user_avatar">${api.icon('house')}</span>
        <div>
            <h3>${third_party.label}</h3>
            <small><em>Enseigne interne à la CAE</em></small>
        </div>
    % else:
        <span class="user_avatar">${api.icon('user')}</span>
        <div>
            <h3>${third_party.label}</h3>
            <small><em>Personne physique</em></small>
        </div>
    % endif
</div>
<div class="data_display content_vertical_padding">
    % if third_party.is_company() or third_party.is_internal():
        <dl class="data_number">
            <div>
                <dt>Numéro d’immatriculation</dt>
                <dd>
                    % if third_party.registration:
                        ${third_party.registration}
                    % else:
                        <em>Non renseigné</em>
                    % endif
                </dd>
            </div>
            <div>
                <dt>TVA intracommunautaire</dt>
                <dd>
                    % if third_party.tva_intracomm:
                        ${third_party.tva_intracomm}
                    % else:
                        <em>Non renseigné</em>
                    % endif
                </dd>
            </div>
        </dl>
        % if third_party.get_name():
            <h4>Contact principal</h4>
            <dl>
                <div>
                    <dt>Nom</dt>
                    <dd>${third_party.get_name()}</dd>
                </div>

                % if third_party.function:
                    <div>
                        <dt>Fonction</dt>
                        <dd>${format_text(third_party.function)}</dd>
                    </div>
                % endif
            </dl>
        % endif
    % endif
    <dl>
        <div>
            <dt>Adresse Postale</dt>
            <dd><br />${format_text(third_party.full_address)}</dd>
        </div>
        <div>
            <dt>Adresse électronique</dt>
            <dd>
                % if third_party.email:
                    ${format_mail(third_party.email)}
                % else:
                    <em>Non renseigné</em>
                % endif
            </dd>
        </div>
        <div>
            <dt>Téléphone portable</dt>
            <dd>
                % if third_party.mobile:
                    ${format_phone(third_party.mobile, 'mobile')}
                % else:
                    <em>Non renseigné</em>
                % endif
            </dd>
        </div>
        <div>
            <dt>Téléphone</dt>
            <dd>
                % if third_party.phone:
                    ${format_phone(third_party.phone, 'desk')}
                % else:
                    <em>Non renseigné</em>
                % endif
            </dd>
        </div>
        <div>
            <dt>Fax</dt>
            <dd>
                % if third_party.fax:
                    ${format_phone(third_party.fax, 'fax')}
                % else:
                    <em>Non renseigné</em>
                % endif
            </dd>
        </div>
    </dl>
</div>
