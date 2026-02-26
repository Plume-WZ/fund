exist=`ps -ef | grep fund_server | grep -v grep`
if [[ -z "$exist" ]];then
   cd /opt/fund/
   nohup python3 fund_server.py > /tmp/fund.log &
fi
