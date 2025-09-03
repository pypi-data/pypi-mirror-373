<%doc>
    Simple page for form rendering
</%doc>

<%inherit file="${context['main_template'].uri}" />

<%block name="content">
    ${request.layout_manager.render_panel(
        'help_message_panel',
        parent_tmpl_dict=context.kwargs
    )}
    <div class="limited_width width80 dispatch_invoice">
		<div>
			${form|n}
		</div>
    </div>
</%block>

<%block name='footerjs'>

new TotalMatchLinesValidation(
  '.item-lines input[name=ht]',
  $('input[name=total_ht]'),
  $('.btn.deform-seq-add'),
);
new TotalMatchLinesValidation(
  '.item-lines input[name=tva]',
  $('input[name=total_tva]'),
  $('.btn.deform-seq-add'),
);
</%block>
