<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_mail" />
<%namespace file="/base/utils.mako" import="format_phone" />
<%namespace file="/base/utils.mako" import="format_address" />
<%namespace file="/base/utils.mako" import="company_list_badges" />
<%namespace file="/base/utils.mako" import="login_disabled_msg" />

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
	<div class='layout flex main_actions'>
	% for button in actions:
		${request.layout_manager.render_panel(button.panel_name, context=button)}
	% endfor
	</div>
</div>
</%block>

<%block name='content'>
<div class='data_display separate_bottom layout flex two_cols with_memos'>
	<div>
		<h2>
			Informations générales
		</h2>
		<div class="layout flex">
			<span class='user_avatar'>
				${api.icon('building')}
			</span>
			<div>
				<h3>
					% if not company.active:
						<small><span class="icon status closed">${api.icon('lock')}</span></small>
					% endif
					Enseigne ${company.name}
					% if not company.active:
						<small>${company_list_badges(company)}</small>
					% endif
				</h3>
				<p>${company.goal}</p>
				% if company.logo_id:
					<img src="${api.img_url(company.logo_file)}" alt=""  width="250px" />
				%endif
			</div>
		</div>
		<div class="data_display content_vertical_padding">
			<h4 class="separate_top content_vertical_double_padding">Enseigne</h4>
			<dl>
			% if company.email:
				<div>
					<dt>E-mail</dt>
					<dd>${format_mail(company.email)}</dd>
				</div>
			% else:
				<div class="empty">
					<dt>E-mail</dt>
					<dd><em>Non renseigné</em></dd>
				</div>
			% endif

			% if company.phone:
				<div>
					<dt>Téléphone</dt>
					<dd>${format_phone(company.phone, 'desk')}</dd>
				</div>
			% else:
				<div class="empty">
					<dt>Téléphone</dt>
					<dd><em>Non renseigné</em></dd>
				</div>
			% endif

			% if company.mobile:
				<div>
					<dt>Téléphone portable</dt>
					<dd>${format_phone(company.mobile, 'mobile')}</dd>
				</div>
			% else:
				<div class="empty">
					<dt>Téléphone portable</dt>
					<dd><em>Non renseigné</em></dd>
				</div>
			% endif

			% if company.address or company.city:
				<div>
					<dt>Adresse</dt>
					<dd><br />${format_address(company, multiline=True)}</dd>
				</div>
			% else:
				<div class="empty">
					<dt>Adresse</dt>
					<dd><em>Non renseignée</em></dd>
				</div>
			% endif

			% if company.activities:
				<div>
					<dt>Domaine(s) d’activité</dt>
					<dd>
						<ul>
							% for activity in company.activities:
								<li>${activity.label}</li>
							% endfor
						</ul>
					</dd>
				</div>
			% else:
				<div class="empty">
					<dt>Domaine(s) d’activité</dt>
					<dd><em>Non renseigné</em></dd>
				</div>
			% endif

			% if api.has_permission('global.manage_accounting'):
				% if company.RIB:
					<div>
						<dt>RIB</dt>
						<dd>${company.RIB}</dd>
					</div>
				% else:
					<div class="empty">
						<dt>RIB</dt>
						<dd><em>Non renseigné</em></dd>
					</div>
				% endif

				% if company.IBAN:
					<div>
						<dt>IBAN</dt>
						<dd>${company.IBAN}</dd>
					</div>
				% else:
					<div class="empty">
						<dt>IBAN</dt>
						<dd><em>Non renseigné</em></dd>
					</div>
				% endif

				% if company.antenne is not None:
					<div>
				% else:
					<div class="empty">
				% endif
						<dt>Antenne de rattachement</dt>
						<dd>
						% if company.antenne is not None:
							${company.antenne.label}
						% else:
							<em>Non renseignée</em>
						%endif
						</dd>
					</div>

				% if company.follower is not None:
					<div>
				% else:
					<div class="empty">
				% endif
						<dt>Enseigne accompagnée par</dt>
						<dd>
						% if company.follower is not None:
							${api.format_account(company.follower)}
						% else:
							<em>Non renseigné</em>
						% endif
						</dd>
					</div>

			</dl>
			<h4 class="separate_top content_vertical_double_padding">Comptabilité</h4>
			<dl class="data_number">
				<% accounting_data = [
					('Code analytique', company.code_compta),
					('Compte client général', company.general_customer_account),
					('Compte client tiers', company.third_party_customer_account),
					('Compte fournisseur général', company.general_supplier_account),
					('Compte fournisseur tiers', company.third_party_supplier_account),
					('Compte client général (interne)', company.internalgeneral_customer_account),
					('Compte client tiers (interne)', company.internalthird_party_customer_account),
					('Compte fournisseur général (interne)', company.internalgeneral_supplier_account),
					('Compte fournisseur tiers (interne)', company.internalthird_party_supplier_account),
					('Compte général (classe 4) pour les dépenses', company.general_expense_account),
					('Compte de banque', company.bank_account),
				]
				%>
				% for label, value in accounting_data:
					% if value:
					<div>
					% else:
					<div class="empty">
					% endif
						<dt>${label}</dt>
						<dd>${value or "Non renseigné"}</dd>
					</div>
				% endfor
			</dl>
			<h4 class="separate_top content_vertical_double_padding">Calculs de prix</h4>
			<dl class="data_number">
				% if enabled_modules['contribution']:
					<% value = company.get_rate(company.id, 'contribution') %>
					% if value:
					<div>
					% else:
					<div class="empty">
					% endif
						<dt>Contribution à la CAE</dt>
						<dd>
							% if value:
								${api.format_float(value)} %
								% if company.contribution is None:
									(par défaut)
								% endif
							% else:
								<em>Non renseigné</em>
							% endif
						</dd>
					</div>
				% endif

				% if enabled_modules['internalcontribution']:
					<% value = company.get_rate(company.id, 'contribution', 'internal') %>
					% if value:
					<div>
					% else:
					<div class="empty">
					% endif
						<dt>Contribution à la CAE (pour la facturation interne)</dt>
						<dd>
							% if value:
								${api.format_float(value)} %
								% if company.internalcontribution is None:
									(par défaut)
								% endif
							% else:
								<em>Non renseigné</em>
							% endif
						</dd>
					</div>
				% endif

				% if enabled_modules['insurance']:
				<% value = company.get_rate(company.id, 'insurance') %>
					% if value:
					<div>
					% else:
					<div class="empty">
					% endif
						<dt>Taux d’assurance professionnelle</dt>
						<dd>
							% if value:
								${api.format_float(value)} %
								% if company.insurance is None:
									(par défaut)
								% endif
							% else:
								<em>Non renseigné</em>
							% endif
						</dd>
					</div>
				% endif

				% if enabled_modules['internalinsurance']:
				<% value = company.get_rate(company.id, 'insurance', 'internal') %>
					% if value:
					<div>
					% else:
					<div class="empty">
					% endif
						<dt>Taux d’assurance professionnelle (pour la facturation interne)</dt>
						<dd>
							% if value:
								${api.format_float(value)} %
								% if company.internalinsurance is None:
									(par défaut)
								% endif
							% else:
								<em>Non renseigné</em>
							% endif
						</dd>
					</div>
				% endif
			% endif

			% if company.general_overhead:
				<div>
					<dt>Coefficient de frais généraux</dt>
					<dd>${company.general_overhead}</dd>
				</div>
			% else:
				<div class="empty">
					<dt>Coefficient de frais généraux</dt>
					<dd><em>0</em></dd>
				</div>
			% endif

			% if company.margin_rate:
				<div>
				<dt>Coefficient de marge</dt>
					<dd>${company.margin_rate}</dd>
				</div>
			% else:
				<div class="empty">
				<dt>Coefficient de marge</dt>
					<dd><em>0</em></dd>
				</div>
			% endif

			% if company.cgv and 'Renseignées':
				<div>
					<dt>CGV complémentaires</dt>
					<dd>Renseignées</dd>
				</div>
			% else:
				<div class="empty">
					<dt>CGV complémentaires</dt>
					<dd><em>Non renseignées</em></dd>
				</div>
			% endif

			% if company.header_id and 'Personalisé (image)':
				<div>
					<dt>En-tête des documents</dt>
					<dd>Personnalisé (image)</dd>
				</div>
			% else:
				<div class="empty">
					<dt>En-tête des documents</dt>
					<dd><em>Par défaut</em></dd>
				</div>
			% endif
			</dl>
		</div>
	</div>
	<div>
		<div class="content_vertical_padding">
			<div class="status_history hidden-print memos">
				Chargement des mémos…
			</div>
		</div>
		<div class="content_vertical_padding">
			<h3>Raccourcis</h3>

			<ul class="no_bullets content_vertical_padding">
				% for module, perm, route, label, title, icon in ( \
					(None, 'company.view', '/companies/{id}/estimations', 'Devis', 'Voir les devis de l’enseigne', 'file-alt'),\
					(None, 'company.view', '/companies/{id}/invoices', 'Factures', 'Voir les factures de l’enseigne', 'file-invoice-euro'),\
					('commercial', 'company.view', 'commercial_handling', 'Gestion commerciale', 'Voir la gestion commerciale de l’enseigne', 'chart-line'), \
					('accounting', 'company.view', '/companies/{id}/accounting/treasury_measure_grids', 'États de trésorerie', 'Voir les états de trésorerie de l’enseigne', 'euro-circle'), \
					('accounting', 'company.view', '/companies/{id}/accounting/income_statement_measure_grids', 'Comptes de résultat', 'Voir les comptes de résultat de l’enseigne', 'table'), \
					('accompagnement', 'company.view', 'company_activities', 'Rendez-vous', 'Voir les rendez-vous de l’enseigne', 'calendar-alt'),\
					('workshops', 'company.view', 'company_workshops_subscribed', 'Ateliers auxquels l’enseigne participe', 'Voir les ateliers auxquels l’enseigne participe', 'chalkboard-students'),\
					('training', 'context.view_training', 'company_workshops', 'Ateliers organisés par l’enseigne', 'Voir les ateliers organisés par l’enseigne', 'chalkboard-teacher'),\
					):
					% if (module is None or request.has_module(module)) and request.has_permission(perm):
						<li>
							<a href="${request.route_path(route, id=_context.id)}"  title="${title}" aria-label="${title}">
								<span class="icon">${api.icon(icon)}</span>${label}
							</a>
						</li>
					% endif
				% endfor
			</ul>
		</div>
	</div>
	<div class="data_display">
		<h2>Employé(s)</h2>
		<div class='panel-body'>
			<ul class="company_employees">
			% for user in company.employees:
				<li class="company_employee_item">
					% if user.photo_file:
						<span class="user_avatar">
							<img src="${api.img_url(user.photo_file)}"
								title="${api.format_account(user)}"
								alt="Photo de ${api.format_account(user)}"
								width="256" height="256" />
						</span>
					% else:
						<span class="user_avatar">${api.icon('user')}</span>
					% endif
					% if api.has_permission("context.view_user", user):
						<a href="${request.route_path('/users/{id}', id=user.id)}" title='Voir ce compte'>
							${api.format_account(user)}
						</a>
					% else:
						${api.format_account(user)}
					% endif
					% if user.login is not None and not user.login.active:
						<small>${login_disabled_msg()}</small>
					% endif
				</li>
			% endfor
			</ul>
			% if len(company.employees) == 0:
				Aucun entrepreneur n’est associé à cette enseigne
			% endif
		</div>
	</div>
</div>
</%block>

<%block name='footerjs'>
	AppOption = {};
	% for key, value in js_app_options.items():
		AppOption["${key}"] = "${value}"
	% endfor;
</%block>
