<%inherit file="${context['main_template'].uri}" />
<%block name="mainblock">
${request.layout_manager.render_panel(
  "filetable",
  files=files,
  add_url=add_url,
  help_message=help_message,
  add_perm="context.add_file",
)}
</%block>
