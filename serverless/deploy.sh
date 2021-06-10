#!/bin/bash

#删除非云函数需要的模块
BiliClient_needs=("__init__.py" "asyncBiliApi.py" "asyncXliveWs.py")
params=''
for i in ${BiliClient_needs[@]};do params="$params\|$i"; done
delete_arr=(`ls ./BiliClient|grep -v ${params: 2}`)
for i in ${delete_arr[@]};do rm -rf "./BiliClient/${i}"; done

#安装云函数需要的依赖库到severless文件夹
sudo -H pip3 install --upgrade setuptools >/dev/null
sudo -H pip3 install -r ./serverless/requirements.txt -t ./serverless

#将需要的代码移动并cd到severless文件夹
sudo mv BiliExp.py ./serverless
sudo mv ./tasks ./serverless
sudo mv ./BiliClient ./serverless
sudo mkdir ./serverless/config
sudo mv ./config/*.json ./serverless/config
cd ./serverless

#部署至腾讯云函数
if [ -z "$TENCENT_SECRET_ID" ] || [ -z "$TENCENT_SECRET_KEY" ]; then
  echo "部署至腾讯云需要填写TENCENT_SECRET_ID和TENCENT_SECRET_KEY两个secrets，跳过部署"
else
  echo "开始安装腾讯ServerlessFramework"
  sudo npm install -g serverless
  
  echo "开始配置云函数参数"
  if [ -n "$CRON" ]; then    #修改cron表达式
    sed -i "s/0 0 12 \* \* \* \*/${CRON}/g" ./serverless.yml
  fi
  if [ -n "$REGION" ]; then  #修改部署区域
    sed -i "s/ap-guangzhou/${REGION}/g" ./serverless.yml
  fi
  
  echo "开始部署至腾讯云函数"
  sudo rm -f aliyun_serverless.yml
  sls deploy --debug
  exit 0
fi

#部署至阿里云函数
if [ -z "$ACCOUNT_ID" ] || [ -z "$ACCESS_KEY_ID" ] || [ -z "$ACCOUNT_ID" ]; then
  echo "部署至阿里云需要填写ACCOUNT_ID、ACCESS_KEY_ID和ACCOUNT_ID三个secrets，跳过部署"
else
  echo "开始安装阿里云Funcraft"
  sudo apt-get update
  sudo apt-get install -y unzip zip
  wget --no-check-certificate -O fun-linux.zip https://gosspublic.alicdn.com/fun/fun-v3.6.14-linux.zip
  unzip fun-linux.zip
  sudo mv fun-*-linux /usr/local/bin/fun
  
  echo "开始配置云函数参数"
  if [ -n "$CRON" ]; then    #修改cron表达式
    sed -i "s/0 0 4 \* \* \*/${CRON}/g" ./aliyun_serverless.yml
  fi
  
  echo "开始部署至阿里云函数"
  sudo rm -f serverless.yml
  fun deploy -t ./aliyun_serverless.yml
fi
