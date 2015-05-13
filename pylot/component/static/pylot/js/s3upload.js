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