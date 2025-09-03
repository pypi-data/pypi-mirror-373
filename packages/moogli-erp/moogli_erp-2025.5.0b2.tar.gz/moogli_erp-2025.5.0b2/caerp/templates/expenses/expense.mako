<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_text" />

<%block name="headtitle">
${request.layout_manager.render_panel('task_title_panel', title=title)}
</%block>

<%block name='actionmenucontent'>
<% expense = request.context %>
<div class='main_toolbar action_tools' id='js_actions'></div>
</%block>

<%block name="beforecontent">
<% expense = request.context %>
<div>
    <div class='expense_header layout flex two_cols'>
        <div>
            <h3 class='hidden-print'>
                ${request.layout_manager.render_panel('status_title', context=request.context)}
            </h3>
            <ul class="document_summary content_vertical_padding">
                <li class='hidden-print'>
                    ${api.format_expense_status(expense)}
                </li>
                <li>
                    Titre : 
                    % if expense.title:
                        ${expense.title}
                    % else:
                        <em>Non renseigné</em>
                    % endif
                </li>
                % if api.has_permission('global.manage_accounting'):
                    <li>
                    	Numéro de pièce :
                        % if expense.status == 'valid':
                            <strong>${ expense.official_number }</strong>
                        % else:
                            <strong>Ce document n’a pas été validé</strong>
                        % endif
                    </li>
                    <li>
                        % if expense.purchase_exported and expense.expense_exported:
                            Ce document a déjà été exporté vers le
                            logiciel de comptabilité
                        % elif expense.purchase_exported:
                            Les achats déclarés dans ce document ont déjà été
                            exportés vers le logiciel de comptabilité
                        % elif expense.expense_exported:
                            Les frais déclarés dans ce document ont déjà été
                            exportés vers le logiciel de comptabilité
                        %else:
                            Ce document n'a pas encore été exporté vers le logiciel de comptabilité
                        % endif

                        % if expense.purchase_exported or expense.expense_exported:
                            <ul>
                            % for export in expense.exports:
                                <li>Exporté le
                                    ${api.format_datetime(export.datetime)} par
                                    ${api.format_account(export.user)}
                                </li>
                            % endfor
                            </ul>
                        % endif
                    </li>
                    <li>
                        Entrepreneur : ${api.format_account(expense.user)}
                    </li>
                    <li>
                        Enseigne : ${expense.company.name}
                    </li>
                    <li>
                        Numéro analytique : ${expense.company.code_compta}
                    </li>
                % endif
                <li>
                    Kms déjà validés cette année : 
                    ${api.format_amount(kmlines_current_year)} km ${user_vehicle_information}
                </li>
                % if treasury:
                <li>
                    ${treasury['label']} : ${api.format_amount(treasury['value'])}&nbsp;€                
                </li>
                % endif
                % if expense.payments:
                    <li>
                        Paiement(s) recu(s):
                        <ul>
                            % for payment in expense.payments:
                                <% url = request.route_path('expense_payment', id=payment.id) %>
                                <li>
                                <a href="${url}">
                                    <strong>${api.format_amount(payment.amount)}&nbsp;€</strong>
                                    le ${api.format_date(payment.date)} 
                                    <small>(${api.format_paymentmode(payment.mode)}
                                    % if payment.bank:
                                        &nbsp;(${payment.bank.label})
                                    % endif
                                     enregistré par ${api.format_account(payment.user)})</small>
                                </a>
                                </li>
                            % endfor
                        </ul>
                    </li>
                % endif
            </ul>
        </div>
        <!-- will get replaced by backbone -->
        <div class="status_history"></div>
    </div>
</div>
</%block>

<%block name='content'>
<div id="js-main-area"></div>
</%block>

<%block name='footerjs'>
var AppOption = AppOption || {};
% for option, value in js_app_options.items():
${api.write_js_app_option(option, value)}
%endfor
</%block>
