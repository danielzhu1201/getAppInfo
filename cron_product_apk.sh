sourceString="source /home/ymserver/dmvhost/getAppInfo/getappinfo/bin/activate"
$sourceString
enviroment="hdfs:///"
filePath="datamining.ym/dmuser/qwwang/apkList/"
#today=$1
today=$(date "+%Y-%m-%d" -d "7 days ago")
hadoopFilePath=$enviroment$filePath$today"/"

sparkString="spark-submit ./getApkList.py "$today" "$hadoopFilePath" day --num-executors=10"
echo $sparkString
$sparkString

localpath=$("pwd")
downloadFolder=$today
localFolderPath=$localpath"/"$today

cpstring="hadoop fs -copyToLocal "$hadoopFilePath" "$localpath
echo $cpstring
$cpstring

deleteHadoopData="hadoop fs -rm -r "$hadoopFilePath
#echo $deleteHadoopData
#$deleteHadoopData

loadIntoRedisPythonFile="apps/cron_product_apk/loadApkIntoRedis_ssdb_list.py"
loadString="python "$loadIntoRedisPythonFile" "$localpath"/"$today
echo $loadString
$loadString
