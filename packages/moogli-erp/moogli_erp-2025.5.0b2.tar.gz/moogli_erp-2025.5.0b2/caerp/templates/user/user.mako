<%inherit file="${context['main_template'].uri}" />
<%namespace name="utils" file="/base/utils.mako" />
<%namespace file="/base/utils.mako" import="company_disabled_msg"/>
<%namespace file="/base/utils.mako" import="company_list_badges" />
<%block name="mainblock">
<div class='user_dashboard'>
    <div class='layout flex separate_bottom'>
        <div class='col-md-2'>
        % if user.login:
            % if user.login.active:
                <span class='icon big status valid' title='Identifiants actifs'>
                    ${api.icon('lock')}
                    <span class="screen-reader-text">Identifiants actifs</span>
                </span>
            %else:
                <span class='icon big status invalid' title='Identifiants désactivés'>
                    ${api.icon('danger')}
                    <span class="screen-reader-text">Identifiants désactivés</span>
                </span>
            % endif
        % else:
            <span class='icon big status disabled' title='Pas d’identifiants'>
                ${api.icon('lock')}
                <span class="screen-reader-text">Pas d’identifiants</span>
            </span>
        % endif
        </div>
    % if api.has_permission('global.create_user'):
        <div class='col-md-10'>
        % if user.login:
            % if user.login.active:
            <p>
                Ce compte dispose d’identifiants : <strong>${user.login.login}</strong><br />
                <strong>L’utilisateur peut se connecter à MoOGLi</strong>
            </p>
            <a class='btn'
                href="${request.route_path('/users/{id}/login', id=user.id)}"
                >
                ${api.icon('pen')}
                Voir les identifiants et droits
            </a>
            % else:
            <p>
                Les identifiants de ce compte sont désactivés<br />
                <strong>L’utilisateur ne peut pas se connecter à MoOGLi</strong>
            </p>
            % endif
        % else:
            <p>
                <em>Ce compte ne dispose pas d’identifiants</em>
            </p>
            <a
            class='btn btn-primary'
            href="${request.route_path('/users/{id}/login/add', id=user.id)}"
            >
                ${api.icon('plus')}
                Créer des identifiants
            </a>
        % endif
        </div>
    % elif api.has_permission('context.edit_user') and request.identity == user:
        <div class='col-md-10'>
            <a
                class='btn'
                href="${request.route_path('/users/{id}/myaccount', id=request.context.id)}"
                >
                ${api.icon('pen')}
                Modifier mes informations
            </a>
            <br><br>
            <a
                class='btn'
                href="${request.route_path('/users/{id}/login/set_password', id=request.context.id)}"
                >
                ${api.icon('lock')}
                Changer mon mot de passe
            </a>
        </div>
    % endif
    </div>

    % if api.has_permission('global.company_view'):
    <div class='layout flex separate_bottom'>
    % if user.companies:
        <div class='col-md-2'>
            <span class='icon big status valid' title='Enseignes'>
                ${api.icon('building')}
                <span class="screen-reader-text">Enseignes</span>
            </span>
        </div>
        <div class='col-md-10'>
        % if len(user.companies) == 1:
            <p>Ce compte est rattaché à l’enseigne
            <a
                href="${request.route_path('/companies/{id}', id=user.companies[0].id)}"
                title="Voir l’enseigne">
                ${user.companies[0].name}
            </a>
            </p>
        % else:
            <p>
            Ce compte est rattaché aux enseignes suivantes&nbsp;
            </p>
            <ul>
            % for company in user.companies:
            <li>
                <a
                    href='${request.route_path('/companies/{id}', id=company.id)}'
                    title="Voir l’enseigne"
                >
                    ${company.name}
                </a>
                % if not company.active:
                ${company_disabled_msg()}
                % endif
            </li>
            % endfor
            </ul>
            <p>
                <a class='btn'
                    href="${request.route_path('/users/{id}/companies', id=user.id)}"
                    >
                    ${api.icon('building')}
                    Voir les enseignes
                </a>
            </p>
        % endif
        </div>

    % else:
        <div class='col-md-2'>
            <span class='icon big status disabled' title='Enseignes'>
                ${api.icon('building')}
                <span class="screen-reader-text">Enseignes</span>
            </span>
        </div>
        <div class='col-md-10'>
            <p>
                <em>Ce compte n’est rattaché à aucune enseigne</em>
            </p>
        </div>
    % endif
    </div>
    % endif

    % if api.has_permission('global.view_userdata') and request.has_module('userdatas'):
    <div class='layout flex separate_bottom'>
        % if user.userdatas:
        <div class='col-md-2'>
            <span class='icon big status valid'>${api.icon('address-card')}</span>
        </div>
        <div class='col-md-10'>
            <p>Une fiche de gestion sociale est associée à ce compte</p>
        <a class='btn'
            href="${request.route_path('/users/{id}/userdatas', id=user.id)}"
            >
            ${api.icon('address-card')}
            Voir la fiche de gestion sociale
        </a>
        % else:
        <div class='col-md-2'>
            <span class='icon big status disabled'>${api.icon('address-card')}</span>
        </div>
        <div class='col-md-10'>
            <p>
                <em>Aucune fiche de gestion sociale n’est associée à ce compte</em>
            </p>
            <% create_userdata_url = request.route_path('/users/{id}/userdatas/add', id=user.id) %>
            <%utils:post_action_btn url="${create_userdata_url}" icon="plus"
              _class="btn btn-primary"
            >
                Créer une fiche de gestion sociale
            </%utils:post_action_btn>
        % endif
        </div>
    </div>
    % endif
    % if api.has_permission('context.view_trainerdata') and request.has_module('training'):
    <div class='layout flex separate_bottom'>
        
        % if user.trainerdatas:
        
            <div class='col-md-2'>
                <span class='icon big status valid' title='Fiche formateur'>
                    ${api.icon('chalkboard-teacher')}
                    <span class="screen-reader-text">Fiche formateur</span>
                </span>
            </div>
            <div class='col-md-10'>
            % if user == request.identity:
                <a class='btn' href="${request.route_path('/users/{id}/trainerdatas/edit', id=user.id)}">
                    ${api.icon('chalkboard-teacher')}
                    Voir/Modifier ma fiche formateur
                </a>
            % else:
                <p>Une fiche formateur est associée à ce compte</p>
                <a class='btn'
                    href="${request.route_path('/users/{id}/trainerdatas/edit', id=user.id)}"
                    >
                    ${api.icon('chalkboard-teacher')}
                    Voir/Modifier la fiche formateur
                </a>
            % endif
            </div>
        % elif api.has_permission('global.view_training'):
        
        <div class='col-md-2'>
            <span class='icon big status disabled' title='Fiche formateur'>
                ${api.icon('chalkboard-teacher')}
                <span class="screen-reader-text">Fiche formateur</span>
            </span>
        </div>
        <div class='col-md-10'>
            <p>
                <em>Aucune fiche formateur n’est associée à ce compte</em>
            </p>
            <% create_trainerdata_url = request.route_path('/users/{id}/trainerdatas/add', id=user.id) %>
            <%utils:post_action_btn url="${create_trainerdata_url}" icon="plus"
              _class="btn btn-primary"
            >
                Créer une fiche formateur
            </%utils:post_action_btn>
        % endif
    </div>
</div>
% endif
</%block>
