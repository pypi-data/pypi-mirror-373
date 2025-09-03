<%inherit file="${context['main_template'].uri}" />
<%namespace name="utils" file="/base/utils.mako" />
<%block name="mainblock">
<div class="content_vertical_padding separate_bottom align_right">
    % if api.has_permission('global.view_training', current_trainerdatas):
        <%utils:post_action_btn url="${delete_url}"  icon="trash-alt"
          _class='btn negative'
          onclick="return confirm('Êtes-vous sûr de vouloir supprimer cette fiche formateur et tous les éléments associés ?')"
        >
            Supprimer la fiche
        </%utils:post_action_btn>
% endif
</div>
${request.layout_manager.render_panel('help_message_panel', parent_tmpl_dict=context.kwargs)}
${form|n}
</%block>
<%block name="footerjs">
    setAuthCheckBeforeSubmit('#deform');
</%block>
