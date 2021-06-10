#!/bin/bash

#删除非Actions需要的模块
BiliClient_needs=("wasm_enc" "__init__.py" "asyncBiliApi.py" "asyncXliveWs.py")
params=''
for i in ${BiliClient_needs[@]};do params="$params\|$i"; done
delete_arr=(`ls ./BiliClient|grep -v ${params: 2}`)
for i in ${delete_arr[@]};do rm -rf "./BiliClient/${i}"; done

#安装Actions需要的依赖库
sudo -H pip3 install --upgrade setuptools >/dev/null
sudo -H pip3 install -r ./run_in_Actions/requirements.txt >/dev/null

#将secrets映射到配置文件
\cp -f ./run_in_Actions/config.json ./config/
python3 ./run_in_Actions/secrets2config.py

#启动BiliExp
python3 BiliExp.py