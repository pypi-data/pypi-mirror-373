<%namespace file="/base/utils.mako" import="format_text" />
<footer>
<div class='row pdf_footer'>
	<p>
	% if title:
		<b>${ format_text(title) }</b>
		% if more_text or text:
			<br />
		% endif
	% endif
	% if more_text:
		${format_text(more_text)}
	% endif
	% if more_text and text:
		<br />
	% endif
	% if text:
		${format_text(text)}
	% endif
	</p>
</div>
<div id='page-number' class='pdf_page_number'>
	<p>
		${number}
		<span class='page_count'>
			<span>-</span>
			Page ${ pdf_current_page } / ${ pdf_page_count }
		</span>
	</p>
</div>
</footer>
