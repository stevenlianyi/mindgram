application_name='accountApp'
application_app='application'
application_port='16021'
application_num='2'
echo application=$application_name
application_gunicorn=/usr/local/bin/gunicorn
echo
echo ps aux|grep -E ${application_name}|grep -v grep|awk '{print $2}'|xargs kill -9
ps aux|grep -E ${application_name}|grep -v grep|awk '{print $2}'|xargs kill -9
echo
echo gunicorn $application_name
$application_gunicorn --reload -w $application_num -b 127.0.0.1:$application_port $application_name:$application_app &
#gunicorn -b 127.0.0.1:$application_port $application_name:$application_app &
