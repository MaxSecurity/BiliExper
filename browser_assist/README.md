# BiliExp-browser_assist

## 这里是一些用于B站的浏览器辅助脚本

### 使用方式

脚本需要以以下方式执行
浏览器打开B站指定页面(具体看下面脚本列表)--》按F12打开开发者工具--》console--》在下面粘贴脚本，回车

### 脚本列表

#### 所有过期抽奖动态删除
*  适用页面为 B站主页--》右上角"动态"--》左边头像下方"动态"(`https://space.bilibili.com/xxxxxx/dynamic`)
*  脚本内容如下

`
(function(){if(!window.location.href.match(/https:\/\/space.bilibili.com\/[0-9]*\/dynamic.*/g)){console.log("本脚本只能在B站个人动态页面执行！");return}var i=0;function dellott(){var a=$("span.dynamic-link-hover-bg").eq(i);if(a.length==0){$(document).scrollTop($(document).height()-$(window).height());setTimeout(function(){dellott()},1500);return}var ids=a.attr("click-href").match(/.*business_id=([0-9]*)&.*/);if(ids){var bid=ids[1]}else{setTimeout(function(){i++;dellott()},500);return}$.get("https://api.vc.bilibili.com/lottery_svr/v1/lottery_svr/lottery_notice",{"dynamic_id":bid},function(data){if("lottery_result" in data["data"]){a.parents("div.card").find(".child-button")[1].click();setTimeout(function(){$(".bp-popup-ctnr").find(".bl-button--size")[0].click();dellott()},1000)}else{i++;dellott()}})}dellott()})();
`

#### B站专栏不可复制破解
*  适用页面为 所有不可复制的专栏
*  脚本内容如下

`
(function(){var a=document.querySelector("div.article-holder");a.classList.remove("unable-reprint");a.addEventListener("copy",function(e){e.clipboardData.setData("text",window.getSelection().toString())})})();
`

#### 清空所有动态
*  适用页面为 B站主页--》右上角"动态"--》左边头像下方"动态"(`https://space.bilibili.com/xxxxxx/dynamic`)
*  脚本内容如下

`
setInterval(function(){$(".child-button")[1].click();$(".bp-popup-ctnr").find(".bl-button--size")[0].click();},500);
`

#### 删除关注的up主(慎用)
*  适用页面为 B站主页--》点击头像--》右边"关注数"(`https://space.bilibili.com/xxxxxx/fans/follow`)
*  脚本内容如下(一次只能删除一页)

`
`$(".be-dropdown-item:contains('取消关注')").click()
`

#### 删除互粉的粉丝(慎用)
*  适用页面为 B站主页--》点击头像--》右边"粉丝数"(`https://space.bilibili.com/xxxxxx/fans/fans`)
*  脚本内容如下(一次只能删除一页)

`
$(".be-dropdown-item:contains('取消关注')").click()
`

#### 关注话题页面up主(主要是抽奖话题)
*  适用页面为 带"#话题名称#"这样的标签点进去后的页面，比如动态中带有标签"#互动抽奖#"，点击后会跳转到
   [https://t.bilibili.com/topic/name/互动抽奖/feed](https://t.bilibili.com/topic/name/%E4%BA%92%E5%8A%A8%E6%8A%BD%E5%A5%96/feed)
   这样的地址，本脚本执行后会关注此页面上所有up主
*  脚本内容如下(页面刷新速度可能慢请耐心等待，浏览器可开多页面同时关注不同话题页面的up主)

`
(function(){function next(){$('.unfocus-text').click();setTimeout(next,3000);$('.card').remove()}next();})();
`

#### B站自动答题(非原创，未测试)
*  适用页面为 B站新用户答题页面
*  脚本内容如下

`
(function(){var jqserc="https://cdn.bootcss.com/jquery/3.3.1/jquery.min.js";var scr=document.createElement("script");scr.src=jqserc;document.head.appendChild(scr);function after1s(){return new Promise(res=>{setTimeout(res,1000)})}function afterS(value){return new Promise(res=>{setTimeout(()=>{res(value)},200)})}scr.onload=function(){var resArr=[];var $subbtn=$(".footer-bottom .btn-default");var isFirst=true;async function loop(){setTimeout(async()=>{var $error=$(".exam-list.error");if($error.length===0){if(!isFirst){$subbtn[0].click();return}}var $alltimu=$(".exam-list");var asyncIterable={[Symbol.asyncIterator](){return{i:0,next(){if(this.i<$alltimu.length){return afterS({value:{e:$alltimu[this.i++],i:this.i},done:false})}return Promise.resolve({done:true})}}}};for await({e,i}of asyncIterable){var $options=$(e).children(".key-list").children("li");var $active=$options.filter(".active");console.log(resArr);if($active.length===0){isFirst=false;$options[0].click();resArr[i]=0}if($(e).hasClass("error")){resArr[i]=resArr[i]+1;$options[resArr[i]].click()}}$subbtn[0].click();console.log("提交了");await after1s();loop()},2000)}window.onhashchange=function(e){if(e.newURL==="#/promotion"){}};loop()}})();
`