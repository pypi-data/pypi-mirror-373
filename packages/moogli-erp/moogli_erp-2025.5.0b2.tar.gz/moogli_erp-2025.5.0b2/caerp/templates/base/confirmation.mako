<%doc>
Template pour la confirmation d'action
Attend :

- confirmation_message : Le confirmation_message pour la confirmation 
- validate_button : Bouton de validation
- cancel_button : Bouton d'annulation
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
    <h1 class='separate_bottom'>Confirmation</h1>
    <div class='layout separate_bottom'>
    <p>${confirmation_message | n }</p>
    </div>
    <div class='layout flex separate_bottom'>
        ${request.layout_manager.render_panel(validate_button.panel_name, context=validate_button)}
        ${request.layout_manager.render_panel(cancel_button.panel_name, context=cancel_button)}
    </div>
</%block>