<%inherit file="${context['main_template'].uri}" />
<%block name="mainblock">
% if not is_void:
<div class='alert alert-info'>
<span class="icon">${api.icon('info-circle')}</span>
Cochez ici les documents sociaux que l’entrepreneur a déjà transmis
</div>
<div class='doc_list'>
${form|n}
</div>
% else:
<div class='alert alert-info'>
<span class="icon">${api.icon('info-circle')}</span>
Aucun type de document n’a été configuré.
% if api.has_permission('global.config_userdatas'):
<br />
Vous pouvez les configurer <a href='${request.route_path('/admin/userdatas/social_doc_type_option')}' target='_blank' title="Cet écran s’ouvrira dans une nouvelle fenêtre" aria-label="Cet écran s’ouvrira dans une nouvelle fenêtre">dans l’interface de configuration.</a>
% endif
</div>
% endif
</%block>
