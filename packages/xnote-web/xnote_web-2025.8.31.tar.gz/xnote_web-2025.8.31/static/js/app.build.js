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
/**
* xnote全局初始化
* @author xupingmao
* @since 2022/01/09 16:17:02
* @modified 2022/04/09 18:15:07
* @filename x-init.js
*/
if (window.xnote === undefined) {
var xnote = {};
xnote.device = {
contentWidth: 0,     // 内容的宽度，包括左侧主数据和侧边栏
contentLeftWidth: 0, // 左侧的宽度
isMobile: false, // 是否是移动端
isDesktop: true, // 默认是桌面端
leftNavWidth: 0, // 左侧导航宽度
end: 0
};
xnote.config = {};
xnote.config.serverHome = "";
xnote.config.isPrintMode = false;
xnote.config.nodeRole = "master";
xnote.config.isMaster = true;
xnote.MOBILE_MAX_WIDTH = 1000;
xnote.constants = {
MOBILE_MAX_WIDTH: 100
};
xnote.events = {};
xnote.events.resizeHooks = [];
xnote.table = {};
xnote.editor = {};
xnote.dialog = {};
xnote.layout = {};
xnote.state = {};
xnote.state.currentId = 0;
xnote.state.system = {};
xnote.state.system.keyupTime = new Date().getTime();
xnote.http = {};
xnote.string = {};
xnote.array = {};
xnote.tmp = {};
xnote.api = {};
xnote.action = {};
xnote.note = {};
xnote.message = {}
xnote.admin = {};
xnote.view = {}
}
xnote.registerApiModule = function (name) {
if (xnote.api[name] === undefined) {
xnote.api[name] = {};
}
};
xnote.createNewId = function() {
xnote.state.currentId++;
return xnote.state.currentId;
}
/**
* 注册API
* @param {string} apiName API名称
* @param {function} fn 函数
*/
xnote.registerApi = function (apiName, fn) {
if (xnote.api[apiName] === undefined) {
xnote.api[apiName] = fn;
} else {
var errMessage = "api is registered: " + apiName;
console.error(errMessage);
xnote.alert(errMessage);
}
}
xnote.isEmpty = function (value) {
return value === undefined || value === null || value === "";
};
xnote.isNotEmpty = function (value) {
return !xnote.isEmpty(value);
};
xnote.getOrDefault = function (value, defaultValue) {
if (value === undefined) {
return defaultValue;
}
return value;
};
xnote.execute = function (fn) {
return fn();
};
xnote.validate = {
"notUndefined": function (obj, errMsg) {
if (obj === undefined) {
xnote.alert(errMsg);
throw new Error(errMsg);
}
},
"isFunction": function (obj, errMsg) {
if (typeof obj !== 'function') {
xnote.alert(errMsg);
throw new Error(errMsg);
}
}
};
xnote.table.adjustWidth = function(selector) {
$(selector).each(function (element, index) {
var headings = $(this).find("th");
if (headings.length > 0) {
var width = 100 / headings.length;
headings.css("width", width + "%");
}
});
};
/**
* 追加CSS样式表
* @param {string} styleText 样式文本
*/
xnote.appendCSS = function (styleText) {
var style = document.createElement("style");
style.type = "text/css";
if (style.styleSheet) {
style.styleSheet.cssText = styleText;
} else {
style.innerHTML = styleText;
}
document.head.appendChild(style);
};
xnote.http.defaultFailHandler = function (err) {
console.log(err);
xnote.toast("服务器繁忙, 请稍后重试~");
};
xnote.http.resolveURL = function(url) {
if (url == "" || url[0] == "?") {
return url;
}
return xnote.config.serverHome + url;
}
xnote.http.post = function (url, data, callback, type) {
var newURL = xnote.http.resolveURL(url);
return $.post(newURL, data, callback, type).fail(xnote.http.defaultFailHandler);
}
xnote.http.internalPost = function(url, data, callback, type) {
var newURL = xnote.http.resolveURL(url);
return $.post(newURL, data, callback, type);
}
xnote.http.get = function (url, data, callback, type) {
var newURL = xnote.http.resolveURL(url);
return $.get(newURL, data, callback, type).fail(xnote.http.defaultFailHandler);
}
xnote.http.ajax = function(method, url, data, callback, dataType) {
var newURL = xnote.http.resolveURL(url);
return $.ajax({
url: newURL,
type: method,
dataType: dataType,
data: data,
success: callback
}).fail(xnote.http.defaultFailHandler);
}
xnote.http.internalGet = function(url, data, callback, type) {
return $.get(xnote.config.serverHome + url, data, callback, type);
}
xnote.isTyping = function() {
var now = new Date().getTime();
var typingGap = 200; // 200毫秒
return now - xnote.state.system.keyupTime < typingGap;
}
xnote.assert = function (expression, message) {
if (!expression) {
xnote.alert(message);
}
};
var XUI = function(window) {
function initSelect() {
$("select").each(function(index, ele) {
var self = $(ele);
var multiple = self.attr("multiple");
var children = self.find("option");
var value = self.attr("value");
if (value === undefined) {
return;
}
if (multiple === "multiple") {
var values = value.split(",");
for (var i = 0; i < children.length; i++) {
var child = children[i];
if (values.indexOf(child.value) >= 0) {
child.selected = "selected";
}
}
} else {
for (var i = 0; i < children.length; i++) {
var child = children[i];
if (value == child.value) {
child.selected = "selected";
}
}
}
});
}
function initCheckbox() {
$("input[type=checkbox]").each(function(index, ele) {
var self = $(ele);
var value = self.attr("default-value");
if (value == "on") {
self.attr("checked", "checked");
}
})
}
function initRadio() {
$("input[type=radio]").each(function(index, ele) {
var self = $(ele);
var value = self.attr("default-value");
if (value == self.val()) {
self.attr("checked", "checked");
}
});
}
function initXRadio() {
$(".x-radio").each(function(index, element) {
var self = $(element);
var option = self.attr("data-option");
var value = self.attr("data-value");
if (value == option) {
self.addClass("selected-link");
}
});
};
$(".link-btn").click(function() {
var link = $(this).attr("x-href");
if (!link) {
link = $(this).attr("href");
}
var confirmMessage = $(this).attr("confirm-message");
if (confirmMessage) {
xnote.confirm(confirmMessage, function (result) {
window.location.href = link;
});
} else {
window.location.href = link;
}
});
$(".prompt-btn").click(function() {
var action = $(this).attr("action");
var message = $(this).attr("message");
var defaultValue = $(this).attr("default-value");
var inputValue = prompt(message, defaultValue);
if (inputValue != "" && inputValue) {
var actionUrl = action + encodeURIComponent(inputValue);
$.get(actionUrl, function(resp) {
window.location.reload();
})
}
});
function initDefaultValue(event) {
initSelect();
initCheckbox();
initRadio();
initXRadio();
xnote.table.adjustWidth(".default-table");
if (xnote.initSelect2) {
xnote.initSelect2();
}
};
xnote.refresh = function () {
initDefaultValue();
xnote.addEventListener("init-default-value", initDefaultValue);
xnote.addEventListener("xnote.reload", initDefaultValue);
};
xnote.refresh();
};
$(document).ready(function() {
XUI(window);
$("body").on("keyup", function (event) {
xnote.state.system.keyupTime = new Date().getTime();
});
});
/**
* 指定索引对文本进行替换
* @param {string} text 原始文本
* @param {string} target 被替换的文本
* @param {string} replacement 新的文本
* @param {int} index 索引位置
* @returns
*/
xnote.string.replaceByIndex = function (text, target, replacement, index) {
var tokens = text.split(target);
var result = [];
for (var i = 0; i < tokens.length; i++) {
var token = tokens[i];
result.push(token);
if (i+1 == tokens.length) {
continue;
}
if (i == index) {
result.push(replacement);
} else {
result.push(target);
}
}
return result.join("");
};
/**
* 判断 srcArray 是否包含target
* @param {array} srcArray
* @param {object} target
* @param {function|undefined} equalsFunction
* @returns
*/
xnote.array.contains = function(srcArray, target, equalsFunction) {
if (equalsFunction === undefined) {
return srcArray.indexOf(target)>=0;
}
for (var i = 0; i < srcArray.length; i++) {
var srcItem = srcArray[i];
if (equalsFunction(srcItem, target)) {
return true;
}
}
return false;
}
/**
* 从srcArray中移除target元素,返回一个新的array
* @param {array} srcArray
* @param {array|object} target
* @param {function|undefined} equalsFunction 比较函数
* @returns
*/
xnote.array.remove = function(srcArray, target, equalsFunction) {
var result = [];
if (equalsFunction === undefined) {
equalsFunction = function (a,b) {
return a === b;
}
}
if (Array.isArray(target)) {
var contains = xnote.array.contains;
srcArray.forEach(function (item) {
if (!contains(target, item, equalsFunction)) {
result.push(item);
}
})
} else {
srcArray.forEach(function (item) {
if (!equalsFunction(item, target)) {
result.push(item);
}
})
}
return result;
};
/**
* xnote扩展事件
* @author xupingmao
* @since 2021/05/30 14:39:39
* @modified 2022/01/09 16:31:57
* @filename x-event.js
*/
xnote.execute(function(){
/**
* 代码来自 quarkjs
* 构造函数.
* @name EventDispatcher
* @class EventDispatcher类是可调度事件的类的基类，它允许显示列表上的任何对象都是一个事件目标。
*/
var EventDispatcher = function()
{
this._eventMap = {};
this._eventDescription = {};
};
/**
* 注册事件侦听器对象，以使侦听器能够接收事件通知。
*/
EventDispatcher.prototype.addEventListener = function(type, listener)
{
var map = this._eventMap[type];
if(map == null) map = this._eventMap[type] = [];
if(map.indexOf(listener) == -1)
{
map.push(listener);
return true;
}
return false;
};
/**
* 删除事件侦听器。
*/
EventDispatcher.prototype.removeEventListener = function(type, listener)
{
if(arguments.length == 1) return this.removeEventListenerByType(type);
var map = this._eventMap[type];
if(map == null) return false;
for(var i = 0; i < map.length; i++)
{
var li = map[i];
if(li === listener)
{
map.splice(i, 1);
if(map.length == 0) delete this._eventMap[type];
return true;
}
}
return false;
};
/**
* 删除指定类型的所有事件侦听器。
*/
EventDispatcher.prototype.removeEventListenerByType = function(type)
{
var map = this._eventMap[type];
if(map != null)
{
delete this._eventMap[type];
return true;
}
return false;
};
/**
* 删除所有事件侦听器。
*/
EventDispatcher.prototype.removeAllEventListeners = function()
{
this._eventMap = {};
};
/**
* 派发事件，调用事件侦听器。
*/
EventDispatcher.prototype.dispatchEvent = function(event)
{
var map = this._eventMap[event.type];
if(map == null) return false;
if(!event.target) event.target = this;
map = map.slice();
for(var i = 0; i < map.length; i++)
{
var listener = map[i];
if(typeof(listener) == "function")
{
listener.call(this, event);
}
}
return true;
};
/**
* 检查是否为指定事件类型注册了任何侦听器。
*/
EventDispatcher.prototype.hasEventListener = function(type)
{
var map = this._eventMap[type];
return map != null && map.length > 0;
};
/**
* 声明一个事件，在严格模式下，如果不声明无法使用，为了避免消息过多无法管理的问题
*/
EventDispatcher.prototype.defineEvent = function(type, description)
{
this._eventDescription[type] = description;
};
EventDispatcher.prototype.on = EventDispatcher.prototype.addEventListener;
EventDispatcher.prototype.un = EventDispatcher.prototype.removeEventListener;
EventDispatcher.prototype.fire = EventDispatcher.prototype.dispatchEvent;
xnote._eventDispatcher = new EventDispatcher();
xnote.addEventListener = xnote.on = function (type, listener) {
return xnote._eventDispatcher.addEventListener(type, listener);
};
xnote.dispatchEvent = xnote.fire = function (type, target) {
var event = {type: type, target: target};
return xnote._eventDispatcher.dispatchEvent(event);
};
});
/**
* xnote扩展函数
* @author xupingmao
* @since 2021/05/30 14:39:39
* @modified 2022/01/09 16:08:42
* @filename x-ext.js
*/
xnote.EXT_DICT = {};
xnote.getExtFunc = function (funcName) {
return xnote.EXT_DICT[funcName];
};
xnote.setExtFunc = function (funcName, func) {
xnote.EXT_DICT[funcName] = func;
};
/**
* xnote专用ui
* 依赖库
*   jquery
*   layer.js
* @author xupingmao
* @since 2017/10/21
* @modified 2022/04/16 20:24:02
*/
layer.photos = function(options, loop, key){
var cache = layer.cache||{}, skin = function(type){
return (cache.skin ? (' ' + cache.skin + ' ' + cache.skin + '-'+type) : '');
};
var dict = {};
options = options || {};
if(!options.photos) return;
var type = options.photos.constructor === Object;
var photos = type ? options.photos : {}, data = photos.data || [];
var start = photos.start || 0;
dict.imgIndex = (start|0) + 1;
dict.state = {};
dict.state.rotate = 0; // 旋转角度
dict.state.img = null; // 图片资源
options.img = options.img || 'img';
options.isMobile = options.isMobile || false;
var success = options.success;
delete options.success;
if(!type){ //页面直接获取
var parent = $(options.photos);
var pushData = function(){
data = [];
parent.find(options.img).each(function(index){
var othis = $(this);
othis.attr('layer-index', index);
data.push({
alt: othis.attr('alt'),
pid: othis.attr('layer-pid'),
src: othis.attr('layer-src') || othis.attr('src'),
thumb: othis.attr('src')
});
})
};
pushData();
if (data.length === 0) return;
loop || parent.on('click', options.img, function(){
var othis = $(this), index = othis.attr('layer-index');
layer.photos($.extend(options, {
photos: {
start: index,
data: data,
tab: options.tab
},
full: options.full
}), true);
pushData();
})
if(!loop) return;
} else if (data.length === 0){
return layer.msg('&#x6CA1;&#x6709;&#x56FE;&#x7247;');
}
dict.imgprev = function(key){
dict.imgIndex--;
if(dict.imgIndex < 1){
dict.imgIndex = data.length;
}
dict.tabimg(key);
};
dict.imgnext = function(key,errorMsg){
dict.imgIndex++;
if(dict.imgIndex > data.length){
dict.imgIndex = 1;
if (errorMsg) {return};
}
dict.tabimg(key)
};
dict.keyup = function(event){
if(!dict.end){
var code = event.keyCode;
event.preventDefault();
if(code === 37){
dict.imgprev(true);
} else if(code === 39) {
dict.imgnext(true);
} else if(code === 27) {
layer.close(dict.index);
}
}
}
dict.tabimg = function(key){
if(data.length <= 1) return;
photos.start = dict.imgIndex - 1;
layer.close(dict.index);
return layer.photos(options, true, key);
setTimeout(function(){
layer.photos(options, true, key);
}, 200);
}
dict.repaint = function(layero) {
console.log("layero", layero);
var img = dict.state.img;
var imgarea = [img.width, img.height];
var isRotate90 = dict.state.rotate == 90 || dict.state.rotate == 270;
if (isRotate90) {
imgarea = [img.height, img.width];
}
console.log("imgarea", imgarea);
var area = dict.calcArea(imgarea, options, true);
console.log("area", area);
var width = area[0];
var height = area[1];
var top = ($(window).height() - height) / 2;
var left = ($(window).width() - width) / 2;
var style = {
"width": width + "px",
"height": height + "px",
"left": left + "px",
"top": top + "px",
};
console.log("repaint style", style);
var imgLeft = 0;
var imgTop = 0;
if (isRotate90) {
imgLeft = ($(window).width()-height)/2;
imgTop = ($(window).height()-width)/2;
}
var imgCss = {
"position": "relative",
"width": "100%",
"left": 0,
"top": 0
};
if (isRotate90) {
imgCss = {
"position": "fixed",
"width": height,
"left": imgLeft,
"top": imgTop
};
}
console.log("img css", imgCss);
layero.css(style);
layero.find(".layui-layer-content").css("height", height);
layero.find("img").css(imgCss);
}
dict.calcArea = function (imgarea, options, returnNumber) {
var winarea;
if (options.isMobile) {
winarea = [$(window).width(), $(window).height()-64];
} else {
winarea = [$(window).width() - 100, $(window).height() - 100];
}
if(!options.full && (imgarea[0]>winarea[0]||imgarea[1]>winarea[1])){
var wh = [imgarea[0]/winarea[0],imgarea[1]/winarea[1]];//取宽度缩放比例、高度缩放比例
if(wh[0] > wh[1]){//取缩放比例最大的进行缩放
imgarea[0] = imgarea[0]/wh[0];
imgarea[1] = imgarea[1]/wh[0];
} else if(wh[0] < wh[1]){
imgarea[0] = imgarea[0]/wh[1];
imgarea[1] = imgarea[1]/wh[1];
}
}
var minsize = 150;
if (imgarea[0] < minsize && imgarea[1] < minsize) {
var ratio = Math.min(minsize/imgarea[0], minsize/imgarea[1]);
imgarea[0] = imgarea[0]*ratio;
imgarea[1] = imgarea[1]*ratio;
}
if (returnNumber) {
return imgarea;
}
return [imgarea[0]+'px', imgarea[1]+'px'];
}
dict.event = function(layero){
dict.bigimgPic.click(function() {
dict.imgsee.toggle();
});
dict.bigimg.find('.layui-layer-imgprev').on('click', function(event){
event.preventDefault();
dict.imgprev();
});
dict.bigimg.find('.layui-layer-imgnext').on('click', function(event){
event.preventDefault();
dict.imgnext();
});
dict.bigimg.find(".close-span").on("click", function(event) {
layer.close(dict.index);
});
dict.bigimg.find(".rotate-span").on("click", function(event) {
dict.state.rotate += 90;
dict.state.rotate %= 360;
dict.bigimg.find("img").css("transform", "rotate(" + dict.state.rotate + "deg)");
dict.repaint(layero);
})
$(document).on('keyup', dict.keyup);
var hammer = options.hammer;
if (hammer) {
hammer.on('swipeleft', function(e) {
dict.imgprev();
});
hammer.on('swiperight', function(e) {
dict.imgnext();
});
}
};
function loadImage(url, callback, error) {
var img = new Image();
img.src = url;
if(img.complete){
return callback(img);
}
img.onload = function(){
img.onload = null;
callback(img);
};
img.onerror = function(e){
img.onerror = null;
error(e);
};
};
dict.loadi = layer.load(1, {
shade: 'shade' in options ? false : 0.9,
scrollbar: false
});
function imgBarTop() {
if (options.hideBar) {
return "";
}
var bar = $("<div>").addClass("layui-layer-imgbar").addClass("imgbar-top").hide();
bar.append($("<span>").addClass("rotate-span").addClass("clickable").text("旋转"));
bar.append("&nbsp;");
var rightBox = $("<div>").addClass("float-right");
rightBox.append($("<span>").addClass("close-span").addClass("clickable").text("关闭"));
bar.append(rightBox);
return bar.prop("outerHTML");
}
function imgBarBottom() {
if (options.hideBar) {
return "";
}
return '<div class="layui-layer-imgbar imgbar-bottom" style="display:'
+ (key ? 'block' : '')
+ '"><span class="layui-layer-imgtit"><a target="_blank" href="'
+ data[start].src +  '">'+ (data[start].alt||'')
+ '</a><em>'+ dict.imgIndex +'/'+ data.length +'</em></span></div>';
}
loadImage(data[start].src, function(img){
dict.state.img = img;
layer.close(dict.loadi);
dict.index = layer.open($.extend({
type: 1,
id: 'layui-layer-photos',
area: dict.calcArea([img.width, img.height], options),
title: false,
shade: 0.9,
shadeClose: true,
closeBtn: false,
move: false,
moveType: 1,
scrollbar: false,
moveOut: false,
isOutAnim: false,
skin: 'layui-layer-photos' + skin('photos'),
content: '<div class="layui-layer-phimg">'
+imgBarTop()
+'<img src="'+ data[start].src +'" alt="'+ (data[start].alt||'') +'" layer-pid="'+ data[start].pid +'">'
+'<div class="layui-layer-imgsee">'
+(data.length > 1 ? '<span class="layui-layer-imguide"><a href="javascript:;" class="layui-layer-iconext layui-layer-imgprev"></a><a href="javascript:;" class="layui-layer-iconext layui-layer-imgnext"></a></span>' : '')
+imgBarBottom()
+'</div>'
+'</div>',
success: function(layero, index){
dict.bigimg = layero.find('.layui-layer-phimg');
dict.bigimgPic = layero.find('.layui-layer-phimg img');
dict.imgsee = layero.find(".layui-layer-imgbar");
layero.find(".layui-layer-imgnext,.layui-layer-imgprev").
css("position", "fixed").show();
layero.find(".layui-layer-imguide").show();
layero.find(".layui-layer-imgbar").show();
dict.event(layero);
options.tab && options.tab(data[start], layero);
typeof success === 'function' && success(layero);
}, end: function(){
dict.end = true;
$(document).off('keyup', dict.keyup);
}
}, options));
}, function(){
layer.close(dict.loadi);
layer.msg('&#x5F53;&#x524D;&#x56FE;&#x7247;&#x5730;&#x5740;&#x5F02;&#x5E38;<br>&#x662F;&#x5426;&#x7EE7;&#x7EED;&#x67E5;&#x770B;&#x4E0B;&#x4E00;&#x5F20;&#xFF1F;', {
time: 30000,
btn: ['&#x4E0B;&#x4E00;&#x5F20;', '&#x4E0D;&#x770B;&#x4E86;'],
yes: function(){
data.length > 1 && dict.imgnext(true,true);
}
});
});
};
(function () {
/**
* 获取窗口的宽度
*/
xnote.getWindowWidth = function() {
if (window.innerWidth) {
return window.innerWidth;
} else {
return Math.min(document.body.clientHeight, document.documentElement.clientHeight);
}
}
window.getWindowWidth = xnote.getWindowWidth;
xnote.getWindowHeight = function() {
if (window.innerHeight) {
return window.innerHeight;
} else {
return Math.min(document.body.clientWidth, document.documentElement.clientWidth);
}
}
window.getWindowHeight = xnote.getWindowHeight
/**
* 判断是否是PC设备，要求width>=800 && height>=600
*/
xnote.isDesktop = function() {
return getWindowWidth() >= 800;
}
window.isPc = xnote.isDesktop;
window.isDesktop = window.isDesktop;
window.isMobile = function() {
return !isPc();
};
xnote.isMobile = function() {
return $(window).width() < xnote.MOBILE_MAX_WIDTH;
};
/**
* 浏览器的特性的简单检测，并非精确判断。
* from quark.js
*/
function detectBrowser(ns)
{
var win = window;
var ua = ns.ua = navigator.userAgent;
ns.isWebKit = (/webkit/i).test(ua);
ns.isMozilla = (/mozilla/i).test(ua);
ns.isIE = (/msie/i).test(ua);
ns.isFirefox = (/firefox/i).test(ua);
ns.isChrome = (/chrome/i).test(ua);
ns.isSafari = (/safari/i).test(ua) && !this.isChrome;
ns.isMobile = (/mobile/i).test(ua);
ns.isOpera = (/opera/i).test(ua);
ns.isIOS = (/ios/i).test(ua);
ns.isIpad = (/ipad/i).test(ua);
ns.isIpod = (/ipod/i).test(ua);
ns.isIphone = (/iphone/i).test(ua) && !this.isIpod;
ns.isAndroid = (/android/i).test(ua);
ns.supportStorage = "localStorage" in win;
ns.supportOrientation = "orientation" in win;
ns.supportDeviceMotion = "ondevicemotion" in win;
ns.supportTouch = "ontouchstart" in win;
ns.supportCanvas = document.createElement("canvas").getContext != null;
ns.cssPrefix = ns.isWebKit ? "webkit" : ns.isFirefox ? "Moz" : ns.isOpera ? "O" : ns.isIE ? "ms" : "";
};
detectBrowser(xnote.device);
})();
/** 下拉组件
* @since 2020/01/11
* @modified 2020/01/22 00:29:27
*/
$.fn.extend({
"hideDropdown": function () {
var self = $(this);
if (self.hasClass("mobile")) {
self.animate({
"height": "0px"
}).removeClass("active");
self.parent().find(".dropdown-mask").hide();
xnote.enableBodyScroll();
} else {
self.slideUp("fast");
}
}
});
xnote.disableBodyScroll = function (e) {
$("body").css("overflow", "hidden");
}
xnote.enableBodyScroll = function (e) {
$("body").css("overflow", "auto");
}
xnote.showDropdown = function (target) {
var dropdownContent = $(target).siblings(".dropdown-content");
if (dropdownContent.hasClass("mobile")) {
console.log("dropdown mobile");
if (dropdownContent.hasClass("active")) {
return;
} else {
$(target).parent().find(".dropdown-mask").show();
dropdownContent.show().animate({
"height": "60%"
}).addClass("active");
xnote.disableBodyScroll();
}
} else {
dropdownContent.slideDown("fast");
if (dropdownContent.offset() && dropdownContent.offset().left < 0) {
dropdownContent.css("left", 0);
}
}
}
xnote.toggleDropdown = function (target) {
var dropdownContent = $(target).siblings(".dropdown-content");
if (dropdownContent.hasClass("mobile")) {
console.log("dropdown mobile");
if (dropdownContent.hasClass("active")) {
dropdownContent.hideDropdown();
} else {
$(target).parent().find(".dropdown-mask").show();
dropdownContent.show().animate({
"height": "60%"
}).addClass("active");
xnote.disableBodyScroll();
}
} else {
dropdownContent.slideToggle("fast");
if (dropdownContent.offset() && dropdownContent.offset().left < 0) {
dropdownContent.css("left", 0);
}
$(".dropdown-content").each(function (index, element) {
if (element != dropdownContent[0]) {
$(element).slideUp(0);
}
});
}
}
$(function () {
$(".dropdown").click(function (e) {
xnote.toggleDropdown(e.target);
});
$(".x-dropdown").click(function (e) {
xnote.toggleDropdown(e.target);
});
$("body").on("click", function (e) {
var target = e.target;
if ($(target).hasClass("dropdown") || $(target).hasClass("dropdown-btn")) {
return;
}
$(".dropdown-content").hideDropdown();
});
});
/** 图片处理 part of xnote-ui
* @filename x-photo.js
*/
$(function () {
$("body").on('click', ".x-photo", function (e) {
var src = $(this).attr("src");
var alt = $(this).attr("alt");
console.log(src);
var data = [];
var imageIndex = 0;
var target = e.target;
$(".x-photo").each(function(index, el) {
if (el == target) {
imageIndex = index;
}
var src = $(el).attr("data-src");
if (!src) {
src = $(el).attr("src");
}
data.push({
"alt": $(el).attr("alt"),
"pid": 0,
"src": src,
"thumb": ""
});
});
var hammer;
if (window.Hammer) {
hammer = new Hammer(document.body);
}
layer.photos({
"photos": {
"title": "", //相册标题
"id": 123,   //相册id
"start": imageIndex, //初始显示的图片序号，默认0
"data": data
},
"anim":5,
"hideBar": false,
"isMobile": xnote.isMobile(),
"hammer": hammer,
});
});
});
/** audio.js, part of xnote-ui
* @since 2020/01/05
* @modified 2022/01/09 16:09:02
**/
$(function(e) {
var audioEnabled = false;
$("body").on("click", ".x-audio", function(e) {
var src = $(this).attr("data-src");
layer.open({
type: 2,
content: src,
shade: 0
});
});
var AUDIO_MAP = {};
xnote.loadAudio = function (id, src) {
AUDIO_MAP[id] = new Audio(src);
}
xnote.playAudio = function (id) {
if (!audioEnabled) {
return;
}
var audioObject = AUDIO_MAP[id];
if (audioObject) {
audioObject.play();
}
}
});
/**
* xnote的公有方法
*/
var BASE_URL = "/static/lib/webuploader";
function createXnoteLoading() {
return loadingIndex = layer.load(2);
}
function closeXnoteLoading(index) {
layer.close(index);
}
xnote._initUploadEvent = function(uploader, fileSelector, successFn) {
var loadingIndex = 0;
uploader.on( 'fileQueued', function( file ) {
});
uploader.on( 'uploadProgress', function( file, percentage ) {
var percent = (percentage * 100).toFixed(2) + '%';
console.log('upload process ' + percent)
});
uploader.on( 'uploadBeforeSend', function (object, data, headers) {
$( '#uploadProgress' ).find('.progress').remove();
data.dirname = "auto";
})
uploader.on( 'uploadSuccess', function( file, resp) {
layer.close(loadingIndex);
if (resp.success) {
successFn(resp);
} else {
xnote.alert(resp.message);
}
});
uploader.on( 'uploadError', function( file ) {
console.error("uploadError", file);
layer.close(loadingIndex);
layer.alert('上传失败');
});
uploader.on( 'uploadComplete', function( file ) {
});
$(fileSelector).on("change", function (event) {
console.log(event);
var fileList = event.target.files; //获取文件对象
if (fileList && fileList.length > 0) {
loadingIndex = layer.load(2);
uploader.addFile(fileList);
}
});
};
xnote.createUploader = function(fileSelector, chunked, successFn) {
var req = {
fileSelector: fileSelector,
chunked: chunked,
successFn: successFn,
fixOrientation: true
}
if (chunked) {
req.fixOrientation = false;
}
return xnote.createUploaderEx(req);
}
/** 创建上传器
* @param {string} req.selector 选择器
* @param {boolean} req.chunked 是否分段上传
* @param {callback} req.successFn 成功的回调函数
* @param {boolean} req.fixOrientation 是否修复方向
* @param {string} fileName 文件名
*/
xnote.createUploaderEx = function(req) {
var fileSelector = req.fileSelector;
var chunked = req.chunked;
var successFn = req.successFn;
var fixOrientation = req.fixOrientation;
var fileName = req.fileName;
if (fileSelector == undefined) {
fileSelector = '#baseFilePicker';
}
var upload_service;
var serverHome = xnote.config.serverHome;
if (chunked == undefined) {
chunked = false;
}
if (chunked) {
upload_service = serverHome + "/fs_upload/range";
} else {
upload_service = serverHome + "/fs_upload";
}
var uploader = WebUploader.create({
auto: true,
swf: BASE_URL + '/Uploader.swf',
server: upload_service,
pick: fileSelector,
chunked: chunked,
chunkSize: 1024 * 1024 * 5,
chunkRetry: 10,
fileVal: "file",
threads: 1,
preserveHeaders: true,
});
uploader.on('uploadBeforeSend', function(object, data, headers) {
data.fix_orientation = fixOrientation;
data.name = fileName;
});
if (successFn) {
xnote._initUploadEvent(uploader, fileSelector, successFn);
}
return uploader;
};
xnote.uploadBlob = function(blob, prefix, successFn, errorFn) {
var fd = new FormData();
var loadingIndex = createXnoteLoading();
fd.append("file", blob);
fd.append("prefix", prefix);
fd.append("name", "auto");
var xhr = new XMLHttpRequest();
xhr.open('POST', '/fs_upload');
xhr.onload = function() {
closeXnoteLoading(loadingIndex);
if (xhr.readyState === 4) {
if (xhr.status === 200) {
var data = JSON.parse(xhr.responseText);
if (successFn) {
successFn(data);
} else {
console.log(data);
}
} else {
console.error(xhr.statusText);
if (errorFn) {
errorFn(xhr);
}
}
};
};
xhr.onerror = function(error) {
console.log(xhr.statusText);
closeXnoteLoading(loadingIndex);
if (errorFn) {
errorFn(error)
}
}
xhr.send(fd);
};
xnote.requestUploadAuto = function (fileSelector, chunked, successFn, errorFn) {
return xnote.requestUploadByOption({
fileSelector: fileSelector,
chunked: chunked,
successFn: successFn,
errorFn: errorFn,
fileName: "auto"
});
}
xnote.requestUpload = function(fileSelector, chunked, successFn, errorFn) {
return xnote.requestUploadByOption({
fileSelector: fileSelector,
chunked: chunked,
successFn: successFn,
errorFn: errorFn
});
}
xnote.requestUploadByOption = function (option) {
var fileSelector = option.fileSelector;
var chunked = option.chunked;
var successFn = option.successFn;
var errorFn = option.errorFn;
var fileName = option.fileName;
if (fileSelector == undefined) {
throw new Error("selector is undefined");
}
var loadingIndex = 0;
var uploader = window.xnote.createUploader(fileSelector, chunked);
uploader.on('fileQueued', function(file) {
console.log("file = " + file);
});
uploader.on('uploadProgress', function(file, percentage) {
});
uploader.on('uploadBeforeSend', function(object, data, headers) {
data.dirname = "auto";
data.name = fileName;
});
uploader.on('uploadSuccess', function(file, resp) {
console.log("uploadSuccess", file, resp);
closeXnoteLoading(loadingIndex);
successFn(resp);
});
uploader.on('uploadError', function(file) {
layer.alert('上传失败');
closeXnoteLoading(loadingIndex);
});
uploader.on('uploadComplete', function(file) {
console.log("uploadComplete", typeof(file), file);
});
$(fileSelector).click();
$(fileSelector).on("change", function(event) {
console.log(event);
var fileList = event.target.files; //获取文件对象
if (fileList && fileList.length > 0) {
uploader.addFile(fileList);
loadingIndex = createXnoteLoading();
}
event.target.files = [];
});
};
xnote.requestUploadByClip = function (e, filePrefix, successFn, errorFn) {
console.log(e);
var clipboardData = e.clipboardData || e.originalEvent
&& e.originalEvent.clipboardData || {};
if (clipboardData.items) {
items = clipboardData.items;
for (var index = 0; index < items.length; index++) {
var item  = items[index];
var value = item.value;
if (/image/i.test(item.type)) {
console.log(item);
e.preventDefault();
var loadingIndex = createXnoteLoading();
var blob = item.getAsFile();
xnote.uploadBlob(blob, filePrefix, function (resp) {
successFn(resp);
closeXnoteLoading(loadingIndex);
}, function (resp) {
if (errorFn) {
errorFn(resp);
}
closeXnoteLoading(loadingIndex);
});
}
}
}
}
/**
* 对话框实现
* 参考 https://www.layui.com/doc/modules/layer.html
*
* 对外接口:
* 1. 展示对话框并且自适应设备
*    xnote.showDialog(title, html, buttons = [], functions = [])
*    xnote.openDialog(title, html, buttons = [], functions = [])
*    xnote.showDialogEx(options)
*
* 2. 展示iframe页面
*    xnote.showIframeDialog(title, url)
*    xnote.showAjaxDialog(title, url, buttons, functions)
*
* 3. 展示选项的对话框
*    // option参数的定义 {html, title = false}
*    xnote.showOptionDialog(option)
*
* 4. 系统自带的弹窗替换
*    xnote.alert(message)
*    xnote.confirm(message, callback)
*    xnote.prompt(title, defaultValue, callback)
*    // 打开文本编辑的对话框
*    xnote.showTextDialog(title, text, buttons, functions)
*    xnote.openTextDialog(title, text, buttons, functions)
*
*/
if (window.xnote === undefined) {
throw new Error("xnote is undefined!");
}
var xnoteDialogModule = {}
xnote.dialog = xnoteDialogModule;
xnoteDialogModule.idToIndexMap = {};
xnoteDialogModule.handleOptions = function (options) {
if (options.dialogId === undefined) {
options.dialogId = this.createNewId();
}
return options;
}
xnote.getDialogArea = function () {
if (isMobile()) {
return ['100%', '100%'];
} else {
return ['600px', '80%'];
}
}
getDialogArea = xnote.getDialogArea;
xnote.getDialogAreaLarge = function() {
if (xnote.isMobile()) {
return ['100%', '100%'];
} else {
return ['80%', '80%'];
}
}
xnote.getDialogAreaFullScreen = function() {
return ["100%", "100%"];
}
xnote.getNewDialogId = function () {
var dialogId = xnote.state._dialogId;
if (dialogId === undefined) {
dialogId = 1;
} else {
dialogId++;
}
xnote.state._dialogId = dialogId;
return "_xnoteDialog" + dialogId;
}
xnoteDialogModule.showIframeDialog = function (title, url, buttons, functions) {
var area = getDialogArea();
return layer.open({
type: 2,
shadeClose: false,
title: title,
maxmin: true,
area: area,
content: url,
scrollbar: false,
btn: buttons,
functions: functions
});
}
xnoteDialogModule._getCloseAnim = function() {
if (xnote.isMobile()) {
return 2;
} else {
return undefined;
}
}
xnoteDialogModule.closeDialog = function (flag) {
if (xnote.isMobile()) {
anim = 2; // 向下滑出
}
if (flag === "last") {
var index = layer.index;
layer.close(index, xnoteDialogModule._getCloseAnim());
}
if (typeof(flag) === 'number') {
layer.close(flag, xnoteDialogModule._getCloseAnim());
}
}
xnoteDialogModule.openDialogEx = function (options) {
return xnoteDialogModule.openDialogExInner(options);
}
xnote.showDialogEx = function () {
return xnoteDialogModule.openDialogEx.apply(xnoteDialogModule, arguments);
}
/**
* 创建对话框
* @param {object} options 创建选项
* @param {string} options.title 标题
* @param {string} options.html HTML内容
* @param {list[string]} options.buttons 按钮文案
* @param {list[function]} options.functions 回调函数(第一个是成功的回调函数)
* @param {boolean} options.closeForYes 成功后是否关闭对话框(默认关闭)
* @returns index
*/
xnoteDialogModule.openDialogExInner = function (options) {
options = xnoteDialogModule.handleOptions(options);
var area = options.area;
var title = options.title;
var html  = options.html;
var buttons = options.buttons;
var functions = options.functions;
var anim = options.anim;
var closeBtn = options.closeBtn;
var onOpenFn = options.onOpenFn;
var shadeClose = xnote.getOrDefault(options.shadeClose, false);
var closeForYes = xnote.getOrDefault(options.closeForYes, true);
var template = options.template;
var defaultValues = options.defaultValues; // 模板的默认值
var yesFunction = function(index, layero, dialogInfo) {};
var successFunction = function(layero, index, that/*原型链的this对象*/) {};
var dialogId = options.dialogId;
if (template !== undefined && html !== undefined) {
throw new Error("不能同时设置template和html选项");
}
if (template !== undefined) {
var templateBody = $(template).html();
dialogId = xnote.getNewDialogId();
var ele = $("<div>").attr("id", dialogId).html(templateBody);
html = ele.prop("outerHTML");
if (defaultValues !== undefined) {
html = xnote.renderTemplate(html, defaultValues);
}
}
if (functions === undefined) {
functions = [];
}
if (!(functions instanceof Array)) {
functions = [functions];
}
if (functions.length>0) {
yesFunction = functions[0];
}
if (area === undefined) {
area = xnote.getDialogArea();
}
if (area == "large") {
area = xnote.getDialogAreaLarge();
}
if (area == "fullscreen") {
area = xnote.getDialogAreaFullScreen();
}
if (anim === undefined && xnote.isMobile()) {
anim = 2;
}
var params = {
type: 1,
title: title,
shadeClose: shadeClose,
closeBtn: closeBtn,
area: area,
content: html,
anim: anim,
success: successFunction,
scrollbar: false
}
if (buttons !== undefined) {
params.btn = buttons
params.yes = function (index, layero) {
console.log(index, layero);
var dialogInfo = {
id: dialogId
};
var yesResult = yesFunction(index, layero, dialogInfo);
if (yesResult === undefined && closeForYes) {
layer.close(index);
}
return yesResult;
}
}
var index = layer.open(params);
options.layerIndex = index;
xnoteDialogModule.idToIndexMap[dialogId] = index;
if (onOpenFn) {
onOpenFn(index);
}
return index;
}
/**
* 打开一个对话框
* @param {string} title 标题
* @param {string|DOM} html 文本或者Jquery-DOM对象 比如 $(".mybox")
* @param {array} buttons 按钮列表
* @param {array} functions 函数列表
* @returns 弹层的索引
*/
xnoteDialogModule.openDialog = function(title, html, buttons, functions) {
var options = {};
options.title = title;
options.html  = html;
options.buttons = buttons;
options.functions = functions;
return xnoteDialogModule.openDialogEx(options);
}
xnoteDialogModule.showDialog = function () {
return xnoteDialogModule.openDialog.apply(xnoteDialogModule, arguments);
}
xnoteDialogModule.openTextDialogByOption = function(options) {
var title = options.title;
var text = options.text;
var buttons = options.buttons;
var functions = options.functions;
var features = options.features;
var req = {};
var dialogId = xnoteDialogModule.createNewId();
req.title = title;
req.dialogId = dialogId;
/*
<div class="card dialog-body">
<textarea class="dialog-textarea"></textarea>
</div>
<div class="dialog-footer">
<div class="float-right">
<button class="large btn-default" data-dialog-id="{{!dialogId}}" onclick="xnote.dialog.closeByElement(this)">关闭</button>
</div>
</div>
*/
var div = $("<div>");
var textarea = $("<textarea>").addClass("dialog-textarea").text(text);
var dialogBody = $("<div>").addClass("card dialog-body").append(textarea);
var btnBox = $("<div>").addClass("float-right");
var closeBtn = $("<button>").attr("data-dialog-id", dialogId)
.addClass("btn large btn-default")
.attr("onclick", "xnote.dialog.closeByElement(this)")
.text("关闭");
var dialogFooter = $("<div>").addClass("dialog-footer").append(btnBox.append(closeBtn));
if (buttons === undefined) {
div.append(dialogBody);
div.append(dialogFooter);
} else {
div.append(textarea);
}
req.html = div.html();
req.buttons = buttons;
req.functions = functions;
if (features != undefined) {
xnote._updateDialogFeatures(req, features);
}
return xnote.showDialogEx(req);
}
xnoteDialogModule.openTextDialog = function(title, text, buttons, functions, features) {
return xnoteDialogModule.openTextDialogByOption({
title: title,
text: text,
buttons: buttons,
functions: functions,
features: features
});
}
xnote._updateDialogFeatures = function (options, features) {
for (var i = 0; i < features.length; i++) {
var item = features[i];
if (item === "large") {
options.area = "large";
}
}
}
/**
* 打开ajax对话框
* @param {object} options 打开选项
*/
xnoteDialogModule.openAjaxDialogEx = function (options) {
var respFilter = xnote.getOrDefault(options.respFilter, function (resp) {
return resp;
});
xnote.http.get(options.url, function (resp) {
options.html = respFilter(resp);
xnote.showDialogEx(options);
xnote.refresh();
});
}
/**
* 打开ajax对话框
* @param {string} title 对话框标题
* @param {string} url 对话框URL
* @param {list<string>} buttons 按钮名称
* @param {list<function>} functions 按钮对应的函数
*/
xnoteDialogModule.openAjaxDialog = function(title, url, buttons, functions) {
var options = {};
options.title = title;
options.buttons = buttons;
options.functions = functions;
options.url = url;
return xnoteDialogModule.openAjaxDialogEx(options);
}
xnoteDialogModule.showAjaxDialog = function () {
return xnoteDialogModule.openAjaxDialog.apply(xnoteDialogModule, arguments);
}
xnote.promptInternal = function(title, defaultValue, callback, formType) {
if (layer && layer.prompt) {
layer.prompt({
title: title,
value: defaultValue,
scrollbar: false,
formType: formType,
area: ['400px', '300px']
},
function(value, index, element) {
callback(value);
layer.close(index);
})
} else {
var result = prompt(title, defaultValue);
callback(result);
}
};
xnote.prompt = function(title, defaultValue, callback) {
return xnote.promptInternal(title, defaultValue, callback, 0);
};
xnote.promptTextarea = function (title, defaultValue, callback) {
var functions;
if (callback) {
functions = function (index, layero) {
var inputText = layero.find("textarea").val();
callback(inputText);
}
}
return xnote.openTextDialog(title, defaultValue, ["确定", "取消"], functions);
}
xnote.confirm = function(message, callback) {
if (layer && layer.confirm) {
layer.confirm(message,
function(index) {
callback(true);
layer.close(index);
});
} else {
var result = confirm(message);
callback(result);
}
};
xnote.alert = function(message) {
if (layer && layer.alert) {
layer.alert(message);
} else {
alert(message);
}
};
/**
* 展示Toast信息
* @param {string} message 展示信息
* @param {number} time 显示时间
* @param {function} callback 回调函数
*/
xnote.toast = function (message, time, callback) {
if (layer && layer.msg) {
layer.msg(message, {time: time});
} else {
myToast(message, time);
}
if (callback) {
if (time === undefined) {
time = 1000;
}
setTimeout(callback, time);
}
}
var myToast = function(message, timeout) {
if (timeout == undefined) {
timeout = 1000;
}
var maxWidth = $(document.body).width();
var maxHeight = $(document.body).height()
var fontSize = 14;
var toast = $("<div>").css({
"margin": "0 auto",
"position": "fixed",
"left": 0,
"top": "24px",
"font-size": fontSize,
"padding": "14px 18px",
"border-radius": "4px",
"background": "#000",
"opacity": 0.7,
"color": "#fff",
"line-height": "22px",
"z-index": 1000
});
toast.text(message);
$(document.body).append(toast);
var width = toast.outerWidth();
var left = (maxWidth - width) / 2;
if (left < 0) {
left = 0;
}
toast.css("left", left);
var height = toast.outerHeight();
var top = (maxHeight - height) / 2;
if (top < 0) {
top = 0;
}
toast.css("top", top);
setTimeout(function() {
toast.remove();
}, timeout);
}
window.showToast = window.xnote.toast;
/**
* 展示选项对话框
*/
xnoteDialogModule.showOptionDialog = function (option) {
var content = option.html;
if (option.title === undefined) {
option.title = false;
}
var oldStyle = $("body").css("overflow");
$("body").css("overflow", "hidden");
function recoveryStyle() {
$("body").css("overflow", oldStyle);
}
var dialogIndex = layer.open({
title: option.title,
closeBtn: false,
shadeClose: true,
btn: [],
content: content,
skin: "x-option-dialog",
yes: function (index, layero) {
layer.close(index);
recoveryStyle();
},
cancel: function() {
layer.close(index);
recoveryStyle();
}
});
$('#layui-layer-shade'+ dialogIndex).on('click', function(){
console.log("xnote.showOptionDialog: shadowClose event")
layer.close(dialogIndex);
recoveryStyle();
});
};
window.ContentDialog = {
open: function (title, content, size) {
var width = $(".root").width() - 40;
var area;
if (isMobile()) {
area = ['100%', '100%'];
} else {
if (size == "small") {
area = ['400px', '300px'];
} else {
area = [width + 'px', '80%'];
}
}
layer.open({
type: 1,
shadeClose: true,
title: title,
area: area,
content: content,
scrollbar: false
});
}
}
xnote.closeAllDialog = function() {
layer.closeAll();
}
$(function () {
$("body").on("click", ".dialog-btn", function() {
var dialogUrl = $(this).attr("dialog-url");
var dialogId = $(this).attr("dialog-id");
var dailogTitle = $(this).attr("dialog-title");
var optionSelector = $(this).attr("dialog-option-selector");
if (dialogUrl) {
$.get(dialogUrl, function(respHtml) {
xnote.showDialog(dailogTitle, respHtml);
xnote.fire("init-default-value");
})
} else if (optionSelector) {
var html = $(optionSelector).html();
var option = {};
option.html = html;
xnote.showOptionDialog(option);
} else {
xnote.alert("请定义[dialog-url]或者[dialog-option-selector]属性");
}
});
/**
* 初始化弹层
*/
function initDialog() {
$(".x-dialog-close").css({
"background-color": "red",
"float": "right"
});
$(".x-dialog").each(function(index, ele) {
var self = $(ele);
var width = window.innerWidth;
if (width < 600) {
dialogWidth = width - 40;
} else {
dialogWidth = 600;
}
var top = Math.max((getWindowHeight() - self.height()) / 2, 0);
var left = (width - dialogWidth) / 2;
self.css({
"width": dialogWidth,
"left": left
}).css("top", top);
});
$("body").css("overflow", "hidden");
}
function onDialogHide() {
$(".x-dialog").hide();
$(".x-dialog-background").hide();
$(".x-dialog-remote").remove(); // 清空远程的dialog
$("body").css("overflow", "auto");
}
$(".x-dialog-background").click(function() {
onDialogHide();
});
$(".x-dialog-close, .x-dialog-cancel").click(function() {
onDialogHide();
});
function doModal(id) {
initDialog();
$(".x-dialog-background").show();
$(".x-dialog-remote").show();
$("#" + id).show();
}
xnote.initDialog = initDialog;
});
xnoteDialogModule.closeByElement = function (target) {
var dialogId = $(target).attr("data-dialog-id");
if (dialogId) {
var index = xnoteDialogModule.idToIndexMap[dialogId];
layer.close(index, xnoteDialogModule._getCloseAnim());
} else {
var times = $(target).parents(".layui-layer").attr("times");
layer.close(times, xnoteDialogModule._getCloseAnim());
}
}
xnoteDialogModule.closeLast = function () {
xnoteDialogModule.closeDialog("last");
}
xnoteDialogModule.createNewId = function() {
return "dialog_" + xnote.createNewId();
}
xnote.openAjaxDialog = xnoteDialogModule.openAjaxDialog;
xnote.openAjaxDialogEx = xnoteDialogModule.openAjaxDialogEx;
xnote.showAjaxDialog = xnoteDialogModule.showAjaxDialog;
xnote.showDialog = xnoteDialogModule.showDialog;
xnote.showDialogEx = xnoteDialogModule.openDialogEx;
xnote.openDialogEx = xnoteDialogModule.openDialogEx;
xnote.openDialogExInner = xnoteDialogModule.openDialogExInner;
xnote.openDialog = xnoteDialogModule.openDialog;
xnote.closeDialog = xnoteDialogModule.closeDialog;
xnote.showIframeDialog = xnoteDialogModule.showIframeDialog;
xnote.showTextDialog = xnoteDialogModule.openTextDialog;
xnote.openTextDialog = xnoteDialogModule.openTextDialog;
xnote.showOptionDialog = xnoteDialogModule.showOptionDialog;
xnote.openTextArea = xnote.promptTextarea;
/** x-tab.js
* tab页功能，依赖jQuery
* 有两个样式: tab-link 和 tab-btn
*/
$(function (e) {
function initTabBtn() {
var hasActive = false;
var count = 0;
var pathAndSearch = location.pathname + location.search;
$(".x-tab-btn").each(function(index, ele) {
var link = $(ele).attr("href");
if (pathAndSearch == link) {
$(ele).addClass("active");
hasActive = true;
}
count += 1;
});
if (count > 0 && !hasActive) {
$(".x-tab-default").addClass("active");
}
}
xnote.handleTabClick = function (target) {
console.log("handleTabClick", target);
var parent = $(target).parent();
var tabContentId = parent.attr("data-content-id");
var tabContent = $("#" + tabContentId);
console.log("tabContent", tabContent);
var contentId = $(target).attr("data-content-id");
var contentHtml = $("#" + contentId).html();
tabContent.html(contentHtml);
parent.find(".x-tab").removeClass("active");
$(target).addClass("active");
}
function initTabBox() {
$(".x-tab-box").each(function (index, ele) {
var key = $(ele).attr("data-tab-key");
var defaultValue = $(ele).attr("data-tab-default");
var value = getUrlParam(key);
if ( xnote.isEmpty(value) ) {
value = defaultValue;
}
console.log("tab-value=",value);
var qValue = '"' + value + '"'; // 加引号quote
$(ele).find(".x-tab[data-tab-value=" + qValue + "]").addClass("active");
$(ele).find(".x-tab-btn[data-tab-value=" + qValue + "]").addClass("active");
$(ele).find(".x-tab").each(function (index, child) {
var childQuery = $(child);
var dataContentId = childQuery.attr("data-content-id");
if (dataContentId) {
childQuery.attr("onclick", "xnote.handleTabClick(this)");
if (childQuery.attr("data-default") == "true") {
childQuery.click();
}
return;
}
var oldHref = $(child).attr("href");
if ( xnote.isNotEmpty(oldHref) ) {
return;
}
var tabValue = $(child).attr("data-tab-value");
$(child).attr("href", xnote.addUrlParam(window.location.href, key, tabValue))
});
});
}
function initTabDefault() {
initTabBtn();
initTabBox();
}
initTabDefault();
xnote.addEventListener("init-default-value", initTabDefault);
});
$.fn.autoHeight = function(){
function autoHeight(elem){
elem.style.height = 'auto';
elem.scrollTop = 0; //防抖动
elem.style.height = elem.scrollHeight + 'px';
};
this.each(function(){
autoHeight(this);
$(this).on('keyup', function(){
autoHeight(this);
});
});
};
$.fn.showInScroll = function(offsetY) {
if (offsetY === undefined) {
offsetY = 0;
}
var parent = this.parent();
var offset = this.offset();
if (offset === undefined) {
return;
}
var topDiff = offset.top - parent.offset().top + offsetY;
parent.scrollTop(topDiff);
};
xnote.layout.getTextareaTextHeight = function(textarea) {
var $textarea = $(textarea);
var $clone = $('<div />')
.css({
position: 'absolute',
top: '-9999px',
left: '-9999px',
whiteSpace: 'pre-wrap',
wordWrap: 'break-word',
boxSizing: $textarea.css('box-sizing')
})
.width($textarea.outerWidth())
.appendTo('body');
var props = [
'fontFamily', 'fontSize', 'fontWeight', 'fontStyle',
'letterSpacing', 'textTransform', 'wordSpacing', 'textIndent',
'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
'borderTopWidth', 'borderRightWidth', 'borderBottomWidth', 'borderLeftWidth',
'lineHeight'
];
for (var i = 0; i < props.length; i++ ) {
var prop = props[i];
$clone.css(prop, $textarea.css(prop));
}
$clone.text($textarea.val() || $textarea.attr('placeholder') || '');
var height = $clone.outerHeight();
$clone.remove();
return height;
}
/**
* 模板渲染器
* @author xupingmao
* @since 2021/05/01 14:56:59
* @modified 2022/01/09 16:42:27
* @filename x-template.js
*/
/**
* 简单的模板渲染，这里假设传进来的参数已经进行了html转义
* <code>
*   var text = xnote.renderTemplate("Hello,${name}!", {name: "World"});
*   // text = "Hello,World";
* </code>
*/
xnote.renderTemplate = function(templateText, object) {
function escapeHTML(text) {
var temp = document.createElement("div");
temp.innerHTML = text;
return temp.innerText || temp.textContent
}
return templateText.replace(/\$\{(.+?)\}/g, function (context, objKey) {
var value = object[objKey.trim()] || '';
return escapeHTML(value);
});
};
xnote.renderArtTemplate = function(templateText, data, options) {
return template.render(templateText, data, options);
};
(function() {
function jqRenderTemplate(data, options) {
var templateText = $(this).text();
return template.render(templateText, data, options);
}
/**
* 获取表单数据
*/
$.fn.extend({
"render": jqRenderTemplate,
"renderTemplate": jqRenderTemplate,
});
})();
/**
* 解析URL参数
* @param {string} src 输入的URL
* @param {boolean} doDecode 是否进行decode操作
* @returns {object} 解析之后的对象
*/
xnote.parseUrl = function(src, doDecode) {
var path = '';
var args = {};
var state = 0;
var name = '';
var value = '';
if (doDecode === undefined) {
doDecode = false;
}
for(var i = 0; i < src.length; i++) {
var c = src[i]
if (c == '?' || c == '&') {
state = 1; // arg name;
if (name != '') {
args[name] = value;
}
name = '';
continue;
} else if (c == '=') { // arg value
state = 2;
value = '';
continue;
}
if (state == 0) {
path += c; // path state
} else if (state == 1) {
name += c; // arg name;
} else if (state == 2) {
value += c;
}
}
function formatValue(value) {
if (doDecode) {
return decodeURIComponent(value);
} else {
return value;
}
}
if (name != '') {
args[name] = formatValue(value);
}
return {'path': path, 'param': args};
}
/**
* 获取请求参数
*/
xnote.getUrlParams = function() {
var params = {};
var url = window.location.href;
url = url.split("#")[0];
var idx = url.indexOf("?");
if(idx > 0) {
var queryStr = url.substring(idx + 1);
var args = queryStr.split("&");
for(var i = 0, a, nv; a = args[i]; i++) {
nv = args[i] = a.split("=");
if (nv.length > 1) {
var value = nv[1];
try {
params[nv[0]] = decodeURIComponent(value);
} catch (e) {
params[nv[0]] = value;
console.warn('decode error', e)
}
}
}
}
return params;
};
/**
* 根据key获取url参数值
* @param {string} key
* @param {string} defaultValue 默认值
*/
xnote.getUrlParam = function (key, defaultValue) {
var paramValue = xnote.getUrlParams()[key];
if (paramValue === undefined) {
return defaultValue;
} else {
return paramValue;
}
}
/**
* 给指定的url添加参数
* @param {string} url 指定的url
* @param {string} key 参数的key
* @param {string} value 参数的value
*/
xnote.addUrlParam = function(url, key, value) {
var parsed = parseUrl(url);
var result = parsed.path;
var params = parsed.param;
var isFirst = true;
params[key] = encodeURIComponent(value);
for (var key in params) {
var paramValue = params[key];
if (isFirst) {
result += "?" + key + "=" + paramValue;
isFirst = false;
} else {
result += "&" + key + "=" + paramValue;
}
}
return result;
}
/**
* HTML转义
* @param {string} text 待转义的文本
* @returns {string}
*/
xnote.escapeHTML = function (text) {
return $("<div>").text(text).html();
}
window.parseUrl = xnote.parseUrl
window.getUrlParam = xnote.getUrlParam
window.getUrlParams = xnote.getUrlParams
window.addUrlParam = xnote.addUrlParam
xnote.table.handleAction = function (target) {
var url = $(target).attr("data-url");
var title = $(target).attr("data-title");
var xnoteDialogId = xnote.showIframeDialog(title, url, ["确认", "取消"]);
}
xnote.table.handleConfirmAction = function (target, event) {
if (event instanceof Event) {
event.preventDefault();
event.stopPropagation();
}
var method = $(target).attr("data-method");
var url = $(target).attr("data-url");
var msg = $(target).attr("data-msg");
var reloadUrl = $(target).attr("data-reload-url");
if (method == "") {
method = "GET";
}
xnote.confirm(msg, function () {
xnote.http.ajax(method, url, "", function (resp) {
console.log(resp);
if (resp.success) {
var msg = resp.message || "操作成功";
xnote.toast(msg);
setTimeout(function() {
if (reloadUrl) {
window.location.href = reloadUrl;
} else {
window.location.reload();
}
}, 1000);
} else {
xnote.toast(resp.message);
}
});
});
}
xnote.table.handleEditForm = function (target) {
var url = $(target).attr("data-url");
var title = $(target).attr("data-title");
xnote.http.get(url, function (respHtml) {
var options = {};
options.title = title;
options.html = respHtml;
xnote.showDialogEx(options);
});
}
xnote.table.handleViewDetail = function (target) {
var detail = $(target).attr("data-detail");
xnote.showTextDialog("查看详情", detail);
}
/**
* 通用的操作函数
*/
$(function () {
window.moveTo = function (selfId, parentId) {
$.post("/note/move",
{ id: selfId, parent_id: parentId },
function (resp) {
console.log(resp);
window.location.reload();
});
}
function showSideBar() {
$(".navMenubox").animate({ "margin-left": "0px" });
$("#poweredBy").show();
}
function hideSideBar() {
$(".navMenubox").animate({ "margin-left": "-200px" });
$("#poweredBy").hide();
}
function checkResize() {
if ($(".navMenubox").is(":animated")) {
return;
}
if (window.innerWidth < 600) {
hideSideBar();
} else {
showSideBar();
}
}
function toggleMenu() {
var marginLeft = $(".navMenubox").css("margin-left");
if (marginLeft == "0px") {
hideSideBar();
} else {
showSideBar();
}
}
$(".toggleMenu").on("click", function () {
toggleMenu();
});
});
/**
* 处理悬浮控件
*/
$(function () {
var width = 960;
var maxWidth = $(window).width();
var maxHeight = $(window).height();
var leftPartWidth = 200;
var btnRight = (maxWidth - width) / 2 + 20;
if (btnRight < 0) {
btnRight = 20;
}
var botHeight = "100%";
var botWidth = maxWidth / 2;
var bots = {};
function createIframe(src) {
return $("<iframe>")
.addClass("dialog-iframe")
.attr("src", src)
.attr("id", "botIframe");
}
function createCloseBtn() {
return $("<span>").text("Close").addClass("dialog-close-btn");
}
function createTitle() {
var btn1 = $("<span>").text("Home").addClass("dialog-title-btn dialog-home-btn");
var btn2 = $("<span>").text("Tools").addClass("dialog-title-btn dialog-tools-btn");
var btn3 = $("<span>").text("Refresh").addClass("dialog-title-btn dialog-refresh-btn");
return $("<div>").addClass("dialog-title")
.append(createCloseBtn())
.append(btn1).append(btn2).append(btn3);
}
function getBottomBot() {
if (bots.bottom) {
return bots.bottom;
}
var bot = $("<div>").css({
"position": "fixed",
"width": "100%",
"height": "80%",
"background-color": "#fff",
"border": "1px solid #ccc",
"bottom": "0px",
"right": "0px",
"z-index": 50
}).append(createIframe("/"));
bot.hide();
bot.attr("id", "x-bot");
$(document.body).append(bot);
bots.bottom = bot;
return bot;
}
function getIframeDialog() {
if (bots.dialog) {
return bots.dialog;
}
var mainWidth = $(".root").width();
var bot = $("<div>").css({
"position": "fixed",
"width": mainWidth,
"height": "80%",
"background-color": "#fff",
"border": "1px solid #ccc",
"bottom": "0px",
"right": "0px",
"z-index": 50
}).append(createIframe("/"));
bot.hide();
$(document.body).append(bot);
bots.dialog = bot;
return bot;
}
function initEventHandlers() {
console.log("init");
$("body").on("click", ".dialog-close-btn", function () {
getRightBot().fadeOut(200);
});
$("body").on("click", ".dialog-home-btn", function () {
$(".right-bot iframe").attr("src", "/");
});
$("body").on("click", ".dialog-tools-btn", function () {
$(".right-bot iframe").attr("src", "/fs_api/plugins");
});
$("body").on("click", ".dialog-refresh-btn", function () {
$(".right-bot iframe")[0].contentWindow.location.reload();
});
$("body").on("click", ".layer-btn", function (event) {
console.log("click");
var target = event.target;
var url = $(target).attr("data-url");
openDialog(url);
});
console.log("init done");
}
function getRightBot() {
if (bots.right) {
return bots.right;
}
var width = "50%";
if (maxWidth < 600) {
width = "100%";
}
var rightBot = $("<div>").css({
"position": "fixed",
"width": width,
"right": "0px",
"bottom": "0px",
"top": "0px",
"background-color": "#fff",
"border": "solid 1px #ccc",
"z-index": 50,
}).append(createTitle())
.append(createIframe("/system/index"))
.addClass("right-bot");
rightBot.hide();
$(document.body).append(rightBot);
bots.right = rightBot;
return rightBot;
}
function initSearchBoxWidth() {
if (window.SHOW_ASIDE == "False") {
$(".nav-left-search").css("width", "100%");
}
}
function init() {
$(".bot-btn").click(function () {
getRightBot().fadeToggle(200);
});
initSearchBoxWidth();
initEventHandlers();
}
function showIframeDialog(src) {
getRightBot().fadeIn(200);
$("#botIframe").attr("src", src);
}
function hideIframeDialog() {
getRightBot().fadeOut(200);
}
window.openDialog = function (url) {
var width = $(".root").width() - 40;
var area;
if (isMobile()) {
area = ['100%', '100%'];
} else {
area = [width + 'px', '80%'];
}
layer.open({
type: 2,
shadeClose: true,
title: '子页面',
maxmin: true,
area: area,
content: url,
scrollbar: false
});
}
window.showIframeDialog = showIframeDialog;
window.hideIframeDialog = hideIframeDialog;
window.toggleMenu = function () {
$(".aside-background").toggle();
$(".aside").toggle(500);
}
/**
* 调整高度，通过
* @param {string} selector 选择器
* @param {number} bottom 距离窗口底部的距离
*/
window.adjustHeight = function (selector, bottom, options) {
bottom = bottom || 0;
if ($(selector).length == 0) {
return;
}
var height = getWindowHeight() - $(selector).offset().top - bottom;
$(selector).css("height", height).css("overflow", "auto");
if (options != undefined) {
if (options.overflow) {
$(selector).css("overflow", options.overflow);
}
}
return height;
}
/**
* 调整导航栏，如果在iframe中，则不显示菜单
*/
window.adjustNav = function () {
if (self != top) {
$(".nav").hide();
$(".root").css("padding", "10px");
}
}
window.adjustTable = function () {
$("table").each(function (index, element) {
var count = $(element).find("th").length;
if (count > 0) {
$(element).find("th").css("width", 100 / count + '%');
}
});
}
$(".aside-background").on('click', function () {
toggleMenu();
});
if (window.PAGE_OPEN == "dialog") {
$(".dialog-link").click(function (e) {
e.preventDefault();
var url = $(this).attr("href");
var width = $(".root").width();
layer.open({
type: 2,
title: "查看",
shadeClose: true,
shade: 0.8,
area: [width + "px", "90%"],
scrollbar: false,
content: url
});
});
}
function processInIframe() {
}
if (self != top) {
processInIframe();
}
init();
});
xnote.events.fireUploadEvent = function (event) {
xnote.fire("fs.upload", event);
};
xnote.events.onUploadEvent = function (listener) {
xnote.on("fs.upload", listener);
};
xnote.events.fireUploadPrepareEvent = function (event) {
console.log("fireUploadPrepareEvent", event);
xnote.fire("fs.upload.prepare", event);
};
xnote.events.onUploadPrepareEvent = function (listener) {
xnote.on("fs.upload.prepare", listener);
};
var NoteView = {};
xnote.action.note = NoteView;
xnote.note = NoteView;
NoteView.wangEditor = null; // wangEditor
NoteView.defaultParentId = 0; // 默认的父级节点
NoteView.groupId = 0; // 当前笔记本
var noteAPI = {};
xnote.api.note = noteAPI;
/**
* 更新笔记的类目
* @deprecated 已废弃
* @param {object} req 更新请求
*/
xnote.updateNoteCategory = function (req) {
if (req === undefined) {
throw new Error("req is undefined");
}
if (req.noteId === undefined) {
throw new Error("req.noteId is undefined");
}
if (req.value === undefined) {
throw new Error("req.value is undefined");
}
var params = {
id: req.noteId,
key: "category",
value: req.value
};
xnote.http.post("/note/attribute/update", params, function (resp) {
console.log("update category", resp);
if (resp.code == "success") {
xnote.toast("更新类目成功");
if (req.doRefresh) {
window.location.reload();
}
} else {
xnote.alert(resp.message);
}
});
};
/**
* 更新类目的名称
* @param {object} req 请求对象
*/
xnote.updateCategoryName = function (req) {
if (req === undefined) {
throw new Error("req is undefined");
}
if (req.oldName === undefined) {
throw new Error("req.oldName is undefined");
}
if (req.code === undefined) {
throw new Error("req.code is undefined");
}
xnote.prompt("重命名类目", req.oldName, function (newName) {
var params = {
code: req.code,
name: newName
};
xnote.http.post("/api/note/category/update", params, function (resp) {
if (resp.code == "success") {
window.location.reload();
} else {
xnote.alert(resp.message);
}
});
});
};
/**
* 创建笔记接口
* @param {object} req
* @param {string} req.name 笔记名称
* @param {string} req.parentId 上级目录id
* @param {string} req.type 笔记类型
* @param {callback} req.callback 回调函数
*/
NoteView.create = function (req) {
xnote.validate.notUndefined(req.name, "req.name is undefined");
xnote.validate.notUndefined(req.parentId, "req.parentId is undefined");
xnote.validate.notUndefined(req.type, "req.type is undefined");
xnote.validate.isFunction(req.callback, "req.callback is not function");
var createOption = {};
createOption.name = req.name;
createOption.parent_id = req.parentId;
createOption.type = req.type;
createOption._format = "json";
var title = req.name;
xnote.http.post("/note/create", createOption, function (resp) {
if (resp.code == "success") {
req.callback(resp);
} else {
xnote.alert(title + "失败:" + resp.message);
}
});
};
xnote.api["note.create"] = NoteView.create;
xnote.api["note.copy"] = function (req) {
xnote.validate.notUndefined(req.name, "req.name is undefined");
xnote.validate.notUndefined(req.originId, "req.originId is undefined");
var copyOption = {
name: req.name,
origin_id: req.originId
};
var title = req.name;
xnote.http.post("/note/copy", copyOption, function (resp) {
if (resp.code == "success") {
req.callback(resp);
} else {
xnote.alert(title + "失败:" + resp.message);
}
});
};
noteAPI.bindTag = function (cmd) {
var currentTags = cmd.currentTags;
var targetId = cmd.targetId;
if (cmd.tagType != "group" && cmd.tagType != "note") {
throw new TypeError("无效的tagType");
}
var html = cmd.html;
xnote.openDialog("添加标签", html, ["确定", "取消"], function () {
var selectedNames = [];
$(".tag.bind.active").each(function (idx, ele) {
var tagName = $(ele).attr("data-code");
selectedNames.push(tagName);
});
var bindParams = {
tag_type: cmd.tagType,
group_id: cmd.groupId,
note_id: cmd.noteId,
tag_names: JSON.stringify(selectedNames),
};
xnote.http.post("/note/tag/bind", bindParams, function (resp) {
if (resp.code != "success") {
xnote.alert(resp.message);
} else {
xnote.toast("添加标签成功");
}
location.reload();
});
});
};
NoteView.onTagClick = function (target) {
$(target).toggleClass("active");
}
NoteView.editNoteTag = function (target) {
var parentId = $(target).attr("data-parent-id");
var noteId = $(target).attr("data-id");
var tagsJson = $(target).attr("data-tags");
var tagType = $(target).attr("data-tag-type");
if (xnote.isEmpty(tagType)) {
tagType = "note";
}
var listParams = {
tag_type: tagType,
group_id: parentId,
v: 2,
tags_json: tagsJson
};
xnote.http.get("/note/tag/bind_dialog", listParams, function (html) {
var cmd = {
tagType: "note", // 绑定类型始终是note
currentTags: JSON.parse(tagsJson),
noteId: noteId,
manageLink: "/note/manage?parent_id=" + parentId,
};
cmd.html = html;
noteAPI.bindTag(cmd);
})
};
NoteView.searchNote = function () {
var self = this;
var searchText = $("#note-search-text").val();
var api = "";
if (searchText == "") {
api = "/note/timeline/search_dialog?action=item_list&limit=100";
} else {
api = "/note/timeline/search_dialog?action=item_list&limit=100&key=" + searchText;
}
xnote.http.get(api, function (html) {
$(".note-search-dialog-body").html(html);
});
};
NoteView.openDialogToAddNote = function (event) {
var tagCode = $(event.target).attr("data-code");
xnote.http.get("/note/timeline/search_dialog?limit=100", function (html) {
xnote.openDialog("选择笔记", html, ["确定", "取消"], function () {
NoteView.addNoteToTag(tagCode);
});
});
};
/**
* @param {options.callback} 回调函数
*/
NoteView.openSearchNoteDialog = function (options) {
var callback = options.callback;
xnote.http.get("/note/timeline/search_dialog?limit=100", function (html) {
var dialogOptions = {};
dialogOptions.title = "选择笔记";
dialogOptions.buttons = ["确认", "取消"];
dialogOptions.closeForYes = false;
dialogOptions.html = html;
var yesFunction = function () {
var noteList = [];
$(".select-note-checkbox:checked").each(function (idx, ele) {
var noteId = $(ele).attr("data-id");
var noteName = $(ele).attr("data-name");
var url = $(ele).attr("data-url");
var noteInfo = {
"note_id": noteId,
"name": noteName,
"url": url
}
noteList.push(noteInfo);
});
console.log(noteList);
var result = callback(noteList);
console.info("callback result:", result, dialogOptions.layerIndex);
if (result) {
if (result.close) {
layer.close(dialogOptions.layerIndex);
}
}
}
dialogOptions.functions = [yesFunction];
xnote.openDialogEx(dialogOptions);
});
}
NoteView.addNoteToTag = function (tagCode) {
var selectedIds = [];
$(".select-note-checkbox:checked").each(function (idx, ele) {
var noteId = $(ele).attr("data-id");
selectedIds.push(noteId);
});
console.log(selectedIds);
var params = {
action: "add_note_to_tag",
tag_code: tagCode,
note_ids: selectedIds.join(",")
};
xnote.http.post("/note/tag/bind", params, function (resp) {
if (resp.code != "success") {
xnote.alert(resp.message);
} else {
xnote.toast("添加成功");
location.reload();
}
});
};
/**
* 选择笔记本-平铺视图
* 这个函数需要配合 group_select_script.html 使用
* @param {object} req
* @param {string} req.noteId 笔记ID
* @param {callback} req.callback 回调函数,参数是 (selectedId: int)
*/
NoteView.selectGroupFlat = function (req) {
var noteId = req.noteId;
var respData;
xnote.validate.isFunction(req.callback, "参数callback无效");
function bindEvent() {
$(".group-select-box").on("keyup", ".nav-search-input", function (event) {
var searchKey = $(this).val().toLowerCase();
var newData = [];
for (var i = 0; i < respData.length; i++) {
var item = respData[i];
if (item.name.toLowerCase().indexOf(searchKey) >= 0) {
newData.push(item);
}
}
renderData(newData);
});
$(".group-select-box").on("click", ".link", function (event) {
var dataId = $(event.target).attr("data-id");
req.callback(dataId);
});
}
function Section() {
this.children = [];
this.title = "title";
}
Section.prototype.add = function (item) {
this.children.push(item);
}
Section.prototype.isVisible = function () {
return this.children.length > 0;
}
function renderData(data) {
var first = new Section();
var second = new Section();
var last = new Section();
var firstGroup = new Section(); // 一级笔记本
for (var i = 0; i < data.length; i++) {
var item = data[i];
if (item.level >= 1) {
first.add(item);
} else if (item.level < 0) {
last.add(item);
} else if (item.parent_id == 0) {
firstGroup.add(item);
} else {
second.add(item);
}
}
first.title = "置顶";
firstGroup.title = "一级笔记本";
second.title = "其他笔记本";
last.title = "归档";
var groups = [first, firstGroup, second, last];
var hasNoMatch = (data.length === 0);
var html = $("#group_select_tpl").renderTemplate({
groups: groups,
noteId: noteId,
hasNoMatch: hasNoMatch
});
$(".group-select-data").html(html);
}
xnote.http.get("/note/api/group?list_type=all&orderby=name", function (resp) {
if (resp.code != "success") {
xnote.alert(resp.message);
return;
}
respData = resp.data;
xnote.showDialog("移动笔记", $(".group-select-box"));
bindEvent();
renderData(respData);
});
};
NoteView.selectGroupTree = function () {
}
NoteView.deleteTagMeta = function (tagMetaList) {
var html = $("#deleteTagTemplate").render({
tagList: tagMetaList,
});
xnote.openDialog("删除标签", html, ["确定删除", "取消"], function () {
var tagCodeList = [];
$(".tag.delete.active").each(function (idx, ele) {
var tagCode = $(ele).attr("data-tag-code");
tagCodeList.push(tagCode);
});
var deleteParams = {
tag_type: "group",
group_id: NoteView.groupId,
tag_code_list: JSON.stringify(tagCodeList),
};
xnote.http.post("/note/tag/delete", deleteParams, function (resp) {
if (!resp.code) {
xnote.alert(resp.message);
} else {
xnote.toast("删除成功,准备刷新...");
setTimeout(function () {
window.location.reload()
}, 500);
}
refreshTagTop();
});
});
};
NoteView.openDialogToMove = function (noteIds) {
if (noteIds == undefined) {
xnote.alert("noteIds 不能为空");
return;
}
var req = {};
req.callback = function (parentId) {
if (parentId === undefined || parentId == "") {
xnote.alert("parentId is undefined");
return;
}
xnote.http.post("/note/move", { note_ids: noteIds, parent_id: parentId }, function (resp) {
if (resp.success) {
console.log(resp);
window.location.reload();
} else {
xnote.alert(resp.message);
}
});
};
this.selectGroupFlat(req);
};
NoteView.openDialogToBatchMove = function (selector) {
var selected = $(selector);
if (selected.length == 0) {
xnote.alert("请先选中笔记本");
return;
}
var noteIds = [];
selected.each(function (index, elem) {
noteIds.push($(elem).attr("data-id"));
})
xnote.note.openDialogToMove(noteIds.join(","));
}
NoteView.openDialogToMoveByElement = function (target) {
return this.openDialogToMove($(target).attr("data-id"));
}
NoteView.onTagClick = function (target) {
$(target).toggleClass("active");
}
NoteView.openDialogToShare = function (target) {
var id = $(target).attr("data-id");
var type = $(target).attr("data-note-type");
var params = { note_id: id };
var ajax_dialog_url = "/note/ajax/share_group_dialog";
var ajax_dialog_title = "分享笔记本";
if (type != "group") {
ajax_dialog_url = "/note/ajax/share_note_dialog";
ajax_dialog_title = "分享笔记";
}
xnote.http.get(ajax_dialog_url, params, function (resp) {
xnote.showDialog(ajax_dialog_title, resp);
});
}
NoteView.changeOrderBy = function (target) {
var id = $(target).attr("data-id");
var orderby = $(target).val();
checkNotEmpty(id, "data-id为空");
checkNotEmpty(orderby, "data-orderby为空");
xnote.http.post("/note/orderby", { id: id, orderby: orderby }, function (resp) {
var code = resp.code;
if (code != "success") {
xnote.alert(resp.message);
} else {
xnote.toast(resp.message);
window.location.reload();
}
})
};
NoteView.changeLevel = function (target) {
var id = $(target).attr("data-id");
var status = $(target).val();
checkNotEmpty(id, "data-id为空");
checkNotEmpty(status, "data-status为空");
xnote.http.post("/note/status", { id: id, status: status }, function (resp) {
var code = resp.code;
if (code != "success") {
xnote.alert(resp.message);
} else {
xnote.toast(resp.message);
window.location.reload();
}
});
};
NoteView.initWangEditor = function () {
var editor = new wangEditor('#toolbar', "#editor");
editor.customConfig.uploadImgServer = false;
editor.customConfig.uploadImgShowBase64 = true;   // 使用 base64 保存图片
editor.customConfig.linkImgCallback = function (link) {
}
editor.create();
editor.txt.html($("#data").text());
this.wangEditor = editor;
}
NoteView.savePost = function (target) {
var noteId = $(target).attr("data-note-id");
var version = $(target).attr("data-note-version");
var data = this.wangEditor.txt.html();
xnote.http.post("/note/save?type=html", { id: noteId, version: version, data: data }, function (resp) {
console.log(resp);
if (resp.success) {
window.location.href = "/note/" + noteId;
} else {
xnote.alert(resp.message);
}
})
}
NoteView.remove = function (id, name, parentId, postAction) {
var confirmed = xnote.confirm("确定删除'" + name + "'?", function (confirmed) {
if (confirmed) {
xnote.http.post("/note/remove", { id: id }, function (resp) {
var code = resp.code;
if (code != "success") {
xnote.alert(resp.message);
} else {
if (postAction == "refresh") {
window.location.reload();
} else if (parentId) {
window.location.href = xnote.http.resolveURL("/note/" + parentId);
} else {
window.location.href = xnote.http.resolveURL("/");
}
}
})
}
});
}
NoteView.deleteByElement = function (target) {
var noteId = $(target).attr("data-id");
var name = $(target).attr("data-name");
var parentId = $(target).attr("data-prent-id");
var postAction = $(target).attr("data-post-action");
NoteView.remove(noteId, name, parentId, postAction);
}
NoteView.recover = function (noteId, callbackFn) {
var params = {
id: noteId
};
xnote.http.post("/note/recover", params, function (resp) {
if (resp.code == "success") {
callbackFn();
} else {
xnote.alert("恢复失败:" + resp.message);
}
}).fail(function (err) {
xnote.alert("网络错误，请稍后重试");
})
}
/** 创建分组
* @param {string} parentId 父级笔记ID
* @param {string} postAction 后置的动作 {refresh}
*/
NoteView.createGroup = function (parentId, postAction) {
var opName = "新建笔记本";
if (parentId === undefined) {
parentId = NoteView.defaultParentId;
}
xnote.prompt(opName, "", function (noteTitle) {
var createOption = {};
createOption.name = noteTitle;
createOption.parent_id = parentId;
createOption.type = "group";
createOption._format = "json";
xnote.http.post("/note/create", createOption, function (resp) {
if (postAction == "refresh") {
window.location.reload();
} else if (resp.code == "success") {
window.location = resp.url;
} else {
xnote.alert(opName + "失败:" + resp.message);
}
});
});
}
NoteView.createNotebook = NoteView.createGroup;
/**
* 重命名笔记
* @param {string} id 笔记ID
* @param {string} oldName 旧的名称
*/
NoteView.rename = function (id, oldName) {
xnote.prompt("新名称", oldName, function (newName) {
console.log(newName);
if (newName != "" && newName != null) {
xnote.http.post("/note/rename", { id: id, name: newName }, function (resp) {
var code = resp.code;
if (code != "success") {
xnote.alert(resp.message);
} else {
window.location.reload();
}
})
}
});
}
NoteView.renameByElement = function (target) {
var id = $(target).attr("data-id");
var oldName = $(target).attr("data-name");
if (id == undefined || id == "") {
xnote.alert("data-id为空");
return;
}
if (oldName == undefined || oldName == "") {
xnote.alert("data-name为空");
return;
}
NoteView.rename(id, oldName);
}
NoteView.updateOrderType = function (target) {
var noteId = $(target).attr("data-id");
var orderType = $(target).attr("data-value");
var params = {
note_id: noteId,
order_type: orderType
}
xnote.http.post("/note/order_type", params, function (resp) {
if (resp.success) {
window.location.reload();
} else {
xnote.alert(resp.message);
}
});
}
/**
* 打开笔记预览
* @param {Event} e
* @param {string} targetSelector
*/
NoteView.openPreviewPopup = function (e, targetSelector) {
e.preventDefault();
var offset = $(e.target).offset();
var name = $(e.target).text();
console.log("name", name);
if (xnote.isMobile()) {
offset.left = 0;
}
xnote.http.get("/note/preview_popup?name="+encodeURIComponent(name), function (html) {
if (html != "") {
offset.top += 20;
offset.left += 10;
console.log("offset", offset);
$(targetSelector).html(html).css(offset).show();
}
});
}
NoteView.initBtnCopy = function (copyBtnSelector, text, toastMessage) {
if (toastMessage === undefined) {
toastMessage = "已经复制到粘贴板";
}
$(copyBtnSelector).attr("data-clipboard-text", text);
new ClipboardJS(copyBtnSelector, {
text: function(trigger) {
xnote.toast(toastMessage);
return trigger.getAttribute('data-clipboard-text');
}
});
}
/**
* 文件相关函数
*/
var FileView = {};
var FileAPI = {};
xnote.action.fs = FileView;
xnote.api.fs = FileAPI;
FileAPI.rename = function(dirname, oldName, newName, callback) {
if (newName != oldName && newName) {
xnote.http.post("/fs_api/rename",
{dirname: dirname, old_name: oldName, new_name: newName},
function (resp) {
if (resp.code == "success") {
callback(resp);
} else {
xnote.alert("重命名失败:" + resp.message);
}
});
} else {
xnote.alert("请输入有效文件名");
}
};
FileView.delete = function(target) {
var path = $(target).attr("data-path");
var name = $(target).attr("data-name");
xnote.confirm("确定删除【" + name + "】?", function (value) {
xnote.http.post("/fs_api/remove", {path: path}, function (resp) {
if (resp.code == "success") {
window.location.reload();
} else {
xnote.alert("删除失败:" + resp.message);
}
});
});
};
FileView.rename = function(target) {
var filePath = $(target).attr("data-path");
var oldName = $(target).attr("data-name");
var realname = $(target).attr("data-realname");
if (xnote.isEmpty(realname)) {
realname = oldName;
}
var dirname = $("#currentDir").val();
xnote.prompt("输入新的文件名", oldName, function (newName) {
FileAPI.rename(dirname, realname, newName, function(resp) {
window.location.reload();
});
});
};
FileView.openOptionDialog = function (target, event) {
event.preventDefault();
event.stopPropagation();
console.log(target);
var filePath = $(target).attr("data-path");
var fileName = $(target).attr("data-name");
var fileRealName = $(target).attr("data-realname");
var dialogId = xnote.dialog.createNewId();
var filePathB64 = $(target).attr("data-path-b64");
var html = $("#fileItemOptionDialog").render({
"filePath": filePath,
"fileName": fileName,
"fileRealName": fileRealName,
"dialogId": dialogId,
"filePathB64": filePathB64,
});
var options = {};
options.title = "选项";
options.html  = html;
options.dialogId = dialogId;
xnote.openDialogEx(options);
};
FileView.showDetail = function(target) {
var dataPath = $(target).attr("data-path");
var params = {fpath: dataPath};
xnote.http.get("/fs_api/detail", params, function(resp) {
var message = ""
if (resp.success) {
message = resp.data;
} else {
message = resp.message;
}
xnote.showTextDialog("文件详情", message);
})
};
FileView.removeBookmark = function(event) {
event.preventDefault();
var path = $(event.target).attr("data-path")
var params = {
action:"remove",
path: path,
}
xnote.confirm("确定要取消收藏文件<code color=red>" + path + "</code>?", function () {
xnote.http.post("/fs_api/bookmark", params, function (resp) {
if (resp.code == "success") {
window.location.reload()
} else {
xnote.alert("取消收藏失败，请稍后重试!")
}
})
})
}
FileView.viewHex = function(target) {
var filePathB64 = $(target).attr("data-path-b64");
window.location.href = "/fs_hex?b64=true&path=" + filePathB64;
}
