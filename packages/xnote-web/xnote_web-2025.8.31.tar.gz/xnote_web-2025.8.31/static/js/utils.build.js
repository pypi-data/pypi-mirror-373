/**
* Array 兼容增强包
*/
/**
* 判断数组中是否存在以start开头的字符串
* @param {string} start
*/
if (!Array.prototype.startsWith) {
Array.prototype.startsWith = function (start) {
var array = this;
for (var key in array) {
var item = array[key];
if (item === start) return true;
}
return false;
}
}
/**
* forEach遍历
* @param {function} callback
*/
if (!Array.prototype.forEach) {
Array.prototype.forEach = function (callback) {
var self = this;
for (var i = 0; i < self.length; i++) {
var item = self[i];
callback(item, i, self);
}
}
}
/**
* filter 函数兼容
*/
if (!Array.prototype.filter) {
Array.prototype.filter = function(fun) {
if (this === void 0 || this === null) {
throw new TypeError();
}
var t = Object(this);
var len = t.length >>> 0;
if (typeof fun !== "function") {
throw new TypeError();
}
var res = [];
var thisArg = arguments.length >= 2 ? arguments[1] : void 0;
for (var i = 0; i < len; i++) {
if (i in t) {
var val = t[i];
if (fun.call(thisArg, val, i, t))
res.push(val);
}
}
return res;
};
}
function objForEach(obj, fn) {
var key = void 0,
result = void 0;
for (key in obj) {
if (obj.hasOwnProperty(key)) {
result = fn.call(obj, key, obj[key]);
if (result === false) {
break;
}
}
}
};
function arrForEach(fakeArr, fn) {
var i = void 0,
item = void 0,
result = void 0;
var length = fakeArr.length || 0;
for (i = 0; i < length; i++) {
item = fakeArr[i];
result = fn.call(fakeArr, item, i);
if (result === false) {
break;
}
}
};
function num2hex(num) {
}
var HEXMAP = {
"0":0, '1':1, '2':2, '3':3,
'4':4, '5':5, '6':6, '7':7,
'8':8, '9':9, '0':0,
'a':10, 'b':11, 'c':12, 'd':13,
'e':14, 'f':15,
'A':10, 'B':11, 'C':12, 'D':13,
'E':14, 'F':15
};
var BINMAP = {
"0":0, '1':1, '2':2, '3':3,
'4':4, '5':5, '6':6, '7':7,
'8':8, '9':9, '0':0,
};
function _strfill(len, c) {
c = c || ' ';
s = "";
for(var i = 0; i < len; i++) {
s += c;
}
return s;
}
function _fmtnum(numval, limit) {
var max = Math.pow(10, limit);
if (numval > max) {
return "" + numval;
} else {
var cnt = 1;
var num = numval;
num /= 10;
while (num >= 1) {
cnt+=1;
num /= 10;
}
var zeros = limit - cnt;
return _strfill(zeros, '0') + numval;
}
}
function _fmtstr(strval, limit) {
if (strval.length < limit) {
return strval + _strfill(limit - strval.length);
} else {
strval = strval.substr(0, limit);
return strval;
}
}
function sFormat(fmt) {
var dest = "";
var idx = 1;
var hexmap = BINMAP;
for(var i = 0; i < fmt.length; i++) {
var c = fmt[i];
if (c == '%') {
switch (fmt[i+1]) {
case 's':
i+=1;
dest += arguments[idx];
idx+=1;
break;
case '%':
i+=1;
dest += '%';
break;
case '0':
case '1':
case '2':
case '3': case '4': case '5':
case '6': case '7': case '8':
case '8': case '9': {
var num = 0;
i += 1;
while (hexmap[fmt[i]] != undefined) {
num = num * 10 + hexmap[fmt[i]];
i+=1;
}
if (fmt[i] == 'd') {
var val = 0;
try {
val = parseInt(arguments[idx]);
} catch (e) {
console.log(e);
dest += 'NaN';
idx+=1;
break;
}
idx+=1;
dest += _fmtnum(val, num);
} else if (fmt[i] == 's') {
dest += _fmtstr(arguments[idx], num);
idx+=1;
}
i+=1;
}
break;
default:
dest += '%';
break;
}
} else {
dest += c;
}
}
return dest;
}
window.sformat = sFormat;
function hex2num(hex) {
var hexmap = HEXMAP;
if(hex[0] == '0' && (hex[1] == 'X' || hex[1] == 'x')) {
hex = hex.substr(2);
}
var num = 0;
for(var i = 0; i < hex.length; i++) {
var c = hex[i];
num = num * 16;
if (hexmap[c] == undefined) {
throw 'invalid char ' + c;
} else {
num += hexmap[c];
}
}
return num;
}
function stringStartsWith(chars) {
return this.indexOf(chars) === 0;
}
String.prototype.startsWith = String.prototype.startsWith || stringStartsWith;
String.prototype.endsWith = String.prototype.endsWith || function (ends) {
function _StrEndsWith(str, ends) {
return str.lastIndexOf(ends) === (str.length - ends.length);
}
if (!ends instanceof Array){
return _StrEndsWith(this, ends);
} else {
for (var i = 0; i < ends.length; i++) {
if (_StrEndsWith(this, ends[i])) {
return true;
}
}
return false;
}
}
String.prototype.count = String.prototype.count || function (dst) {
var count = 0;
var start = 0;
var index = -1;
while ((index = this.indexOf(dst, start)) != -1) {
count += 1;
start = index + 1;
}
return count;
}
String.prototype.format = String.prototype.format || function () {
var dest = "";
var idx = 0;
for(var i = 0; i < this.length; i++) {
var c = this[i];
if (c == '%') {
switch (this[i+1]) {
case 's':
i+=1;
dest += arguments[idx];
idx+=1;
break;
case '%':
i+=1;
dest += '%';
break;
default:
dest += '%';
break;
}
} else {
dest += c;
}
}
return dest;
}
/**
* @param {int} count
* @return {string}
*/
String.prototype.repeat = function (count) {
var value = this;
var str = "";
for (var i = 0; i < count; i++) {
str += value;
}
return str;
}
/**
* 访问字符串的某个下标字符
* @param {int} index
* @return {string}
*/
String.prototype.Get = function (index) {
if (index >= 0) {
return this[index];
} else {
var realIndex = this.length + index;
return this[realIndex];
}
}
/**
* 简单的模板渲染，这里假设传进来的参数已经进行了html转义
*/
function renderTemplate(templateText, object) {
return templateText.replace(/\$\{(.*?)\}/g, function (context, objKey) {
return object[objKey.trim()] || '';
});
}
/**
* 原型：字符串格式化
* @param args 格式化参数值
*/
/**
* 日期格式化
* @param {string} format 日期格式
*/
if (!Date.prototype.format) {
Date.prototype.format = function (format) {
var year = this.getFullYear();
var month = this.getMonth() + 1;
var day = this.getDate();
var hour = this.getHours();
var minute = this.getMinutes();
var second = this.getSeconds();
if (format == "yyyy-MM-dd") {
return sFormat("%d-%2d-%2d", year, month, day);
}
if (format == "HH:mm:ss") {
return sFormat("%2d:%2d:%2d", hour, minute, second);
}
return sFormat("%d-%2d-%2d %2d:%2d:%2d", year, month, day, hour, minute, second);
};
}
/**
* 获取窗口的宽度
*/
function getWindowWidth() {
if (window.innerWidth) {
return window.innerWidth;
} else {
return Math.min(document.body.clientHeight, document.documentElement.clientHeight);
}
};
function getWindowHeight() {
if (window.innerHeight) {
return window.innerHeight;
} else {
return Math.min(document.body.clientWidth, document.documentElement.clientWidth);
}
};
/**
* JQuery 扩展
* @author xupingmao
* @since 2021/09/19 19:41:58
* @modified 2022/04/03 21:16:04
* @filename jq-ext.js
*/
/**
* 获取表单数据
*/
$.fn.extend({
"formData": function () {
var data = {}
$(this).find("[name]").each(function (index, element) {
var key = $(element).attr("name");
var value = $(element).val();
data[key] = value;
});
return data;
},
"scrollBottom": function() {
if (this.length==0) {
return;
}
var height = this[0].scrollHeight;
$(this).scrollTop(height);
}
});
