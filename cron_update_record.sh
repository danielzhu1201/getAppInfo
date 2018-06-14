sourceString="source /home/ymserver/dmvhost/getAppInfo/getappinfo/bin/activate"
echo $sourceString
$sourceString
today=$(date "+%Y-%m-%d")
echo $today
string="python apps/cron_delete_record/cron_delete_record_ssdb.py &"
echo $string
$string

