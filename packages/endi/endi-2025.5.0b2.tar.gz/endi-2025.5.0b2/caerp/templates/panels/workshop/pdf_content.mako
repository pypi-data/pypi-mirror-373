<%doc>
Attendance sheet for a given timeslot (the current context)
</%doc>
<%namespace file="caerp:templates/base/utils.mako" import="format_text" />
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
    	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    	<link rel="shortcut icon" href="" type="image/x-icon" />
    	<meta name="description" comment="">
    	<meta name="KEYWORDS" CONTENT="">
    	<meta NAME="ROBOTS" CONTENT="INDEX,FOLLOW,ALL">
  	</head>
  	<body class='workshop_view'>
  	${request.layout_manager.render_panel('workshop_pdf_header', context=request.context)}
        <main>
			% for index, i in enumerate(('info1', 'info2', 'info3')):
				% if getattr(workshop, i):
                <h${index + 1}>${getattr(workshop, i).label} </h${index + 1}>
				% endif
			% endfor

	        % if timeslots[0].start_time.day == timeslots[-1].end_time.day:
            <h3>
                Émargement du ${api.format_date(timeslots[0].start_time)}
                de ${api.format_datetime(timeslots[0].start_time, timeonly=True)}
                à ${api.format_datetime(timeslots[-1].end_time, timeonly=True)}
            </h3>
    	    % else:
            <h3>
                Émargement du ${api.format_datetime(timeslots[0].start_time)}
                au ${api.format_datetime(timeslots[-1].end_time)}
            </h3>
        	% endif
			<div>
				<div>
					<img src="${request.static_url('caerp:static/img//pdf_checkbox.png', _app_url='')}" alt="case à cocher" />
					Atelier
				</div>
				<div>
					<img src="${request.static_url('caerp:static/img//pdf_checkbox.png', _app_url='')}" alt="case à cocher" />
					Formation
				</div>
			</div>
			<br />
	        <div>
	        	<b>Titre de l'atelier ou de la formation</b> : ${workshop.name}
	        </div>
			<div class='row'>
				<table class="lines">
					<thead class="keep_with_next">
						<tr>
							<th scope="col" class="col_text description">Participants</th>
							% if is_multi_antenna_server:
								<th scope="col" class="col_text description">Antenne de rattachement</th>
							% endif
							% for timeslot in timeslots:
								<th scope="col" class='slot_signature'>${timeslot.name}</th>
							% endfor
						</tr>
					</thead>
					<tbody>
						% for user in participants:
							<tr>
								<td class="col_text description">
									${api.format_account(user)}
									% for c in [company for company in user.companies if company.active]:
										% if loop.first:
											-
										% endif
										${c.name}
										% if not loop.last:
										/
										% endif
									% endfor
								</td>
								% if is_multi_antenna_server:
									<td class="slot_signature">
										% if user.userdatas and user.userdatas.situation_antenne:
											${user.userdatas.situation_antenne.label}
										% else:
											non renseignée
										% endif
									</td>
								% endif
								% for timeslot in timeslots:
									<td class="slot_signature"></td>
								% endfor
							</tr>
						% endfor
					</tbody>
				</table>
			</div>
			<div class="pdf_spacer"><br />
			</div>
			<div class='row'>
				<table class="lines">
					<thead class="keep_with_next">
						<tr>
							<th scope="col" class="col_text"
								% if is_multi_antenna_server:
									colspan="2"
								% endif
							>
								Formateur(s)
							</th>

							% for timeslot in timeslots:
								<th scope="col" class='slot_signature'>${timeslot.name}</th>
							% endfor
						</tr>
					</thead>
					<tbody>
						% for user in workshop.trainers:
							<tr>
								<td class="col_text description"
									% if is_multi_antenna_server:
										colspan="2"
									% endif
								>
									${api.format_account(user)}
								</td>

								% for timeslot in timeslots:
									<td class="slot_signature"></td>
								% endfor
							</tr>
						% endfor
					</tbody>
				</table>
			</div>
    	</main>
    </body>
</html>
