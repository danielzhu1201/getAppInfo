sourceString="source /home/ymserver/dmvhost/getAppInfo/getappinfo/bin/activate"
$sourceString
today=$(date "+%Y-%m-%d")
string="python apps/cron_census_redis/census_ssdb.py &"
echo $string
$string

