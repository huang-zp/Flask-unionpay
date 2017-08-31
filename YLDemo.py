# coding:utf-8
from flask import Flask,redirect,render_template
import OpenSSL
import hashlib
import base64
import datetime
app = Flask(__name__)

_GATEWAY = 'https://gateway.test.95516.com/gateway/api/frontTransReq.do '

cert = {}

def getCertIdWithPFX():
    fp = open('acp_test_sign.pfx', 'rb')
    if not fp:
        raise Exception('open %s fail!!!' % 'TriAxesGW.pfx')
    pkcs12certdata = fp.read()

    certs = OpenSSL.crypto.load_pkcs12(pkcs12certdata, '198309')

    x509data = certs.get_certificate()

    cert["certid"] = x509data.get_serial_number()
    params["certId"] = cert["certid"]
    cert["pkey"] =certs.get_privatekey()


order = '123456789'

params = {
    'version' : '5.1.0',                        # 版本
    'encoding' : 'UTF-8',                       # 编码
    'txnType' : '01',                           # 交易类型  01：消费
    'txnSubType' : '01',                        # 交易子类  01：自助消费
    'bizType' : '000201',                       # 产品类型  000201：B2C网关支付
    'frontUrl': 'http://127.0.0.1/back',        # 前台通知地址
    'backUrl': 'http://127.0.0.1/back',         # 后台通知地址 需外网
    'signMethod' : '01',                        # 签名方法  01：RSA签名
    'channelType' : '07',                       # 渠道类型  07：互联网
    'accessType' : '0',                         # 接入类型  0：普通商户直连接入
    'currencyCode': '156',                      # 交易币种  156：人民币
    'merId': '***************',                 # 商户代码
    'txnAmt' : '100'                            # 订单金额  100=1元
}


def build_sign_str(d):
    getCertIdWithPFX()
    req = []
    for key in sorted(d.keys()):
        if d[key] != '':
            req.append("%s=%s" % (key, d[key]))

    return '&'.join(req)


def build_signature():
    global order
    order = order +str(1)
    params['orderId'] = order                  # 商户订单号
    params['txnTime'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S")
    sha256 = hashlib.sha256(build_sign_str(params)).hexdigest()
    private = OpenSSL.crypto.sign(cert['pkey'],sha256,b'sha256')
    params["signature"] = base64.b64encode(private)

    return build_sign_str(params)



@app.route('/')
def index():
    params["signature"] = ''
    build_signature()

    result = "<html>\
    <head>\
        <meta http-equiv=\"Content-Type\" content=\"text/html; charset=" + "utf-8" + "\" />\
    </head>\
    <body onload=\"javascript:document.pay_form.submit();\">\
        <form id=\"pay_form\" name=\"pay_form\" action=\"" + _GATEWAY + "\" method=\"post\">"
    for key, value in params.iteritems():
        result = result + "    <input type=\"hidden\" name=\"" + str(key) + "\" id=\"" + str(key) + "\" value=\"" + str(value) + "\" />\n";
    result = result + "<!-- <input type=\"submit\" type=\"hidden\">-->\
        </form>\
    </body>\
    </html>"
    print result
    return result


@app.route('/back', methods=['POST', 'GET'])
def back():
    return 'back'

if __name__ == '__main__':
    app.run()