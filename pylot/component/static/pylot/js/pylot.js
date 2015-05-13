
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
