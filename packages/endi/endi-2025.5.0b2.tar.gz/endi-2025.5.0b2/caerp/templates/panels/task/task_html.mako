${request.layout_manager.render_panel('task_pdf_content', context=task, with_cgv=False)}
${request.layout_manager.render_panel('task_pdf_footer', context=task)}
${request.layout_manager.render_panel('task_pdf_cgv', context=task)}
