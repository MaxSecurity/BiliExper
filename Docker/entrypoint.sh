#!/bin/sh

#默认参数
tag='latest'
daemon="no"
cron=''
only_download="no"

#解析参数
while getopts "t:dc:D" opt; do
  case $opt in
    t)
      tag=$OPTARG
      ;;
    d)
      daemon="yes"
      ;;
    c)
      cron="$cron;$OPTARG"
      ;;
    D)
      # 仅下载程序
      only_download="yes"
      ;;
    \?)
      echo "Invalid option: -$OPTARG"
      ;;
  esac
done

# 下载程序
function download(){
  wget -q -O /tmp/BiliExp.zip https://archive.fastgit.org/MaxSecurity/BiliExper/archive/master.zip
  [ "$?" != 0 ] && echo "Update/Download BiliExp error!" && return
  unzip /tmp/BiliExp.zip -d /tmp > /dev/null
  rm /tmp/BiliExp.zip
  [ -d /tmp/BiliExp ] && rm -rf /tmp/BiliExp
  mv /tmp/BiliExp* /tmp/BiliExp

  if [ -f "/tmp/BiliExp/Docker/init.sh" ]; then
    /bin/sh "/tmp/BiliExp/Docker/init.sh";
  fi
}


if [ "$only_download" = "yes" ];then
  download
  return
fi

if [ ! -d "/BiliExp" ]; then
  echo "未找到挂载目录"
  exit -1
fi

download

if [ $daemon = "yes" ];then
  # 每天2点更新程序
  echo "0 2 * * * pkill -9 python3; /entrypoint.sh -D" > "/etc/crontabs/`whoami`"

  [ "$cron" = "" ] && cron="0 12 * * *"
  OLDIFS=$IFS;IFS=';'
  for cr in $cron; do
    if [ "$cr" != "" ]; then
      echo "$cr /usr/local/bin/python3 /tmp/BiliExp/BiliExp.py -c /BiliExp/config.json -l /BiliExp/BiliExp.log" >> "/etc/crontabs/`whoami`"
    fi
  done
  IFS=$OLDIFS
  /usr/sbin/crond start

  # 监听日志
  echo "" >> /BiliExp/BiliExp.log
  tail -n 1 -F /BiliExp/BiliExp.log

else
  cd /tmp/BiliExp && /usr/local/bin/python3 BiliExp.py -c /BiliExp/config.json -l /BiliExp/BiliExp.log
fi
