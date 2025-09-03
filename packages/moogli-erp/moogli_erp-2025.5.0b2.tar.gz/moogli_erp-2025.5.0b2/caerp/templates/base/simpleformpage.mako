<%doc>
    Simple page for form rendering
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%block name="content">
<div class="col-md-6 col-md-offset-2">
    ${form|n}
</div>
</%block>
