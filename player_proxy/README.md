# B站视频接口代理(node.js)

* 用于B站视频下载脚本(videoDownloader.py)解析港澳台独播视频，需要将本目录下player_proxy.js文件部署到阿里云函数(香港地区)上，并将videoDownloader.py文件中的ReverseProxy变量替换为自己阿里云函数的接口地址。暂不提供一键部署的actions，需要的请手动部署。

* 除了用于代理港澳台解析，也可以将大会员的cookie配置在代理服务器中，为其他非会员用户下载大会员专享视频提供代理，而且比共享账号更安全。