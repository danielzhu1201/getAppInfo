sourceString="source /home/ymserver/dmvhost/getAppInfo/getappinfo/bin/activate"
echo $sourceString
$sourceString
today=$(date "+%Y-%m-%d")
echo $today
string="python apps/server/getAppInfo_flask_api.py &"
echo $string
$string

