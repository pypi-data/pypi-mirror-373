Le ${api.format_datetime(activity.datetime)} 
"${activity.type_object.label}" ${activity.mode}
<br />entre
${','.join([participant.label for participant in activity.conseillers])}
et 
${','.join([participant.label for participant in activity.participants])}
