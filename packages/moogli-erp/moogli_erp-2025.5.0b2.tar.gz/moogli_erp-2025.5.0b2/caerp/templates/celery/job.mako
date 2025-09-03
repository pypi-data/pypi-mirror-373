<%doc>
Main job page
should load dynamically the datas about a job execution
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%block name="content">
<div id="ajax_container">
</div>
<script type='text/javascript'>
    AppOptions['url'] = "${url}";
    AppOptions['dataType'] = "${request.context.type_}"
</script>
</%block>
