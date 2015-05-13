# Flask-Pilot

**Flask-Pilot** is a Flask extension that adds structure to both your views and
templates, by mapping them to each other to provide a rapid application development framework.
The extension also comes with Flask-Classy, Flask-Assets, Flask-Mail,
JQuery 2.x, Bootstrap 3.x, Font-Awesome, Bootswatch templates.
The extension also provides pre-made templates for error pages and macros.

---

<a name="toc"></a>

### Table of Contents


- [About Flask-Pilot](#about)
- [Install](#install)
- [Application Structure](#structure)
- [Create Hello World](#first-project)
- [Project Config](#config)
- [Project Views](#views)
- - [Routing](#views-routing)
- - [API](#views-api)
- - [Special Methods](#views-special-methods)
- [Project Templates](#templates)
- [Project Assets](#assets)
- [Command Line](#cammand-line)


- Features
    - Login
        - Login
        - Logout
        - Signup
        - Lost Password
        - Password Reset
    - User Manager
    - Contact
    - Maintenance
    - Post
        - blog
        - article
    - File Manager
    
    Storage: S3 or Local
    
---

<a name="about"></a>
## About Flask-Pilot

### What is it?

**Flask-Pilot** is a Flask extension that adds structure to both your views and
templates, by mapping them to each other to provide a rapid application development environment.

Flask-Pilot is extended by [Flask-Classy](https://github.com/apiguy/flask-classy) which adds structure to your views, and also come with [Flask-Assets](https://github.com/miracle2k/flask-assets) to manage your assets to merge and compress JS and CSS files, and [Flask-Mail](https://github.com/mattupstate/flask-mail) to allow you to send email from your application

Also the default project skeleton comes with the following: 

* Pre-made templates for error pages
* Macros
* [JQuery 2.x](http://jquery.com/)
* [Bootstrap 3.x](http://getbootstrap.com/)
* [Font Awesome](http://fontawesome.io/)
* [Bootswatch templates](http://bootswatch.com/)

Upon setting up your first project, everything should be ready to go. You should effortlessly implement your own views and templates. 


### Why MarcoPolo name? 

Honestly, as a developer, the hardest part of an application is to name variables or find the right name for a package (lol, just kidding). I came up with several names, and out of the blue MarcoPolo popped in my head, and I thought it sounded good. Try to say it, "Flask-Marco-Polo". You see! It's fun to say.

### Why should I use MarcoPolo instead of something else?

To tell you the truth, IDK (I don't know). Lol!

(A story of my life) This is my own experience, I have a PHP background (please don't frown upon me, you have to start somewhere). When I started to migrate over to Python, I couldn't find a low learning curve framework to get going with web development. But within days after I started Python, I discovered Bottle, it was cool. Then someone recommended Flask, now it was super cool.. anyway... 

To make a long story short...  I wanted an easy framework that maps my views to my templates on the fly without me specifying which templates to use. So my requirements would be, this framework would automatically have a basic layout, and would inject my templates inside. This would save tons of repetitive task (hmmmmm hmmmmm {% extends "whatever.html" %} {% block content %}). So Flask was the first pick, pretty easy. Then I discovered [Flask-Classy](https://github.com/apiguy/flask-classy) which adds class based views to Flask. Nice. That's a start. And everything stopped there. Oops! So from there comes MarcoPolo, it continues what Flask-Classy started by extending it to the templates. And Voila! You are here on this page, wanting to learn more about **Flask-Pilot** 

(Keep reading below to learn more)

[^ Up](#toc)

---

<a name="install"></a>
## So How to Install it? 

Well, you know the routine... 

    pip install flask-marcopolo
    
[^ Up](#toc)

## And to Setup Your First Project?

Once you finish to install Flask-Pilot, you will probably want to setup your first project.

There are two options to do so, 

1) On the command line

Flask-Pilot provides a simple command line tool to setup your project. On your command line, 
go to the directory that will host your project, and type the following:

    flask-marcopolo -c project_name
    
Where `project_name` is the name of your project. Automatically it will create your basic project, 
which will include all of its components.

2) Or you can create a structure similar to the one below:


    /root
        - run_my_project.py
        |
        - /my_project
            |
            + config.py
            |
            + /views
            |
            + /templates
                |
                + layout.html
            |
            + /static
            
            
 [Learn more on the structure](#structure)
            
[^ Up](#toc)




---

<a name="structure"></a>
## Basic Application Structure

A basic application must be directory containing the following directory: views, templates, assets

    /root
        - run_my_project.py
        |
        - /my_project
            |
            + config.py
            |
            + /views
            |
            + /templates
                |
                + layout.html
            |
            + /static
            
 *run_my_project.py*: The python to init the server
 
 
 */my_project* : The project directory
 
 
 - */config.py* : The configuration file
 
 
 - */views* : The views modules
 
 
 - */templates* : Contains the templates mapped to the views
 
 
 - */templates/layout.html* : The application's layout
 
 
 - */static* : The static files (css, js, img, ...)


### How does it work?

Let's take for example the structure below:

    /root
        - /my_project
            |
            |- config.py
            |
            |- /views
                    |
                    |
                index.py
                    |
                    + Class Index(MarcoPolo):

                            def index():...

                            def about():...

                            def contact():...
                    |
                    |
                    + Class Blog(MarcoPolo):

                            def index(self):...

                            def read(self):...
                    |
                    |
                account.py
                    |
                    + Class Index(MarcoPolo):

                            def index():...

                            def edit():...

                            def photos():...
                    |
            _ _ _ _ |
            |
            |- /templates
                    |
                /index
                    |
                    /Index
                        |
                        + index.html
                        |
                        + about.html
                        |
                        + contact.html
                     _ _|
                    |
                    /Blog
                        |
                        + index.html
                        |
                        + read.html
                     _ _|
                    |
                /account
                    |
                    |
                    /Index
                        |
                        + index.html
                        |
                        + edit.html
                        |
                        + photos.html
                     _ _|
                    |
                 _ _|
                |
                |- layout.html
            |
            |- /static
                |
                + /css
                |
                + /js
                |
                + /img
                |
                + /vendor
                

### Let's break down the `views` and `templates` piece by piece in parallel. 
    
`views` contains all the modules and `templates` contains all the `.html` mapped respectively to their modules

##### - Each module is mapped to its own template directory. It will let us to place it's own module and template i   

- Inside of `/views` we have two modules: `index.py`, `account.py`

- Inside of `/templates` we have two directories `/index`, `/account`


##### - Each module class is mapped to its own directory in the templates directory of its own module


- The module `views.index` (/views/index.py) contains two classes `Index` (views.index.Index) and `Blog` (views.index.Blog)

- The `views.index` templates are structure the same way: `/templates/index/Index` and `/templates/index/Blog` 

- The module `views.account` (/views/account.py) contains one class `Index` (views.account.Index) 

- The `views.account` templates are structured the same way: `/templates/account/Index`

##### - Each method is mapped to its own `.html` file inside of 

- The method `views.index.Index.index()` contains everything you want to do in that view

- Upon rendering, it will call the template `/templates/index/Index/index.html`

- Same for `views.index.Index.about()` -> `/templates/index/Index/about.html`

- Same for `views.index.Index.contact()` -> `/templates/index/Index/contact.html`

- Same for `views.index.Blog.index()` -> `/templates/index/Blog/index.html`

- Same for `views.index.Blog.read()` -> `/templates/index/Blog/read.html`

- Same for `views.account.Index.index()` -> `/templates/account/Index/index.html`

- Same for `views.account.Index.edit()` -> `/templates/account/Index/edit.html`

- Same for `views.account.Index.photos()` -> `/templates/account/Index/photos.html`

Pretty much that's it! Well, not really, but you get the point. :) 

Now let's go ahead and create a project.


[^ Up](#toc)

---

<a name="first-project"></a>

## Our First Project: Hello World!

A Flask-Pilot is composed of views, templates (and assets).

To create a project, Flask-Pilot requires 3 files at minimum: the view file, the template file, and the layout file.

Let's create a simple hello world. Flask-Pilot wants you to avoid some repetitive tasks, therefore it encourages you to separate your application into  different pieces, and at the end it will put them together for you.

### 1) ~/my_project

First we'll create a directory called `~/my_project/`. It can be any name you feel like. Inside of this directory, create the following directories: `~/my_project/views`, `~/my_project/templates`, `~/my_project/assets`. They will host the view modules, the templates and the static files respectively.

 

### 2) ~/my_project/templates/layout.html

Then create the layout file.

So the first thing Flask-Pilot wants you have in your project is a *`layout.html`* file. 
By default, the layout is placed at the root of **/templates** -> *`/templates/layout.html`*


Inside of the `layout.html`, Flask-Pilot requires the tag **`{% include __view_template__ %}`** . This tag actually includes the view template inside of the layout. So you no longer need to add *{% extends 'layout.html' %}* inside of your templates files. It does it for you automatically. 


~/my_project/templates/layout.html
    
    <html>
        <head><title></title></head>

        <body>
            {% include __view_template__ %}
        </body>
        
    </html>
    
    

### 3) ~/my_project/views/index.py

/views/index.py is our project module, but it can be anything else like /views/hello_world.py. So you are not restricted by the name index.py.

So the `index.py` must contain at least one class which extends *MarcoPolo*. Inside of the classes, each method will return data to be displayed on template. But it is not a requirement, as it can return other iterable type of data.

So we will create a class `index.Index(MarcoPolo)`  in ~/my_project/views/index.py

    from flask.ext.marcopolo import MarcoPolo

    class Index(MarcoPolo):
        route_base = "/"

        def index(self):
            return self.render()


### 4) ~/my_project/templates/index/Index/index.html

Yes I know everything is index. Lol! This is how you read it: **`/templates/module/Class/method.html`**

By default upon rendering the page, Flask-Pilot will associate the module's class' method to it's associative template.

Data that was assigned in the view will be passed to the template.


/templates/index/Index/index.html

    <h1>Hello World</h1>

This is the page that will be included inside of `layout.html` when you add  `{% include __view_template__ %}	`


### 5) ~/run_server.py 


*~/run_server.py* is the module that will run our Flask-Pilot project.


    from flask import Flask
    from flask.ext.marcopolo import MarcoPolo
    from my_project.views import index

    project = MarcoPolo.init(app=Flask(__name__), project_dir="~/my_project")
    
    if __name__ == "__main__":
        project.run()


So when you go to http://localhost:5000, you will see your *Hello World* page.

Pretty much that's how it is in large.


[^ Up](#toc)

---

# Learn More


Now you are probably wondering how all these magics happen. Well, like mentioned before, Flask-Pilot is extended by [Flask-Classy](https://github.com/apiguy/flask-classy) , an awesome Flask extension that adds class based views to your application.

As said earlier, each module can have multiple class based views.  Flask-Classy (Flask-Pilot by proxy) will automatically generate routes based on the methods in your views, and makes it super simple to override those routes using Flask's familiar decorator syntax.

<a name="config"></a>

## -- Config

By convention, Flask-Pilot has a configuration module at  **`~/my_project/config.py`**  (of course under each project created)

Most applications need more than one configuration. There should be at least separate configurations for the production server and the one used during development. 

An interesting pattern followed by Flask-Pilot is to use classes and inheritance for configuration:

    class BaseConfig(object):
        DEBUG = False
        TESTING = False
        DATABASE_URI = 'sqlite://:memory:'
    
    class Production(BaseConfig):
        DATABASE_URI = 'mysql://user@localhost/foo'
    
    class Dev(BaseConfig):
        DEBUG = True
    
    class Testing(BaseConfig):
        TESTING = True
        
But you can have other pattern for your application.

#### Enable a config

Let say you are in the Development environment, and you need the `Dev` config. Upon `MarcoPolo.init()` in the run_server.py, you can use 

    MarcoPolo.init(app=Flask(__name__), config="my_project.config.Dev")

And when in Production environment: 

    MarcoPolo.init(app=Flask(__name__), config="my_project.config.Production")
    
    
##### * Food for thoughts

Everybody has different ways to identify a development server from a production server. As long as it works for you, it is totally fine.

In my case, to know if I'm Prod vs Dev, I create an empty file called `~/.prod_env` on the production server. I will just check for its existence:

    touch ~/.prod_env
    
If it exists, I'm on the production server, otherwise I'm on the Dev.

    import os    
    from flask import Flask
    from flask.ext.marcopolo import MarcoPolo
    from my_project.views import index
    
    PROD_ENV =  "Production" if os.path.isfile("~/.prod_env") else "Dev"
    
    config = "my_project.views.%s" % PROD_ENV
    
    project = MarcoPolo.init(app=Flask(__name__), project_dir="~/my_project", config=config)
    
    if __name__ == "__main__":
        project.run()
        
Now on the production server, the config will be `my_project.config.Production` otherwise it will be `my_project.config.Dev`


[^ Up](#toc)

---

<a name="views"></a>

## -- Views

Views are placed inside of `~/project_name/views`

Views are classes in a module. A project can have multiple modules with multiple views. All classes must extend MarcoPolo for it to work. 

Flask-Classy (Flask-Pilot) will automatically generate routes based on the methods in your views, and makes it super simple to override those routes using Flask's familiar decorator syntax

A simple view with one page looks like this:

    from flask.ext.marcopolo import MarcoPolo

    class Index(MarcoPolo):
  		route_base = "/"
  		
        def index(self):
            return self.render()

By convention, a class called `Index` must be the entry point of the application, therefore you must set the property **`route_base="/"`**, so when you type http://mysite.com it goes to my_project.index.Index. 

Following this same convention, and this one is from Flask-Classy, having a method called `index()` will be the entry point of the application, the homepage. Anytime you have a method called `index()` it will be the entry point of that view. 

As you can see, inside of index() you notice it **`return self.render()`** . This method glues everything together for you and render the page effortlessy. 

But you don't have to return self.render(), you can  return and iterable object (i.e string) if that's what you want to achieve.

<a name="views-routing"></a>
### -- Routing --


<a name="views-api"></a>
### -- Views API --



#### * MarcoPolo.render(data={}, view_template=None, layout=None)

This is the meat of MarcoPolo, 

* **data** : A dict of data to be passed to the template

* **view_template** : The file path of the template to display. By default the template will map the view method. 

* **layout** : The layout to use upon rendering. By default /template/layout.html will be used

#### *** Other function 

For convenience, Flask-Pilot gives you some handy functions to use in your views


#### - flask.ext.marcopolo.`flash_success(message)`

Create a success flash message

#### - flask.ext.marcopolo.`flash_error(message)`

Create an error flash message

#### - flask.ext.marcopolo.`flash_info(message)`

Create an info flash message

#### - flask.ext.marcopolo.`set_cookie(key, value="", **kwargs)`

Set a cookie. 

* **key** : the key (name) of the cokkie to be set

* **value** : The value of the cookie

* **\*\*kwargs**: kw args. (max_age, expires, domain, path)

#### - flask.ext.marcopolo.`get_cookie(key)`

Read the cookie saved by that key name

#### - flask.ext.marcopolo.`del_cookie(key)`

Deletes a cookie by key


[^ Up](#toc)

---

<a name="views-special-methods"></a>
## *** Special Methods from Flask-Classy


Due to the fact that MarcoPolo extends Flask-Classy, your views get to do the same thing that Flask-Classy does. For the complete API  and documentation go to [Flask-Classy](https://github.com/apiguy/flask-classy)

#### - index()

index is generally used for home pages and lists of resources. The automatically generated route

     rule: /
     endpoint: <Class Name>:index
     method: GET

Example: [GET] http://localhost/

	from flask import request, url_for, redirect, abort
    from flask.ext.marcopolo import MarcoPolo, route, flash_success, flash_error

    class Index(MarcoPolo):
        route_base = "/"

        def index(self):
            return self.render()

#### - get(id)

get is usually used to retrieve a specific resource

     rule: /<id>
     endpoint: <Class Name>:get
     method: GET
     
     
Example: [GET] http://localhost/15

	from flask import request, url_for, redirect, abort
    from flask.ext.marcopolo import MarcoPolo, route, flash_success, flash_error


    class Index(MarcoPolo):
        route_base = "/"

        def index(self):
            return self.render()

        def get(self, id):
            # check existence of id in the database or something
            if id:
                data = {
                    "id": id,
                    "description": "New resource found with id: %s" % id
                }
                return self.render(data)
            else:
                flash_error("Entry doesn't exist")
                return redirect(url_for("Index:index"))
     
     
#### - post()

This method is generally used for creating new instances of a resource but can really be used to handle any posted data you want.

     rule: /
     endpoint: <Class Name>:post
     method: POST
     
     
Example: [POST] http://localhost/

	from flask import request, url_for, redirect, abort
    from flask.ext.marcopolo import MarcoPolo, route, flash_success, flash_error


    class Index(MarcoPolo):
        route_base = "/"

        def index(self):
            return self.render()

        def get(self, id):
            # check existence of id in the database or something
            if id:
                data = {
                    "id": id,
                    "description": "New resource found with id: %s" % id
                }
                return self.render(data)
            else:
                flash_error("Entry doesn't exist")
                return redirect(url_for("Index:index"))

        def post(self):
            #code to save post data ...
            new_data = {id: 1}
        	flash_success("Data saved successfully!")
            return redirect(url_for("Index:get", id=new_data["id"]))
    
     
#### - put(id)

For those of us using REST this one is really helpful. It's generally used to update a specific resource.

     rule: /<id>
     endpoint: <Class Name>:put
     method: PUT
     
     
     
Example: [PUT] http://localhost/15

	from flask import request, url_for, redirect, abort
    from flask.ext.marcopolo import MarcoPolo, route, flash_success, flash_error


    class Index(MarcoPolo):
        route_base = "/"

        def index(self):
            return self.render()

        def get(self, id):
            # check existence of id in the database or something
            if id:
                data = {
                    "id": id,
                    "description": "New resource found with id: %s" % id
                }
                return self.render(data)
            else:
                flash_error("Entry doesn't exist")
                return redirect(url_for("Index:index"))

        def post(self):
            #code to save post data ...
            new_data = {id: 1}
        	flash_success("Data saved successfully!")
            return redirect(url_for("Index:get", id=new_data["id"]))
    
        def put(self, id):
            #code to save with
            new_data = {id: 1}
        	flash_success("Data saved successfully!")
            return redirect(url_for("Index:get", id=new_data["id"]))
            
            
#### - delete(id)

it's commonly used to destroy a specific resource

     rule: /<id>
     endpoint: <Class Name>:delete
     method: DELETE
     
Example: [DELETE] http://localhost/15

	from flask import request, url_for, redirect, abort
    from flask.ext.marcopolo import MarcoPolo, route, flash_success, flash_error

    class Index(MarcoPolo):
        route_base = "/"

        def index(self):
            return self.render()

        def get(self, id):
            # check existence of id in the database or something
            if id:
                data = {
                    "id": id,
                    "description": "New resource found with id: %s" % id
                }
                return self.render(data)
            else:
                flash_error("Entry doesn't exist")
                return redirect(url_for("Index:index"))

        def post(self):
            #code to save post data ...
            new_data = {id: 1}
        	flash_success("Data saved successfully!")
            return redirect(url_for("Index:get", id=new_data["id"]))
    
        def put(self, id):
            #code to save with
            new_data = {id: 1}
        	flash_success("Data saved successfully!")
            return redirect(url_for("Index:get", id=new_data["id"]))
            
            
        def delete(self, id):
        	flash_success("Data deleted successfully!")
            return redirect(url_for("Index:index"))
            

[^ Up](#toc)

---

<a name="templates"></a>

## -- Templates

Your project's templates are under `~/my_project/templates`

Templates are `.html` files 

[^ Up](#toc)

---

<a name="assets"></a>
## -- Assets

Your project's assets are under `~/my_project/assets` 

Assets are CSS, JS, images and any other static files


[^ Up](#toc)

--- 

<a name="command-line"></a>
# Command line 

Oh yeah! Flask-Pilot comes with a simple command line that will help you create your project on the fly. 

Go into the directory that will contain your appliaction and run the following command:


    flask-marcopolo -c project_name
    
    
[^ Up](#toc)

---

(c) 2014 Mardix

