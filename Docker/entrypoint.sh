#!/bin/sh

#默认参数
tag='latest'
daemon="no"
cron='0 12 * * *'

#解析参数
while getopts "t:dc:" opt; do
  case $opt in
    t)
      tag=$OPTARG
      ;;
    d)
      daemon="yes"
      ;;
    c)
      cron=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG"
      ;;
  esac
done

if [ ! -d "/BiliExp" ]; then
  echo "未找到挂载目录"
  exit -1
fi

#装载代码
# if [ $tag = "latest" ];then
#   wget -O /tmp/BiliExp.zip `wget -q -O - https://api.github.com/repos/happy888888/BiliExp/tags | grep zipball_url | head -1 | sed 's/.*: \"\(.*\)\".*/\1/g'`
#   unzip /tmp/BiliExp.zip -d /tmp
#   rm /tmp/BiliExp.zip
#   mv /tmp/*BiliExp* /tmp/BiliExp
# elif [ $tag = "newest" ];then
#   wget -O /tmp/BiliExp.zip https://archive.fastgit.org/happy888888/BiliExp/archive/master.zip
#   unzip /tmp/BiliExp.zip -d /tmp
#   rm /tmp/BiliExp.zip
#   mv /tmp/BiliExp* /tmp/BiliExp
# else
#   if [ ! -d "/BiliExp/code-cache" ]; then
#     wget -O /tmp/BiliExp.zip "https://archive.fastgit.org/happy888888/BiliExp/archive/$tag.zip"
# 	unzip /tmp/BiliExp.zip -d /tmp
# 	rm /tmp/BiliExp.zip
# 	mv /tmp/BiliExp* /tmp/BiliExp
#     cp -r /tmp/BiliExp /BiliExp/code-cache
#   else
#     cp -r /BiliExp/code-cache /tmp/BiliExp
#   fi
# fi

function download(){
  wget -O /tmp/BiliExp.zip https://archive.fastgit.org/MaxSecurity/BiliExper/archive/master.zip
  unzip /tmp/BiliExp.zip -d /tmp
  rm /tmp/BiliExp.zip
  [ -d /tmp/BiliExp ] && rm -rf /tmp/BiliExp
  mv /tmp/BiliExp* /tmp/BiliExp

  if [ -f "/tmp/BiliExp/Docker/init.sh" ]; then
    /bin/sh "/tmp/BiliExp/Docker/init.sh";
  fi
}
# 下载代码
download

#执行代码
if [ $daemon = "yes" ];then
  echo "$cron /usr/local/bin/python3 /tmp/BiliExp/BiliExp.py -c /BiliExp/config.json -l /BiliExp/BiliExp.log" > "/etc/crontabs/`whoami`"
  /usr/sbin/crond start
  while :;do
    sleep 24h
    # 每24小时下载一次代码（用作更新）
    pkill -9 python3
    download
  done
else
  cd /tmp/BiliExp && /usr/local/bin/python3 BiliExp.py -c /BiliExp/config.json -l /BiliExp/BiliExp.log
fi
