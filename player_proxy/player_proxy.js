const qs = require('querystring');
const https = require('https');

exports.handler = (req, resp, context) => {
    var newheaders = req.headers;
    newheaders.host = 'api.bilibili.com';
    newheaders.referer='https://www.bilibili.com/';
    delete newheaders['x-forwarded-proto'];
    const option = {
    hostname: 'api.bilibili.com',
    //path: '/pgc/player/web/playurl?'+qs.stringify(req.queries),
    path: '/x/player/playurl?'+qs.stringify(req.queries),
    headers: newheaders
    };
    https.get(option, (res) => {
        var data='';
        res.on("data", function(chunk) {
            data += chunk;
            });
        res.on("end", () => {
            resp.setHeader('content-type','application/json');
            for (var key in res.headers) {
                var value = res.headers[key];
                resp.setHeader(key, value);
                }
            resp.send(data);
            });
    }).on('error', (e) => {
        console.error(e);
    });
}