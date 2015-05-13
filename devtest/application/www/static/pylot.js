(function() {

  window.S3Upload = (function() {

    S3Upload.prototype.s3_object_name = 'default_name';

    S3Upload.prototype.s3_sign_put_url = '/signS3put';

    S3Upload.prototype.file_dom_selector = 'file_upload';

    S3Upload.prototype.onFinishS3Put = function(public_url) {
      return console.log('base.onFinishS3Put()', public_url);
    };

    S3Upload.prototype.onProgress = function(percent, status) {
      return console.log('base.onProgress()', percent, status);
    };

    S3Upload.prototype.onError = function(status) {
      return console.log('base.onError()', status);
    };

    function S3Upload(options) {
      if (options == null) options = {};
      for (option in options) {
        this[option] = options[option];
      }
      this.handleFileSelect(document.getElementById(this.file_dom_selector));
    }

    S3Upload.prototype.handleFileSelect = function(file_element) {
      var f, files, output, _i, _len, _results;
      this.onProgress(0, 'Upload started.');
      files = file_element.files;
      output = [];
      _results = [];
      for (_i = 0, _len = files.length; _i < _len; _i++) {
        f = files[_i];
        _results.push(this.uploadFile(f));
      }
      return _results;
    };

    S3Upload.prototype.createCORSRequest = function(method, url) {
      var xhr;
      xhr = new XMLHttpRequest();
      if (xhr.withCredentials != null) {
        xhr.open(method, url, true);
      } else if (typeof XDomainRequest !== "undefined") {
        xhr = new XDomainRequest();
        xhr.open(method, url);
      } else {
        xhr = null;
      }
      return xhr;
    };

    S3Upload.prototype.executeOnSignedUrl = function(file, callback) {
      var this_s3upload, xhr;
      this_s3upload = this;
      xhr = new XMLHttpRequest();
      xhr.open('GET', this.s3_sign_put_url + '?s3_object_type=' + file.type + '&s3_object_name=' + this.s3_object_name, true);
      xhr.overrideMimeType('text/plain; charset=x-user-defined');
      xhr.onreadystatechange = function(e) {
        var result;
        if (this.readyState === 4 && this.status === 200) {
          try {
            result = JSON.parse(this.responseText);
          } catch (error) {
            this_s3upload.onError('Signing server returned some ugly/empty JSON: "' + this.responseText + '"');
            return false;
          }
          return callback(decodeURIComponent(result.signed_request), result.url);
        } else if (this.readyState === 4 && this.status !== 200) {
          return this_s3upload.onError('Could not contact request signing server. Status = ' + this.status);
        }
      };
      return xhr.send();
    };

    S3Upload.prototype.uploadToS3 = function(file, url, public_url) {
      var this_s3upload, xhr;
      this_s3upload = this;
      xhr = this.createCORSRequest('PUT', url);
      if (!xhr) {
        this.onError('CORS not supported');
      } else {
        xhr.onload = function() {
          if (xhr.status === 200) {
            this_s3upload.onProgress(100, 'Upload completed.');
            return this_s3upload.onFinishS3Put(public_url);
          } else {
            return this_s3upload.onError('Upload error: ' + xhr.status);
          }
        };
        xhr.onerror = function() {
          return this_s3upload.onError('XHR error.');
        };
        xhr.upload.onprogress = function(e) {
          var percentLoaded;
          if (e.lengthComputable) {
            percentLoaded = Math.round((e.loaded / e.total) * 100);
            return this_s3upload.onProgress(percentLoaded, percentLoaded === 100 ? 'Finalizing.' : 'Uploading.');
          }
        };
      }
      xhr.setRequestHeader('Content-Type', file.type);
      xhr.setRequestHeader('x-amz-acl', 'public-read');
      return xhr.send(file);
    };

    S3Upload.prototype.uploadFile = function(file) {
      var this_s3upload;
      this_s3upload = this;
      return this.executeOnSignedUrl(file, function(signedURL, publicURL) {
        return this_s3upload.uploadToS3(file, signedURL, publicURL);
      });
    };

    return S3Upload;

  })();

}).call(this);

$(function(){
  /**
  How to use

<input s3:upload
       type="file"

       id="profile-pic"

       // The id of this element
       data-id="profile-pic"

       // The prefix to help name the file
       data-filename-prefix="profile-pic/{{ current_user.id }}"

       // The name of the file. If empty it will use the filename of the file
       data-filename=""

       // Type of upload
       data-type="image"

       // The url to request the signed url for s3 upload
       data-s3-url="{{ url_for('Login:sign_s3_upload') }}"

       //-- Ajax upload of data --
       // The url to update the s3  url after upload
       data-update-url="{{ url_for('Login:change_profile_pic') }}"
       // The name of the POST field
       data-update-name="profile_pic_url"

       //-- Update form --
       // The form target to update the $url with
       data-target="#profile-pic-url"

       // The element to show the status
       data-status="#status"
       // The element to show the preview
       data-preview="#preview"
>
<div id="status">
<div id="preview">
<form action>
  <input type="hidden" id="profile-pic-url" name="profile-pic-url">
</form>

  **/
  $("input[s3\\:upload]").change(function(){
      var el = $(this)
      var status_el = $(el.data("status"))
      var preview_el = $(el.data("preview"))
      var target_el =  $(el.data("form-target"))
      var input_file = el.val()
      var filename = el.data("filename-prefix") + "/" + input_file.split(/(\\|\/)/g).pop()

      if (el.data("filename")) {
        filename = el.data("filename-prefix") + "/" + el.data("filename")
      }

     switch(el.data("type")) {
        case "image":
          if (! input_file.match(/\.(jpg|jpeg|png|gif)$/)) {
            alert("You must select an image")
            return null
          }
          break
     }

      var s3upload = new S3Upload({
          s3_object_name: filename,
          file_dom_selector: el.data("id"),
          s3_sign_put_url: el.data("s3-url"),

          onProgress: function(percent, message) {
              status_el.removeClass("alert-danger")
              .removeClass("alert-success")
              .addClass("alert-info")
              .html('Upload progress: ' + percent + '% ' + message);
          },
          onFinishS3Put: function(url) {
              status_el.removeClass("alert-danger")
              .removeClass("alert-info")
              .addClass("alert-success")
              .html('Upload completed');

              // Upload to url
              if (el.data("update-url")) {
                 _d = {}
                 _d[el.data("update-name")] = url
                 _d["_ajax"] = 1
                 $.post(el.data("update-url"), _d)
              } else { // form target
                    target_el.val(url);
              }


              preview_el.html('<img src="'+url+'" style="width:300px;" />');
          },
          onError: function(status) {
              status_el.removeClass("alert-success")
              .removeClass("alert-info")
              .addClass("alert-danger")
              .html('Upload error. Try again');
              console.log('Upload error: ' + status)
          }
      });

  })
})
var hello=function(e){return hello.use(e)};hello.utils={extend:function(e){for(var t=Array.prototype.slice.call(arguments,1),n=0;n<t.length;n++){var o=t[n];if(e instanceof Object&&o instanceof Object&&e!==o)for(var i in o)e[i]=hello.utils.extend(e[i],o[i]);else e=o}return e}},hello.utils.extend(hello,{settings:{redirect_uri:window.location.href.split("#")[0],response_type:"token",display:"popup",state:"",oauth_proxy:"https://auth-server.herokuapp.com/proxy",timeout:2e4,default_service:null,force:!0,page_uri:window.location.href},service:function(e){return"undefined"!=typeof e?this.utils.store("sync_service",e):this.utils.store("sync_service")},services:{},use:function(e){var t=this.utils.objectCreate(this);return t.settings=this.utils.objectCreate(this.settings),e&&(t.settings.default_service=e),t.utils.Event.call(t),t},init:function(e,t){var n=this.utils;if(!e)return this.services;for(var o in e)e.hasOwnProperty(o)&&"object"!=typeof e[o]&&(e[o]={id:e[o]});n.extend(this.services,e);for(o in this.services)this.services.hasOwnProperty(o)&&(this.services[o].scope=this.services[o].scope||{});return t&&(n.extend(this.settings,t),"redirect_uri"in t&&(this.settings.redirect_uri=n.url(t.redirect_uri).href)),this},login:function(){function e(e,t){hello.emit(e,t)}function t(e,t){return{error:{code:e,message:t}}}function n(e){return e}var o,i=this,a=i.utils,r=a.Promise(),s=a.args({network:"s",options:"o",callback:"f"},arguments),l=s.options=a.merge(i.settings,s.options||{});if(s.network=s.network||i.settings.default_service,r.proxy.then(s.callback,s.callback),r.proxy.then(e.bind(this,"auth.login auth"),e.bind(this,"auth.failed auth")),"string"!=typeof s.network||!(s.network in i.services))return r.reject(t("invalid_network","The provided network was not recognized"));var u=i.services[s.network],c=a.globalEvent(function(e){var n;n=e?JSON.parse(e):t("cancelled","The authentication was not completed"),n.error?r.reject(n):(a.store(n.network,n),r.fulfill({network:n.network,authResponse:n}))}),d=a.url(l.redirect_uri).href,f=u.oauth.response_type||l.response_type;/\bcode\b/.test(f)&&!u.oauth.grant&&(f=f.replace(/\bcode\b/,"token")),s.qs={client_id:encodeURIComponent(u.id),response_type:encodeURIComponent(f),redirect_uri:encodeURIComponent(d),display:l.display,scope:"basic",state:{client_id:u.id,network:s.network,display:l.display,callback:c,state:l.state,redirect_uri:d}};var p=a.store(s.network),m=(l.scope||"").toString();if(m=(m?m+",":"")+s.qs.scope,p&&"scope"in p&&p.scope instanceof String&&(m+=","+p.scope),s.qs.state.scope=a.unique(m.split(/[,\s]+/)).join(","),s.qs.scope=m.replace(/[^,\s]+/gi,function(e){if(e in u.scope)return u.scope[e];for(var t in i.services){var n=i.services[t].scope;if(n&&e in n)return""}return e}).replace(/[,\s]+/gi,","),s.qs.scope=a.unique(s.qs.scope.split(/,+/)).join(u.scope_delim||","),l.force===!1&&p&&"access_token"in p&&p.access_token&&"expires"in p&&p.expires>(new Date).getTime()/1e3){var h=a.diff(p.scope||[],s.qs.state.scope||[]);if(0===h.length)return r.fulfill({unchanged:!0,network:s.network,authResponse:p}),r}if("page"===l.display&&l.page_uri&&(s.qs.state.page_uri=a.url(l.page_uri).href),"login"in u&&"function"==typeof u.login&&u.login(s),(!/\btoken\b/.test(f)||parseInt(u.oauth.version,10)<2||"none"===l.display&&u.oauth.grant&&p&&p.refresh_token)&&(s.qs.state.oauth=u.oauth,s.qs.state.oauth_proxy=l.oauth_proxy),s.qs.state=encodeURIComponent(JSON.stringify(s.qs.state)),1===parseInt(u.oauth.version,10)?o=a.qs(l.oauth_proxy,s.qs,n):"none"===l.display&&u.oauth.grant&&p&&p.refresh_token?(s.qs.refresh_token=p.refresh_token,o=a.qs(l.oauth_proxy,s.qs,n)):o=a.qs(u.oauth.auth,s.qs,n),"none"===l.display)a.iframe(o);else if("popup"===l.display)var g=a.popup(o,d,l.window_width||500,l.window_height||550),v=setInterval(function(){if((!g||g.closed)&&(clearInterval(v),!r.state)){var e=t("cancelled","Login has been cancelled");g||(e=t("blocked","Popup was blocked")),e.network=s.network,r.reject(e)}},100);else window.location=o;return r.proxy},logout:function(){function e(e,t){hello.emit(e,t)}function t(e,t){return{error:{code:e,message:t}}}var n=this,o=n.utils,i=o.Promise(),a=o.args({name:"s",options:"o",callback:"f"},arguments);if(a.options=a.options||{},i.proxy.then(a.callback,a.callback),i.proxy.then(e.bind(this,"auth.logout auth"),e.bind(this,"error")),a.name=a.name||this.settings.default_service,!a.name||a.name in n.services)if(a.name&&o.store(a.name)){var r=function(e){o.store(a.name,""),i.fulfill(hello.utils.merge({network:a.name},e||{}))},s={};if(a.options.force){var l=n.services[a.name].logout;if(l)if("function"==typeof l&&(l=l(r)),"string"==typeof l)o.iframe(l),s.force=null,s.message="Logout success on providers site was indeterminate";else if(void 0===l)return i.proxy}r(s)}else i.reject(t("invalid_session","There was no session to remove"));else i.reject(t("invalid_network","The network was unrecognized"));return i.proxy},getAuthResponse:function(e){return e=e||this.settings.default_service,e&&e in this.services?this.utils.store(e)||null:null},events:{}}),hello.utils.extend(hello.utils,{qs:function(e,t,n){if(t){var o;for(var i in t)if(e.indexOf(i)>-1){var a="[\\?\\&]"+i+"=[^\\&]*";o=new RegExp(a),e=e.replace(o,"")}}return e+(this.isEmpty(t)?"":(e.indexOf("?")>-1?"&":"?")+this.param(t,n))},param:function(e,t){var n,o,i={};if("string"==typeof e){if(t=t||decodeURIComponent,o=e.replace(/^[\#\?]/,"").match(/([^=\/\&]+)=([^\&]+)/g))for(var a=0;a<o.length;a++)n=o[a].match(/([^=]+)=(.*)/),i[n[1]]=t(n[2]);return i}t=t||encodeURIComponent;var r=e;i=[];for(var s in r)r.hasOwnProperty(s)&&r.hasOwnProperty(s)&&i.push([s,"?"===r[s]?"?":t(r[s])].join("="));return i.join("&")},store:function(e){function t(){var t={};try{t=JSON.parse(e.getItem("hello"))||{}}catch(n){}return t}function n(t){e.setItem("hello",JSON.stringify(t))}var o=[e,window.sessionStorage],i=0;for(e=o[i++];e;)try{e.setItem(i,i),e.removeItem(i);break}catch(a){e=o[i++]}return e||(e={getItem:function(e){e+="=";for(var t=document.cookie.split(";"),n=0;n<t.length;n++){var o=t[n].replace(/(^\s+|\s+$)/,"");if(o&&0===o.indexOf(e))return o.substr(e.length)}return null},setItem:function(e,t){document.cookie=e+"="+t}}),function(e,o,i){var a=t();if(e&&void 0===o)return a[e]||null;if(e&&null===o)try{delete a[e]}catch(r){a[e]=null}else{if(!e)return a;a[e]=o}return n(a),a||null}}(window.localStorage),append:function(e,t,n){var o="string"==typeof e?document.createElement(e):e;if("object"==typeof t)if("tagName"in t)n=t;else for(var i in t)if(t.hasOwnProperty(i))if("object"==typeof t[i])for(var a in t[i])t[i].hasOwnProperty(a)&&(o[i][a]=t[i][a]);else"html"===i?o.innerHTML=t[i]:/^on/.test(i)?o[i]=t[i]:o.setAttribute(i,t[i]);return"body"===n?!function r(){document.body?document.body.appendChild(o):setTimeout(r,16)}():"object"==typeof n?n.appendChild(o):"string"==typeof n&&document.getElementsByTagName(n)[0].appendChild(o),o},iframe:function(e){this.append("iframe",{src:e,style:{position:"absolute",left:"-1000px",bottom:0,height:"1px",width:"1px"}},"body")},merge:function(){var e=Array.prototype.slice.call(arguments);return e.unshift({}),this.extend.apply(null,e)},args:function(e,t){var n={},o=0,i=null,a=null;for(a in e)if(e.hasOwnProperty(a))break;if(1===t.length&&"object"==typeof t[0]&&"o!"!=e[a])for(a in t[0])if(e.hasOwnProperty(a)&&a in e)return t[0];for(a in e)if(e.hasOwnProperty(a))if(i=typeof t[o],"function"==typeof e[a]&&e[a].test(t[o])||"string"==typeof e[a]&&(e[a].indexOf("s")>-1&&"string"===i||e[a].indexOf("o")>-1&&"object"===i||e[a].indexOf("i")>-1&&"number"===i||e[a].indexOf("a")>-1&&"object"===i||e[a].indexOf("f")>-1&&"function"===i))n[a]=t[o++];else if("string"==typeof e[a]&&e[a].indexOf("!")>-1)return!1;return n},url:function(e){if(e){if(window.URL&&URL instanceof Function&&0!==URL.length)return new URL(e,window.location);var t=document.createElement("a");return t.href=e,t}return window.location},diff:function(e,t){for(var n=[],o=0;o<t.length;o++)-1===this.indexOf(e,t[o])&&n.push(t[o]);return n},indexOf:function(e,t){if(e.indexOf)return e.indexOf(t);for(var n=0;n<e.length;n++)if(e[n]===t)return n;return-1},unique:function(e){if("object"!=typeof e)return[];for(var t=[],n=0;n<e.length;n++)e[n]&&0!==e[n].length&&-1===this.indexOf(t,e[n])&&t.push(e[n]);return t},isEmpty:function(e){if(!e)return!0;if(e&&e.length>0)return!1;if(e&&0===e.length)return!0;for(var t in e)if(e.hasOwnProperty(t))return!1;return!0},objectCreate:function(){function e(){}return Object.create?Object.create:function(t){if(1!=arguments.length)throw new Error("Object.create implementation only accepts one parameter.");return e.prototype=t,new e}}(),Promise:function(){var e=0,t=1,n=2,o=function(t){return this instanceof o?(this.id="Thenable/1.0.6",this.state=e,this.fulfillValue=void 0,this.rejectReason=void 0,this.onFulfilled=[],this.onRejected=[],this.proxy={then:this.then.bind(this)},void("function"==typeof t&&t.call(this,this.fulfill.bind(this),this.reject.bind(this)))):new o(t)};o.prototype={fulfill:function(e){return i(this,t,"fulfillValue",e)},reject:function(e){return i(this,n,"rejectReason",e)},then:function(e,t){var n=this,i=new o;return n.onFulfilled.push(s(e,i,"fulfill")),n.onRejected.push(s(t,i,"reject")),a(n),i.proxy}};var i=function(t,n,o,i){return t.state===e&&(t.state=n,t[o]=i,a(t)),t},a=function(e){e.state===t?r(e,"onFulfilled",e.fulfillValue):e.state===n&&r(e,"onRejected",e.rejectReason)},r=function(e,t,n){if(0!==e[t].length){var o=e[t];e[t]=[];var i=function(){for(var e=0;e<o.length;e++)o[e](n)};"object"==typeof process&&"function"==typeof process.nextTick?process.nextTick(i):"function"==typeof setImmediate?setImmediate(i):setTimeout(i,0)}},s=function(e,t,n){return function(o){if("function"!=typeof e)t[n].call(t,o);else{var i;try{i=e(o)}catch(a){return void t.reject(a)}l(t,i)}}},l=function(e,t){if(e===t||e.proxy===t)return void e.reject(new TypeError("cannot resolve promise with itself"));var n;if("object"==typeof t&&null!==t||"function"==typeof t)try{n=t.then}catch(o){return void e.reject(o)}if("function"!=typeof n)e.fulfill(t);else{var i=!1;try{n.call(t,function(n){i||(i=!0,n===t?e.reject(new TypeError("circular thenable chain")):l(e,n))},function(t){i||(i=!0,e.reject(t))})}catch(o){i||e.reject(o)}}};return o}(),Event:function(){var e=/[\s\,]+/;return this.parent={events:this.events,findEvents:this.findEvents,parent:this.parent,utils:this.utils},this.events={},this.on=function(t,n){if(n&&"function"==typeof n)for(var o=t.split(e),i=0;i<o.length;i++)this.events[o[i]]=[n].concat(this.events[o[i]]||[]);return this},this.off=function(e,t){return this.findEvents(e,function(e,n){t&&this.events[e][n]!==t||(this.events[e][n]=null)}),this},this.emit=function(e){var t=Array.prototype.slice.call(arguments,1);t.push(e);for(var n=function(n,o){t[t.length-1]="*"===n?e:n,this.events[n][o].apply(this,t)},o=this;o&&o.findEvents;)o.findEvents(e+",*",n),o=o.parent;return this},this.emitAfter=function(){var e=this,t=arguments;return setTimeout(function(){e.emit.apply(e,t)},0),this},this.findEvents=function(t,n){var o=t.split(e);for(var i in this.events)if(this.events.hasOwnProperty(i)&&hello.utils.indexOf(o,i)>-1)for(var a=0;a<this.events[i].length;a++)this.events[i][a]&&n.call(this,i,a)},this},globalEvent:function(e,t){return t=t||"_hellojs_"+parseInt(1e12*Math.random(),10).toString(36),window[t]=function(){try{bool=e.apply(this,arguments)}catch(n){console.error(n)}if(bool)try{delete window[t]}catch(n){}},t},popup:function(e,t,n,o){var i=document.documentElement,a=void 0!==window.screenLeft?window.screenLeft:screen.left,r=void 0!==window.screenTop?window.screenTop:screen.top,s=window.innerWidth||i.clientWidth||screen.width,l=window.innerHeight||i.clientHeight||screen.height,u=(s-n)/2+a,c=(l-o)/2+r,d=function(e){var i=window.open(e,"_blank","resizeable=true,height="+o+",width="+n+",left="+u+",top="+c);if(i&&i.addEventListener){var a=hello.utils.url(t),r=a.origin||a.protocol+"//"+a.hostname;i.addEventListener("loadstart",function(e){var t=e.url;if(0===t.indexOf(r)){var n=hello.utils.url(t),o={location:{assign:function(e){i.addEventListener("exit",function(){setTimeout(function(){d(e)},1e3)})},search:n.search,hash:n.hash,href:n.href},close:function(){i.close&&i.close()}};hello.utils.responseHandler(o,window),o.close()}})}return i&&i.focus&&i.focus(),i};return-1!==navigator.userAgent.indexOf("Safari")&&-1===navigator.userAgent.indexOf("Chrome")&&(e=t+"#oauth_redirect="+encodeURIComponent(encodeURIComponent(e))),d(e)},responseHandler:function(e,t){function n(e,t,n){if(a.store(e.network,e),!("display"in e&&"page"===e.display)){if(n){var i=e.callback;try{delete e.callback}catch(r){}if(a.store(e.network,e),i in n){var s=JSON.stringify(e);try{n[i](s)}catch(r){}}}o()}}function o(){try{e.close()}catch(t){}e.addEventListener&&e.addEventListener("load",function(){e.close()})}var i,a=this,r=e.location,s=function(t){r.assign?r.assign(t):e.location=t};if(i=a.param(r.search),i&&(i.code&&i.state||i.oauth_token&&i.proxy_url)){var l=JSON.parse(i.state);i.redirect_uri=l.redirect_uri||r.href.replace(/[\?\#].*$/,"");var u=(l.oauth_proxy||i.proxy_url)+"?"+a.param(i);return void s(u)}if(i=a.merge(a.param(r.search||""),a.param(r.hash||"")),i&&"state"in i){try{var c=JSON.parse(i.state);a.extend(i,c)}catch(d){console.error("Could not decode state parameter")}if("access_token"in i&&i.access_token&&i.network)i.expires_in&&0!==parseInt(i.expires_in,10)||(i.expires_in=0),i.expires_in=parseInt(i.expires_in,10),i.expires=(new Date).getTime()/1e3+(i.expires_in||31536e3),n(i,e,t);else if("error"in i&&i.error&&i.network)i.error={code:i.error,message:i.error_message||i.error_description},n(i,e,t);else if(i.callback&&i.callback in t){var f="result"in i&&i.result?JSON.parse(i.result):!1;t[i.callback](f),o()}i.page_uri&&(e.location=i.page_uri)}else if("oauth_redirect"in i)return void s(decodeURIComponent(i.oauth_redirect))}}),hello.utils.Event.call(hello),hello.utils.responseHandler(window,window.opener||window.parent),function(e){var t={},n={};e.on("auth.login, auth.logout",function(n){n&&"object"==typeof n&&n.network&&(t[n.network]=e.utils.store(n.network)||{})}),function o(){var i=(new Date).getTime()/1e3,a=function(t){e.emit("auth."+t,{network:r,authResponse:s})};for(var r in e.services)if(e.services.hasOwnProperty(r)){if(!e.services[r].id)continue;var s=e.utils.store(r)||{},l=e.services[r],u=t[r]||{};if(s&&"callback"in s){var c=s.callback;try{delete s.callback}catch(d){}e.utils.store(r,s);try{window[c](s)}catch(d){}}if(s&&"expires"in s&&s.expires<i){var f=l.refresh||s.refresh_token;!f||r in n&&!(n[r]<i)?f||r in n||(a("expired"),n[r]=!0):(e.emit("notice",r+" has expired trying to resignin"),e.login(r,{display:"none",force:!1}),n[r]=i+600);continue}if(u.access_token===s.access_token&&u.expires===s.expires)continue;!s.access_token&&u.access_token?a("logout"):s.access_token&&!u.access_token?a("login"):s.expires!==u.expires&&a("update"),t[r]=s,r in n&&delete n[r]}setTimeout(o,1e3)}()}(hello),hello.api=function(){function e(e){e=e.replace(/\@\{([a-z\_\-]+)(\|.+?)?\}/gi,function(e,n,o){var r=o?o.replace(/^\|/,""):"";return n in a.query?(r=a.query[n],delete a.query[n]):o||i.reject(t("missing_attribute","The attribute "+n+" is missing from the request")),r}),e.match(/^https?:\/\//)||(e=u.base+e),a.url=e,o.request(a,function(e,t){if(e===!0?e={success:!0}:e||(e={}),"delete"===a.method&&(e=!e||o.isEmpty(e)?{success:!0}:e),u.wrap&&(a.path in u.wrap||"default"in u.wrap)){var n=a.path in u.wrap?a.path:"default",r=((new Date).getTime(),u.wrap[n](e,t,a));r&&(e=r)}e&&"paging"in e&&e.paging.next&&("?"===e.paging.next[0]?e.paging.next=a.path+e.paging.next:e.paging.next+="#"+a.path),!e||"error"in e?i.reject(e):i.fulfill(e)})}function t(e,t){return{error:{code:e,message:t}}}var n=this,o=n.utils,i=o.Promise(),a=o.args({path:"s!",query:"o",method:"s",data:"o",timeout:"i",callback:"f"},arguments);a.method=(a.method||"get").toLowerCase(),a.headers=a.headers||{},a.query=a.query||{},("get"===a.method||"delete"===a.method)&&(o.extend(a.query,a.data),a.data={});var r=a.data=a.data||{};if(i.then(a.callback,a.callback),!a.path)return i.reject(t("invalid_path","Missing the path parameter from the request"));a.path=a.path.replace(/^\/+/,"");var s=(a.path.split(/[\/\:]/,2)||[])[0].toLowerCase();if(s in n.services){a.network=s;var l=new RegExp("^"+s+":?/?");a.path=a.path.replace(l,"")}a.network=n.settings.default_service=a.network||n.settings.default_service;var u=n.services[a.network];if(!u)return i.reject(t("invalid_network","Could not match the service requested: "+a.network));if(a.method in u&&a.path in u[a.method]&&u[a.method][a.path]===!1)return i.reject(t("invalid_path","The provided path is not available on the selected network"));a.oauth_proxy||(a.oauth_proxy=n.settings.oauth_proxy),"proxy"in a||(a.proxy=a.oauth_proxy&&u.oauth&&1===parseInt(u.oauth.version,10)),"timeout"in a||(a.timeout=n.settings.timeout);var c=n.getAuthResponse(a.network);c&&c.access_token&&(a.query.access_token=c.access_token);var d,f=a.path;a.options=o.clone(a.query),a.data=o.clone(r);var p=u[{"delete":"del"}[a.method]||a.method]||{};if("get"===a.method){var m=f.split(/[\?#]/)[1];m&&(o.extend(a.query,o.param(m)),f=f.replace(/\?.*?(#|$)/,"$1"))}return(d=f.match(/#(.+)/,""))?(f=f.split("#")[0],a.path=d[1]):f in p?(a.path=f,f=p[f]):"default"in p&&(f=p["default"]),a.redirect_uri=n.settings.redirect_uri,a.oauth=u.oauth,a.xhr=u.xhr,a.jsonp=u.jsonp,a.form=u.form,"function"==typeof f?f(a,e):e(f),i.proxy},hello.utils.extend(hello.utils,{request:function(e,t){function n(e,t){var n;e.oauth&&1===parseInt(e.oauth.version,10)&&(n=e.query.access_token,delete e.query.access_token,e.proxy=!0),!e.data||"get"!==e.method&&"delete"!==e.method||(o.extend(e.query,e.data),e.data=null);var i=o.qs(e.url,e.query);e.proxy&&(i=o.qs(e.oauth_proxy,{path:i,access_token:n||"",then:e.proxy_response_type||("get"===e.method.toLowerCase()?"redirect":"proxy"),method:e.method.toLowerCase(),suppress_response_codes:!0})),t(i)}var o=this;if(o.isEmpty(e.data)||"FileList"in window||!o.hasBinary(e.data)||(e.xhr=!1,e.jsonp=!1),"withCredentials"in new XMLHttpRequest&&(!("xhr"in e)||e.xhr&&("function"!=typeof e.xhr||e.xhr(e,e.query))))return void n(e,function(n){var i=o.xhr(e.method,n,e.headers,e.data,t);i.onprogress=e.onprogress||null,i.upload&&e.onuploadprogress&&(i.upload.onprogress=e.onuploadprogress)});var i=e.query;if(e.query=o.clone(e.query),e.callbackID=o.globalEvent(),e.jsonp!==!1){if(e.query.callback=e.callbackID,"function"==typeof e.jsonp&&e.jsonp(e,e.query),"get"===e.method)return void n(e,function(n){o.jsonp(n,t,e.callbackID,e.timeout)});e.query=i}if(e.form!==!1){e.query.redirect_uri=e.redirect_uri,e.query.state=JSON.stringify({callback:e.callbackID});var a;if("function"==typeof e.form&&(a=e.form(e,e.query)),"post"===e.method&&a!==!1)return void n(e,function(n){o.post(n,e.data,a,t,e.callbackID,e.timeout)})}t({error:{code:"invalid_request",message:"There was no mechanism for handling this request"}})},isArray:function(e){return"[object Array]"===Object.prototype.toString.call(e)},domInstance:function(e,t){var n="HTML"+(e||"").replace(/^[a-z]/,function(e){return e.toUpperCase()})+"Element";return t?window[n]?t instanceof window[n]:window.Element?t instanceof window.Element&&(!e||t.tagName&&t.tagName.toLowerCase()===e):!(t instanceof Object||t instanceof Array||t instanceof String||t instanceof Number)&&t.tagName&&t.tagName.toLowerCase()===e:!1},clone:function(e){if(null===e||"object"!=typeof e||e instanceof Date||"nodeName"in e||this.isBinary(e))return e;var t;if(this.isArray(e)){t=[];for(var n=0;n<e.length;n++)t.push(this.clone(e[n]));return t}t={};for(var o in e)t[o]=this.clone(e[o]);return t},xhr:function(e,t,n,o,i){function a(e){for(var t,n={},o=/([a-z\-]+):\s?(.*);?/gi;t=o.exec(e);)n[t[1]]=t[2];return n}var r=new XMLHttpRequest,s=!1;"blob"===e&&(s=e,e="GET"),e=e.toUpperCase(),r.onload=function(t){var n=r.response;try{n=JSON.parse(r.responseText)}catch(o){401===r.status&&(n={error:{code:"access_denied",message:r.statusText}})}var s=a(r.getAllResponseHeaders());s.statusCode=r.status,i(n||("GET"===e?{error:{code:"empty_response",message:"Could not get resource"}}:{}),s)},r.onerror=function(e){var t=r.responseText;try{t=JSON.parse(r.responseText)}catch(n){}i(t||{error:{code:"access_denied",message:"Could not get resource"}})};var l;if("GET"===e||"DELETE"===e)o=null;else if(!(!o||"string"==typeof o||o instanceof FormData||o instanceof File||o instanceof Blob)){var u=new FormData;for(l in o)o.hasOwnProperty(l)&&(o[l]instanceof HTMLInputElement?"files"in o[l]&&o[l].files.length>0&&u.append(l,o[l].files[0]):o[l]instanceof Blob?u.append(l,o[l],o.name):u.append(l,o[l]));o=u}if(r.open(e,t,!0),s&&("responseType"in r?r.responseType=s:r.overrideMimeType("text/plain; charset=x-user-defined")),n)for(l in n)r.setRequestHeader(l,n[l]);return r.send(o),r},jsonp:function(e,t,n,o){var i,a,r=this,s=0,l=document.getElementsByTagName("head")[0],u={error:{message:"server_error",code:"server_error"}},c=function(){s++||window.setTimeout(function(){t(u),l.removeChild(a)},0)};n=r.globalEvent(function(e){return u=e,!0},n),e=e.replace(new RegExp("=\\?(&|$)"),"="+n+"$1"),a=r.append("script",{id:n,name:n,src:e,async:!0,onload:c,onerror:c,onreadystatechange:function(){/loaded|complete/i.test(this.readyState)&&c()}}),window.navigator.userAgent.toLowerCase().indexOf("opera")>-1&&(i=r.append("script",{text:"document.getElementById('"+cb_name+"').onerror();"}),a.async=!1),o&&window.setTimeout(function(){u={error:{message:"timeout",code:"timeout"}},c()},o),l.appendChild(a),i&&l.appendChild(i)},post:function(e,t,n,o,i,a){var r,s=this,l=document,u=null,c=[],d=0,f=null,p=0,m=function(e){p++||o(e)};s.globalEvent(m,i);var h;try{h=l.createElement('<iframe name="'+i+'">')}catch(g){h=l.createElement("iframe")}if(h.name=i,h.id=i,h.style.display="none",n&&n.callbackonload&&(h.onload=function(){m({response:"posted",message:"Content was posted"})}),a&&setTimeout(function(){m({error:{code:"timeout",message:"The post operation timed out"}})},a),l.body.appendChild(h),s.domInstance("form",t)){for(u=t.form,d=0;d<u.elements.length;d++)u.elements[d]!==t&&u.elements[d].setAttribute("disabled",!0);t=u}if(s.domInstance("form",t))for(u=t,d=0;d<u.elements.length;d++)u.elements[d].disabled||"file"!==u.elements[d].type||(u.encoding=u.enctype="multipart/form-data",u.elements[d].setAttribute("name","file"));else{for(f in t)t.hasOwnProperty(f)&&s.domInstance("input",t[f])&&"file"===t[f].type&&(u=t[f].form,u.encoding=u.enctype="multipart/form-data");u||(u=l.createElement("form"),l.body.appendChild(u),r=u);var v;for(f in t)if(t.hasOwnProperty(f)){var y=s.domInstance("input",t[f])||s.domInstance("textArea",t[f])||s.domInstance("select",t[f]);if(y&&t[f].form===u)y&&t[f].name!==f&&(t[f].setAttribute("name",f),t[f].name=f);else{var w=u.elements[f];if(v)for(w instanceof NodeList||(w=[w]),d=0;d<w.length;d++)w[d].parentNode.removeChild(w[d]);v=l.createElement("input"),v.setAttribute("type","hidden"),v.setAttribute("name",f),v.value=y?t[f].value:s.domInstance(null,t[f])?t[f].innerHTML||t[f].innerText:t[f],u.appendChild(v)}}for(d=0;d<u.elements.length;d++)v=u.elements[d],v.name in t||v.getAttribute("disabled")===!0||(v.setAttribute("disabled",!0),c.push(v))}u.setAttribute("method","POST"),u.setAttribute("target",i),u.target=i,u.setAttribute("action",e),setTimeout(function(){u.submit(),setTimeout(function(){try{r&&r.parentNode.removeChild(r)}catch(e){try{console.error("HelloJS: could not remove iframe")}catch(t){}}for(var n=0;n<c.length;n++)c[n]&&(c[n].setAttribute("disabled",!1),c[n].disabled=!1)},0)},100)},hasBinary:function(e){for(var t in e)if(e.hasOwnProperty(t)&&this.isBinary(e[t]))return!0;return!1},isBinary:function(e){return e instanceof Object&&(this.domInstance("input",e)&&"file"===e.type||"FileList"in window&&e instanceof window.FileList||"File"in window&&e instanceof window.File||"Blob"in window&&e instanceof window.Blob)},toBlob:function(e){var t=/^data\:([^;,]+(\;charset=[^;,]+)?)(\;base64)?,/i,n=e.match(t);if(!n)return e;for(var o=atob(e.replace(t,"")),i=[],a=0;a<o.length;a++)i.push(o.charCodeAt(a));return new Blob([new Uint8Array(i)],{type:n[1]})}}),function(e){var t=e.api,n=e.utils;n.extend(n,{dataToJSON:function(e){var t=this,n=window,o=e.data;if(t.domInstance("form",o)?o=t.nodeListToJSON(o.elements):"NodeList"in n&&o instanceof NodeList?o=t.nodeListToJSON(o):t.domInstance("input",o)&&(o=t.nodeListToJSON([o])),("File"in n&&o instanceof n.File||"Blob"in n&&o instanceof n.Blob||"FileList"in n&&o instanceof n.FileList)&&(o={file:o}),!("FormData"in n&&o instanceof n.FormData))for(var i in o)if(o.hasOwnProperty(i))if("FileList"in n&&o[i]instanceof n.FileList)1===o[i].length&&(o[i]=o[i][0]);else{if(t.domInstance("input",o[i])&&"file"===o[i].type)continue;t.domInstance("input",o[i])||t.domInstance("select",o[i])||t.domInstance("textArea",o[i])?o[i]=o[i].value:t.domInstance(null,o[i])&&(o[i]=o[i].innerHTML||o[i].innerText)}return e.data=o,o},nodeListToJSON:function(e){for(var t={},n=0;n<e.length;n++){var o=e[n];!o.disabled&&o.name&&(t[o.name]="file"===o.type?o:o.value||o.innerHTML)}return t}}),e.api=function(){var e=n.args({path:"s!",method:"s",data:"o",timeout:"i",callback:"f"},arguments);return e.data&&n.dataToJSON(e),t.call(this,e)}}(hello),Function.prototype.bind||(Function.prototype.bind=function(e){function t(){}if("function"!=typeof this)throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");var n=[].slice,o=n.call(arguments,1),i=this,a=function(){return i.apply(this instanceof t?this:e||window,o.concat(n.call(arguments)))};return t.prototype=this.prototype,a.prototype=new t,a}),hello.subscribe=hello.on,hello.trigger=hello.emit,hello.unsubscribe=hello.off,function(e){function t(e){e&&"error"in e&&(e.error={code:"server_error",message:e.error.message||e.error})}function n(t,n,o){if(!("object"!=typeof t||"undefined"!=typeof Blob&&t instanceof Blob||"undefined"!=typeof ArrayBuffer&&t instanceof ArrayBuffer||"error"in t)){var i=t.root+t.path.replace(/\&/g,"%26");t.thumb_exists&&(t.thumbnail=e.settings.oauth_proxy+"?path="+encodeURIComponent("https://api-content.dropbox.com/1/thumbnails/"+i+"?format=jpeg&size=m")+"&access_token="+o.query.access_token),t.type=t.is_dir?"folder":t.mime_type,t.name=t.path.replace(/.*\//g,""),t.is_dir?t.files="metadata/"+i:(t.downloadLink=e.settings.oauth_proxy+"?path="+encodeURIComponent("https://api-content.dropbox.com/1/files/"+i)+"&access_token="+o.query.access_token,t.file="https://api-content.dropbox.com/1/files/"+i),t.id||(t.id=t.path.replace(/^\//,""))}}function o(e){return function(t,n){delete t.query.limit,n(e)}}e.init({dropbox:{login:function(e){e.options.window_width=1e3,e.options.window_height=1e3},oauth:{version:"1.0",auth:"https://www.dropbox.com/1/oauth/authorize",request:"https://api.dropbox.com/1/oauth/request_token",token:"https://api.dropbox.com/1/oauth/access_token"},base:"https://api.dropbox.com/1/",root:"sandbox",get:{me:"account/info","me/files":o("metadata/@{root|sandbox}/@{parent}"),"me/folder":o("metadata/@{root|sandbox}/@{id}"),"me/folders":o("metadata/@{root|sandbox}/"),"default":function(e,t){e.path.match("https://api-content.dropbox.com/1/files/")&&(e.method="blob"),t(e.path)}},post:{"me/files":function(t,n){var o=t.data.parent,i=t.data.name;t.data={file:t.data.file},"string"==typeof t.data.file&&(t.data.file=e.utils.toBlob(t.data.file)),n("https://api-content.dropbox.com/1/files_put/@{root|sandbox}/"+o+"/"+i)},"me/folders":function(t,n){var o=t.data.name;t.data={},n("fileops/create_folder?root=@{root|sandbox}&"+e.utils.param({path:o}))}},del:{"me/files":"fileops/delete?root=@{root|sandbox}&path=@{id}","me/folder":"fileops/delete?root=@{root|sandbox}&path=@{id}"},wrap:{me:function(e){return t(e),e.uid?(e.name=e.display_name,e.first_name=e.name.split(" ")[0],e.last_name=e.name.split(" ")[1],e.id=e.uid,delete e.uid,delete e.display_name,e):e},"default":function(e,o,i){if(t(e),e.is_dir&&e.contents){e.data=e.contents,delete e.contents;for(var a=0;a<e.data.length;a++)e.data[a].root=e.root,n(e.data[a],o,i)}return n(e,o,i),e.is_deleted&&(e.success=!0),e}},xhr:function(e){if(e.data&&e.data.file){var t=e.data.file;t&&(e.data=t.files?t.files[0]:t)}return"delete"===e.method&&(e.method="post"),!0},form:function(e,t){delete t.state,delete t.redirect_uri}}})}(hello),function(e){function t(e){return e.id&&(e.thumbnail=e.picture="https://graph.facebook.com/"+e.id+"/picture"),e}function n(e){if("data"in e)for(var n=0;n<e.data.length;n++)t(e.data[n]);return e}function o(e,t,n){if("boolean"==typeof e&&(e={success:e}),e&&"data"in e)for(var o=n.query.access_token,a=0;a<e.data.length;a++){var r=e.data[a];r.picture&&(r.thumbnail=r.picture),r.cover_photo&&(r.thumbnail=i+r.cover_photo+"/picture?access_token="+o),"album"===r.type&&(r.files=r.photos=i+r.id+"/photos"),r.can_upload&&(r.upload_location=i+r.id+"/photos")}return e}var i="https://graph.facebook.com/";e.init({facebook:{name:"Facebook",login:function(e){e.options.auth_type&&(e.qs.auth_type=e.options.auth_type),e.options.window_width=580,e.options.window_height=400},oauth:{version:2,auth:"https://www.facebook.com/dialog/oauth/",grant:"https://graph.facebook.com/oauth/access_token"},refresh:!0,logout:function(t){var n=e.utils.globalEvent(t),o=encodeURIComponent(e.settings.redirect_uri+"?"+e.utils.param({callback:n,result:JSON.stringify({force:!0}),state:"{}"})),i=(e.utils.store("facebook")||{}).access_token;return e.utils.iframe("https://www.facebook.com/logout.php?next="+o+"&access_token="+i),i?void 0:!1},scope:{basic:"public_profile",email:"email",birthday:"user_birthday",events:"user_events",photos:"user_photos,user_videos",videos:"user_photos,user_videos",friends:"user_friends",files:"user_photos,user_videos",publish_files:"user_photos,user_videos,publish_actions",publish:"publish_actions",offline_access:"offline_access"},base:"https://graph.facebook.com/",get:{me:"me","me/friends":"me/friends","me/following":"me/friends","me/followers":"me/friends","me/share":"me/feed","me/like":"me/likes","me/files":"me/albums","me/albums":"me/albums","me/album":"@{id}/photos","me/photos":"me/photos","me/photo":"@{id}","friend/albums":"@{id}/albums","friend/photos":"@{id}/photos"},post:{"me/share":"me/feed","me/albums":"me/albums","me/album":"@{id}/photos"},del:{"me/photo":"@{id}"},wrap:{me:t,"me/friends":n,"me/following":n,"me/followers":n,"me/albums":o,"me/files":o,"default":o},xhr:function(t,n){return("get"===t.method||"post"===t.method)&&(n.suppress_response_codes=!0),"post"===t.method&&t.data&&"string"==typeof t.data.file&&(t.data.file=e.utils.toBlob(t.data.file)),!0},jsonp:function(t,n){var o=t.method;"get"===o||e.utils.hasBinary(t.data)?"delete"===t.method&&(n.method="delete",t.method="post"):(t.data.method=o,t.method="get")},form:function(e){return{callbackonload:!0}}}})}(hello),function(e){function t(t,n,o){var i=(o?"":"flickr:")+"?method="+t+"&api_key="+e.init().flickr.id+"&format=json";for(var a in n)n.hasOwnProperty(a)&&(i+="&"+a+"="+n[a]);return i}function n(t){var n=e.getAuthResponse("flickr");t(n&&n.user_nsid?n.user_nsid:null)}function o(e,o){return o||(o={}),function(i,a){n(function(n){o.user_id=n,a(t(e,o,!0))})}}function i(e,t){var n="https://www.flickr.com/images/buddyicon.gif";return e.nsid&&e.iconserver&&e.iconfarm&&(n="https://farm"+e.iconfarm+".staticflickr.com/"+e.iconserver+"/buddyicons/"+e.nsid+(t?"_"+t:"")+".jpg"),n}function a(e,t,n,o,i){return i=i?"_"+i:"","https://farm"+t+".staticflickr.com/"+n+"/"+e+"_"+o+i+".jpg"}function r(e){e&&e.stat&&"ok"!=e.stat.toLowerCase()&&(e.error={code:"invalid_request",message:e.message})}function s(e){if(e.photoset||e.photos){var t="photoset"in e?"photoset":"photos";e=l(e,t),c(e),e.data=e.photo,delete e.photo;for(var n=0;n<e.data.length;n++){var o=e.data[n];o.name=o.title,o.picture=a(o.id,o.farm,o.server,o.secret,""),o.source=a(o.id,o.farm,o.server,o.secret,"b"),o.thumbnail=a(o.id,o.farm,o.server,o.secret,"m")}}return e}function l(e,t){return t in e?e=e[t]:"error"in e||(e.error={
code:"invalid_request",message:e.message||"Failed to get data from Flickr"}),e}function u(e){if(r(e),e.contacts){e=l(e,"contacts"),c(e),e.data=e.contact,delete e.contact;for(var t=0;t<e.data.length;t++){var n=e.data[t];n.id=n.nsid,n.name=n.realname||n.username,n.thumbnail=i(n,"m")}}return e}function c(e){e.page&&e.pages&&e.page!==e.pages&&(e.paging={next:"?page="+ ++e.page})}e.init({flickr:{name:"Flickr",oauth:{version:"1.0a",auth:"https://www.flickr.com/services/oauth/authorize?perms=read",request:"https://www.flickr.com/services/oauth/request_token",token:"https://www.flickr.com/services/oauth/access_token"},base:"https://api.flickr.com/services/rest",get:{me:o("flickr.people.getInfo"),"me/friends":o("flickr.contacts.getList",{per_page:"@{limit|50}"}),"me/following":o("flickr.contacts.getList",{per_page:"@{limit|50}"}),"me/followers":o("flickr.contacts.getList",{per_page:"@{limit|50}"}),"me/albums":o("flickr.photosets.getList",{per_page:"@{limit|50}"}),"me/photos":o("flickr.people.getPhotos",{per_page:"@{limit|50}"})},wrap:{me:function(e){if(r(e),e=l(e,"person"),e.id){if(e.realname){e.name=e.realname._content;var t=e.name.split(" ");e.first_name=t[0],e.last_name=t[1]}e.thumbnail=i(e,"l"),e.picture=i(e,"l")}return e},"me/friends":u,"me/followers":u,"me/following":u,"me/albums":function(e){if(r(e),e=l(e,"photosets"),c(e),e.photoset){e.data=e.photoset,delete e.photoset;for(var n=0;n<e.data.length;n++){var o=e.data[n];o.name=o.title._content,o.photos="https://api.flickr.com/services/rest"+t("flickr.photosets.getPhotos",{photoset_id:o.id},!0)}}return e},"me/photos":function(e){return r(e),s(e)},"default":function(e){return r(e),s(e)}},xhr:!1,jsonp:function(e,t){"get"==e.method&&(delete t.callback,t.jsoncallback=e.callbackID)}}})}(hello),function(e){function t(e){!e.meta||400!==e.meta.code&&401!==e.meta.code||(e.error={code:"access_denied",message:e.meta.errorDetail})}function n(e){e&&e.id&&(e.thumbnail=e.photo.prefix+"100x100"+e.photo.suffix,e.name=e.firstName+" "+e.lastName,e.first_name=e.firstName,e.last_name=e.lastName,e.contact&&e.contact.email&&(e.email=e.contact.email))}function o(e,t){var n=t.access_token;return delete t.access_token,t.oauth_token=n,t.v=20121125,!0}e.init({foursquare:{name:"FourSquare",oauth:{version:2,auth:"https://foursquare.com/oauth2/authenticate",grant:"https://foursquare.com/oauth2/access_token"},refresh:!0,base:"https://api.foursquare.com/v2/",get:{me:"users/self","me/friends":"users/self/friends","me/followers":"users/self/friends","me/following":"users/self/friends"},wrap:{me:function(e){return t(e),e&&e.response&&(e=e.response.user,n(e)),e},"default":function(e){if(t(e),e&&"response"in e&&"friends"in e.response&&"items"in e.response.friends){e.data=e.response.friends.items,delete e.response;for(var o=0;o<e.data.length;o++)n(e.data[o])}return e}},xhr:o,jsonp:o}})}(hello),function(e){function t(e,t){var n=t?t.statusCode:e&&"meta"in e&&"status"in e.meta&&e.meta.status;(401===n||403===n)&&(e.error={code:"access_denied",message:e.message||(e.data?e.data.message:"Could not get response")},delete e.message)}function n(e){e.id&&(e.thumbnail=e.picture=e.avatar_url,e.name=e.login)}function o(e,t,n){if(e.data&&e.data.length&&t&&t.Link){var o=t.Link.match(/<(.*?)>;\s*rel=\"next\"/);o&&(e.paging={next:o[1]})}}e.init({github:{name:"GitHub",oauth:{version:2,auth:"https://github.com/login/oauth/authorize",grant:"https://github.com/login/oauth/access_token",response_type:"code"},scope:{basic:"",email:"user:email"},base:"https://api.github.com/",get:{me:"user","me/friends":"user/following?per_page=@{limit|100}","me/following":"user/following?per_page=@{limit|100}","me/followers":"user/followers?per_page=@{limit|100}","me/like":"user/starred?per_page=@{limit|100}"},wrap:{me:function(e,o){return t(e,o),n(e),e},"default":function(e,i,a){if(t(e,i),"[object Array]"===Object.prototype.toString.call(e)){e={data:e},o(e,i,a);for(var r=0;r<e.data.length;r++)n(e.data[r])}return e}},xhr:function(e){return"get"!==e.method&&e.data&&(e.headers=e.headers||{},e.headers["Content-Type"]="application/json","object"==typeof e.data&&(e.data=JSON.stringify(e.data))),!0}}})}(hello),function(e){"use strict";function t(e){return parseInt(e,10)}function n(e){e.error||(e.name||(e.name=e.title||e.message),e.picture||(e.picture=e.thumbnailLink),e.thumbnail||(e.thumbnail=e.thumbnailLink),"application/vnd.google-apps.folder"===e.mimeType&&(e.type="folder",e.files="https://www.googleapis.com/drive/v2/files?q=%22"+e.id+"%22+in+parents"))}function o(e){r(e);var t=function(e){var t,n=e.media$group.media$content.length?e.media$group.media$content[0]:{},o=0,i={id:e.id.$t,name:e.title.$t,description:e.summary.$t,updated_time:e.updated.$t,created_time:e.published.$t,picture:n?n.url:null,thumbnail:n?n.url:null,width:n.width,height:n.height};if("link"in e)for(o=0;o<e.link.length;o++){var a=e.link[o];if(a.rel.match(/\#feed$/)){i.upload_location=i.files=i.photos=a.href;break}}if("category"in e&&e.category.length)for(t=e.category,o=0;o<t.length;o++)t[o].scheme&&t[o].scheme.match(/\#kind$/)&&(i.type=t[o].term.replace(/^.*?\#/,""));if("media$thumbnail"in e.media$group&&e.media$group.media$thumbnail.length){for(t=e.media$group.media$thumbnail,i.thumbnail=e.media$group.media$thumbnail[0].url,i.images=[],o=0;o<t.length;o++)i.images.push({source:t[o].url,width:t[o].width,height:t[o].height});t=e.media$group.media$content.length?e.media$group.media$content[0]:null,t&&i.images.push({source:t.url,width:t.width,height:t.height})}return i},o=[];if("feed"in e&&"entry"in e.feed){for(i=0;i<e.feed.entry.length;i++)o.push(t(e.feed.entry[i]));e.data=o,delete e.feed}else{if("entry"in e)return t(e.entry);if("items"in e){for(var i=0;i<e.items.length;i++)n(e.items[i]);e.data=e.items,delete e.items}else n(e)}return e}function i(e){e.name=e.displayName||e.name,e.picture=e.picture||(e.image?e.image.url:null),e.thumbnail=e.picture}function a(e,t,n){r(e);if("feed"in e&&"entry"in e.feed){for(var o=n.query.access_token,i=0;i<e.feed.entry.length;i++){var a=e.feed.entry[i];if(a.id=a.id.$t,a.name=a.title.$t,delete a.title,a.gd$email&&(a.email=a.gd$email&&a.gd$email.length>0?a.gd$email[0].address:null,a.emails=a.gd$email,delete a.gd$email),a.updated&&(a.updated=a.updated.$t),a.link){var s=a.link.length>0?a.link[0].href+"?access_token="+o:null;s&&(a.picture=s,a.thumbnail=s),delete a.link}a.category&&delete a.category}e.data=e.feed.entry,delete e.feed}return e}function r(e){if("feed"in e&&e.feed.openSearch$itemsPerPage){var n=t(e.feed.openSearch$itemsPerPage.$t),o=t(e.feed.openSearch$startIndex.$t),i=t(e.feed.openSearch$totalResults.$t);i>o+n&&(e.paging={next:"?start="+(o+n)})}else"nextPageToken"in e&&(e.paging={next:"?pageToken="+e.nextPageToken})}function s(){function e(e){var n=new FileReader;n.onload=function(n){t(btoa(n.target.result),e.type+a+"Content-Transfer-Encoding: base64")},n.readAsBinaryString(e)}function t(e,t){n.push(a+"Content-Type: "+t+a+a+e),i--,s()}var n=[],o=(1e10*Math.random()).toString(32),i=0,a="\r\n",r=a+"--"+o,s=function(){},l=/^data\:([^;,]+(\;charset=[^;,]+)?)(\;base64)?,/i;this.append=function(n,o){"string"!=typeof n&&"length"in Object(n)||(n=[n]);for(var r=0;r<n.length;r++){i++;var s=n[r];if("undefined"!=typeof File&&s instanceof File||"undefined"!=typeof Blob&&s instanceof Blob)e(s);else if("string"==typeof s&&s.match(l)){var u=s.match(l);t(s.replace(l,""),u[1]+a+"Content-Transfer-Encoding: base64")}else t(s,o)}},this.onready=function(e){(s=function(){0===i&&(n.unshift(""),n.push("--"),e(n.join(r),o),n=[])})()}}function l(e,t){var n={};e.data&&"undefined"!=typeof HTMLInputElement&&e.data instanceof HTMLInputElement&&(e.data={file:e.data}),!e.data.name&&Object(Object(e.data.file).files).length&&"post"===e.method&&(e.data.name=e.data.file.files[0].name),"post"===e.method?e.data={title:e.data.name,parents:[{id:e.data.parent||"root"}],file:e.data.file}:(n=e.data,e.data={},n.parent&&(e.data.parents=[{id:e.data.parent||"root"}]),n.file&&(e.data.file=n.file),n.name&&(e.data.title=n.name));var o;if("file"in e.data&&(o=e.data.file,delete e.data.file,"object"==typeof o&&"files"in o&&(o=o.files),!o||!o.length))return void t({error:{code:"request_invalid",message:"There were no files attached with this request to upload"}});var i=new s;i.append(JSON.stringify(e.data),"application/json"),o&&i.append(o),i.onready(function(o,i){e.headers["content-type"]='multipart/related; boundary="'+i+'"',e.data=o,t("upload/drive/v2/files"+(n.id?"/"+n.id:"")+"?uploadType=multipart")})}function u(e){if("object"==typeof e.data)try{e.data=JSON.stringify(e.data),e.headers["content-type"]="application/json"}catch(t){}}var c="https://www.google.com/m8/feeds/contacts/default/full?v=3.0&alt=json&max-results=@{limit|1000}&start-index=@{start|1}";e.init({google:{name:"Google Plus",login:function(e){"none"===e.qs.display&&(e.qs.display=""),"code"===e.qs.response_type&&(e.qs.access_type="offline")},oauth:{version:2,auth:"https://accounts.google.com/o/oauth2/auth",grant:"https://accounts.google.com/o/oauth2/token"},scope:{basic:"https://www.googleapis.com/auth/plus.me profile",email:"email",birthday:"",events:"",photos:"https://picasaweb.google.com/data/",videos:"http://gdata.youtube.com",friends:"https://www.google.com/m8/feeds, https://www.googleapis.com/auth/plus.login",files:"https://www.googleapis.com/auth/drive.readonly",publish:"",publish_files:"https://www.googleapis.com/auth/drive",create_event:"",offline_access:""},scope_delim:" ",base:"https://www.googleapis.com/",get:{me:"plus/v1/people/me","me/friends":"plus/v1/people/me/people/visible?maxResults=@{limit|100}","me/following":c,"me/followers":c,"me/contacts":c,"me/share":"plus/v1/people/me/activities/public?maxResults=@{limit|100}","me/feed":"plus/v1/people/me/activities/public?maxResults=@{limit|100}","me/albums":"https://picasaweb.google.com/data/feed/api/user/default?alt=json&max-results=@{limit|100}&start-index=@{start|1}","me/album":function(e,t){var n=e.query.id;delete e.query.id,t(n.replace("/entry/","/feed/"))},"me/photos":"https://picasaweb.google.com/data/feed/api/user/default?alt=json&kind=photo&max-results=@{limit|100}&start-index=@{start|1}","me/files":"drive/v2/files?q=%22@{parent|root}%22+in+parents+and+trashed=false&maxResults=@{limit|100}","me/folders":"drive/v2/files?q=%22@{id|root}%22+in+parents+and+mimeType+=+%22application/vnd.google-apps.folder%22+and+trashed=false&maxResults=@{limit|100}","me/folder":"drive/v2/files?q=%22@{id|root}%22+in+parents+and+trashed=false&maxResults=@{limit|100}"},post:{"me/files":l,"me/folders":function(e,t){e.data={title:e.data.name,parents:[{id:e.data.parent||"root"}],mimeType:"application/vnd.google-apps.folder"},t("drive/v2/files")}},put:{"me/files":l},del:{"me/files":"drive/v2/files/@{id}","me/folder":"drive/v2/files/@{id}"},wrap:{me:function(e){return e.id&&(e.last_name=e.family_name||(e.name?e.name.familyName:null),e.first_name=e.given_name||(e.name?e.name.givenName:null),e.emails&&e.emails.length&&(e.email=e.emails[0].value),i(e)),e},"me/friends":function(e){if(e.items){r(e),e.data=e.items,delete e.items;for(var t=0;t<e.data.length;t++)i(e.data[t])}return e},"me/contacts":a,"me/followers":a,"me/following":a,"me/share":function(e){return r(e),e.data=e.items,delete e.items,e},"me/feed":function(e){return r(e),e.data=e.items,delete e.items,e},"me/albums":o,"me/photos":o,"default":o},xhr:function(e){return("post"===e.method||"put"===e.method)&&u(e),!0},form:!1}})}(hello),function(e){function t(e){e&&"meta"in e&&"error_type"in e.meta&&(e.error={code:e.meta.error_type,message:e.meta.error_message})}function n(e){if(i(e),e&&"data"in e)for(var t=0;t<e.data.length;t++)o(e.data[t]);return e}function o(e){e.id&&(e.thumbnail=e.profile_picture,e.name=e.full_name||e.username)}function i(e){"pagination"in e&&(e.paging={next:e.pagination.next_url},delete e.pagination)}e.init({instagram:{name:"Instagram",login:function(e){e.qs.display=""},oauth:{version:2,auth:"https://instagram.com/oauth/authorize/",grant:"https://api.instagram.com/oauth/access_token"},refresh:!0,scope:{basic:"basic",friends:"relationships",publish:"likes comments"},scope_delim:" ",base:"https://api.instagram.com/v1/",get:{me:"users/self","me/feed":"users/self/feed?count=@{limit|100}","me/photos":"users/self/media/recent?min_id=0&count=@{limit|100}","me/friends":"users/self/follows?count=@{limit|100}","me/following":"users/self/follows?count=@{limit|100}","me/followers":"users/self/followed-by?count=@{limit|100}","friend/photos":"users/@{id}/media/recent?min_id=0&count=@{limit|100}"},post:{"me/like":function(e,t){var n=e.data.id;e.data={},t("media/"+n+"/likes")}},del:{"me/like":"media/@{id}/likes"},wrap:{me:function(e){return t(e),"data"in e&&(e.id=e.data.id,e.thumbnail=e.data.profile_picture,e.name=e.data.full_name||e.data.username),e},"me/friends":n,"me/following":n,"me/followers":n,"me/photos":function(e){if(t(e),i(e),"data"in e)for(var n=0;n<e.data.length;n++){var o=e.data[n];"image"===o.type?(o.thumbnail=o.images.thumbnail.url,o.picture=o.images.standard_resolution.url,o.name=o.caption?o.caption.text:null):(e.data.splice(n,1),n--)}return e},"default":function(e){return i(e),e}},xhr:function(e,t){var n=e.method,o="get"!==n;return o&&("post"!==n&&"put"!==n||!e.query.access_token||(e.data.access_token=e.query.access_token,delete e.query.access_token),e.proxy=o),o},form:!1}})}(hello),function(e){function t(e){e&&"errorCode"in e&&(e.error={code:e.status,message:e.message})}function n(e){e.error||(e.first_name=e.firstName,e.last_name=e.lastName,e.name=e.formattedName||e.first_name+" "+e.last_name,e.thumbnail=e.pictureUrl,e.email=e.emailAddress)}function o(e){if(t(e),i(e),e.values){e.data=e.values;for(var o=0;o<e.data.length;o++)n(e.data[o]);delete e.values}return e}function i(e){"_count"in e&&"_start"in e&&e._count+e._start<e._total&&(e.paging={next:"?start="+(e._start+e._count)+"&count="+e._count})}function a(e,t){"{}"===JSON.stringify(e)&&200===t.statusCode&&(e.success=!0)}function r(e){e.access_token&&(e.oauth2_access_token=e.access_token,delete e.access_token)}function s(e,t){e.headers["x-li-format"]="json";var n=e.data.id;e.data=("delete"!==e.method).toString(),e.method="put",t("people/~/network/updates/key="+n+"/is-liked")}e.init({linkedin:{oauth:{version:2,response_type:"code",auth:"https://www.linkedin.com/uas/oauth2/authorization",grant:"https://www.linkedin.com/uas/oauth2/accessToken"},refresh:!0,scope:{basic:"r_fullprofile",email:"r_emailaddress",friends:"r_network",publish:"rw_nus"},scope_delim:" ",base:"https://api.linkedin.com/v1/",get:{me:"people/~:(picture-url,first-name,last-name,id,formatted-name,email-address)","me/friends":"people/~/connections?count=@{limit|500}","me/followers":"people/~/connections?count=@{limit|500}","me/following":"people/~/connections?count=@{limit|500}","me/share":"people/~/network/updates?count=@{limit|250}"},post:{"me/share":function(e,t){var n={visibility:{code:"anyone"}};e.data.id?n.attribution={share:{id:e.data.id}}:(n.comment=e.data.message,e.data.picture&&e.data.link&&(n.content={"submitted-url":e.data.link,"submitted-image-url":e.data.picture})),e.data=JSON.stringify(n),t("people/~/shares?format=json")},"me/like":s},del:{"me/like":s},wrap:{me:function(e){return t(e),n(e),e},"me/friends":o,"me/following":o,"me/followers":o,"me/share":function(e){if(t(e),i(e),e.values){e.data=e.values,delete e.values;for(var o=0;o<e.data.length;o++){var a=e.data[o];n(a),a.message=a.headline}}return e},"default":function(e,n){t(e),a(e,n),i(e)}},jsonp:function(e,t){r(t),"get"===e.method&&(t.format="jsonp",t["error-callback"]=e.callbackID)},xhr:function(e,t){return"get"!==e.method?(r(t),e.headers["Content-Type"]="application/json",e.headers["x-li-format"]="json",e.proxy=!0,!0):!1}}})}(hello),function(e){function t(e){e.id&&(e.picture=e.avatar_url,e.thumbnail=e.avatar_url,e.name=e.username||e.full_name)}function n(e){"next_href"in e&&(e.paging={next:e.next_href})}function o(e,t){var n=t.access_token;return delete t.access_token,t.oauth_token=n,t["_status_code_map[302]"]=200,!0}e.init({soundcloud:{name:"SoundCloud",oauth:{version:2,auth:"https://soundcloud.com/connect",grant:"https://soundcloud.com/oauth2/token"},base:"https://api.soundcloud.com/",get:{me:"me.json","me/friends":"me/followings.json","me/followers":"me/followers.json","me/following":"me/followings.json","default":function(e,t){t(e.path+".json")}},wrap:{me:function(e){return t(e),e},"default":function(e){if(e instanceof Array){e={data:e};for(var o=0;o<e.data.length;o++)t(e.data[o])}return n(e),e}},xhr:o,jsonp:o}})}(hello),function(e){function t(e){if(e.id){if(e.name){var t=e.name.split(" ");e.first_name=t[0],e.last_name=t[1]}e.thumbnail=e.profile_image_url_https||e.profile_image_url}}function n(e){if(o(e),i(e),e.users){e.data=e.users;for(var n=0;n<e.data.length;n++)t(e.data[n]);delete e.users}return e}function o(e){if(e.errors){var t=e.errors[0];e.error={code:"request_failed",message:t.message}}}function i(e){"next_cursor_str"in e&&(e.paging={next:"?cursor="+e.next_cursor_str})}function a(t){return e.utils.isArray(t)?{data:t}:t}var r="https://api.twitter.com/";e.init({twitter:{oauth:{version:"1.0a",auth:r+"oauth/authenticate",request:r+"oauth/request_token",token:r+"oauth/access_token"},base:r+"1.1/",get:{me:"account/verify_credentials.json","me/friends":"friends/list.json?count=@{limit|200}","me/following":"friends/list.json?count=@{limit|200}","me/followers":"followers/list.json?count=@{limit|200}","me/share":"statuses/user_timeline.json?count=@{limit|200}","me/like":"favorites/list.json?count=@{limit|200}"},post:{"me/share":function(e,t){var n=e.data;e.data=null,n.file?(e.data={status:n.message,"media[]":n.file},t("statuses/update_with_media.json")):t(n.id?"statuses/retweet/"+n.id+".json":"statuses/update.json?include_entities=1&status="+n.message)},"me/like":function(e,t){var n=e.data.id;e.data=null,t("favorites/create.json?id="+n)}},del:{"me/like":function(){p.method="post";var e=p.data.id;p.data=null,callback("favorites/destroy.json?id="+e)}},wrap:{me:function(e){return o(e),t(e),e},"me/friends":n,"me/followers":n,"me/following":n,"me/share":function(e){return o(e),i(e),!e.error&&"length"in e?{data:e}:e},"default":function(e){return e=a(e),i(e),e}},xhr:function(e){return"get"!==e.method}}})}(hello),function(e){function t(e,t,n){if(e.id){var o=n.query.access_token;if(e.emails&&(e.email=e.emails.preferred),e.is_friend!==!1){var i=e.user_id||e.id;e.thumbnail=e.picture="https://apis.live.net/v5.0/"+i+"/picture?access_token="+o}}}function n(e,n,o){if("data"in e)for(var i=0;i<e.data.length;i++)t(e.data[i],n,o);return e}e.init({windows:{name:"Windows live",oauth:{version:2,auth:"https://login.live.com/oauth20_authorize.srf",grant:"https://login.live.com/oauth20_token.srf"},refresh:!0,logout:function(){return"http://login.live.com/oauth20_logout.srf?ts="+(new Date).getTime()},scope:{basic:"wl.signin,wl.basic",email:"wl.emails",birthday:"wl.birthday",events:"wl.calendars",photos:"wl.photos",videos:"wl.photos",friends:"wl.contacts_emails",files:"wl.skydrive",publish:"wl.share",publish_files:"wl.skydrive_update",create_event:"wl.calendars_update,wl.events_create",offline_access:"wl.offline_access"},base:"https://apis.live.net/v5.0/",get:{me:"me","me/friends":"me/friends","me/following":"me/contacts","me/followers":"me/friends","me/contacts":"me/contacts","me/albums":"me/albums","me/album":"@{id}/files","me/photo":"@{id}","me/files":"@{parent|me/skydrive}/files","me/folders":"@{id|me/skydrive}/files","me/folder":"@{id|me/skydrive}/files"},post:{"me/albums":"me/albums","me/album":"@{id}/files/","me/folders":"@{id|me/skydrive/}","me/files":"@{parent|me/skydrive/}/files"},del:{"me/album":"@{id}","me/photo":"@{id}","me/folder":"@{id}","me/files":"@{id}"},wrap:{me:function(e,n,o){return t(e,n,o),e},"me/friends":n,"me/contacts":n,"me/followers":n,"me/following":n,"me/albums":function(e){if("data"in e)for(var t=0;t<e.data.length;t++){var n=e.data[t];n.photos=n.files="https://apis.live.net/v5.0/"+n.id+"/photos"}return e},"default":function(e){if("data"in e)for(var t=0;t<e.data.length;t++){var n=e.data[t];n.picture&&(n.thumbnail=n.picture)}return e}},xhr:function(t){return"get"===t.method||"delete"===t.method||e.utils.hasBinary(t.data)||("string"==typeof t.data.file?t.data.file=e.utils.toBlob(t.data.file):(t.data=JSON.stringify(t.data),t.headers={"Content-Type":"application/json"})),!0},jsonp:function(t){"get"===t.method||e.utils.hasBinary(t.data)||(t.data.method=t.method,t.method="get")}}})}(hello),function(e){function t(e){e&&"meta"in e&&"error_type"in e.meta&&(e.error={code:e.meta.error_type,message:e.meta.error_message})}function n(e,n,i){t(e),o(e,n,i);var a,r;if(e.query&&e.query.results&&e.query.results.contact){e.data=e.query.results.contact,delete e.query,e.data instanceof Array||(e.data=[e.data]);for(var s=0;s<e.data.length;s++){a=e.data[s],a.id=null;for(var l=0;l<a.fields.length;l++)r=a.fields[l],"email"===r.type&&(a.email=r.value),"name"===r.type&&(a.first_name=r.value.givenName,a.last_name=r.value.familyName,a.name=r.value.givenName+" "+r.value.familyName),"yahooid"===r.type&&(a.id=r.value)}}return e}function o(e,t,n){e.query&&e.query.count&&n.options&&(e.paging={next:"?start="+(e.query.count+(+n.options.start||1))})}var i=function(e){return"https://query.yahooapis.com/v1/yql?q="+(e+" limit @{limit|100} offset @{start|0}").replace(/\s/g,"%20")+"&format=json"};e.init({yahoo:{oauth:{version:"1.0a",auth:"https://api.login.yahoo.com/oauth/v2/request_auth",request:"https://api.login.yahoo.com/oauth/v2/get_request_token",token:"https://api.login.yahoo.com/oauth/v2/get_token"},login:function(e){e.options.window_width=560;try{delete e.qs.state.scope}catch(t){}},base:"https://social.yahooapis.com/v1/",get:{me:i("select * from social.profile(0) where guid=me"),"me/friends":i("select * from social.contacts(0) where guid=me"),"me/following":i("select * from social.contacts(0) where guid=me")},wrap:{me:function(e){if(t(e),e.query&&e.query.results&&e.query.results.profile){e=e.query.results.profile,e.id=e.guid,e.last_name=e.familyName,e.first_name=e.givenName||e.nickname;var n=[];e.first_name&&n.push(e.first_name),e.last_name&&n.push(e.last_name),e.name=n.join(" "),e.email=e.emails&&e.emails[0]?e.emails[0].handle:null,e.thumbnail=e.image?e.image.imageUrl:null}return e},"me/friends":n,"me/following":n,"default":function(e){return o(e),e}}}})}(hello),"function"==typeof define&&define.amd&&define(function(){return hello}),"object"==typeof module&&module.exports&&(module.exports=hello);

var Pylot = {

    /**
    Google Analytics tracking
    **/
    trackEvent: function(category, action, label, value) {
        if (typeof ga !== 'undefined') {
            ga("send", "event", category, action, label, value)
        }
    },

    //------

    /**
    BASIC Login
    **/
    basic_login: function() {
        var that = this
        $("#pylot-login-login-form").submit(function(e){
            e.preventDefault();
            that.trackEvent("User", "LOGIN", "Email")
            this.submit()
        })
        $("#pylot-login-signup-form").submit(function(e){
            e.preventDefault();
            that.trackEvent("User", "SIGNUP", "Email")
            this.submit()
        })
        $("#pylot-login-lostpassword-form").submit(function(e){
            e.preventDefault();
            that.trackEvent("User", "LOSTPASSWORD", "Email")
            this.submit()
        })
    },

    //-------

    /**
    OAUTH Login
    Requires hello.js for front end authentication
    **/
    oauth_login: function(config, redirect) {

        var that = this
        hello.init(config, {redirect_uri: redirect, scope: "email"})

        $("[pylot\\:oauth-login]").click(function(){

            var el = $(this)
            var form = el.closest("form")
            var status = form.find(".status-message")

            var provider = el.attr("pilot:oauth-login")
            if (provider == "google-plus") {
                provider = "google"
            }

            hello(provider).login({"force": true}).then( function(p){

                hello(provider).api( '/me' ).then( function(r){

                    var msg = form.data("success-message") || "Signing in..."
                    status.removeClass("alert alert-danger")
                        .addClass("alert alert-success").html(msg)

                    var image_url = r.thumbnail
                    switch(provider) {
                        case "facebook":
                            image_url += "?type=large"
                            break
                        case "google":
                            image_url = image_url.split("?")[0]
                    }
                    form.find("[name='provider']").val(provider)
                    form.find("[name='provider_user_id']").val(r.id)
                    form.find("[name='name']").val(r.name)
                    form.find("[name='email']").val(r.email)
                    form.find("[name='image_url']").val(image_url)

                    that.trackEvent("User", "LOGIN", "SOCIAL:" + provider)
                    form.submit()
                });

            }, function( e ){
                var msg = form.data("error-message") || "Unable to signin..."

                status.removeClass("alert alert-success")
                    .addClass("alert alert-danger").html(msg)
            });

        })
    }
}