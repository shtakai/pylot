
import datetime
from pylot import utils
from active_sqlalchemy import SQLAlchemy


class ModelError(Exception):
    pass


# The user_model create a fully built model with social signin
def user_struct(db):

    if not isinstance(db, SQLAlchemy):
        raise AssertionError("'db' must be an 'active_sqlalchemy' instance")

    class UserRole(db.Model):
        name = db.Column(db.String(75), index=True, unique=True)
        description = db.Column(db.String(250))

        @classmethod
        def new(cls, name, description=None):
            name = name.upper()
            role = cls.get_by_name(name)
            if not role:
                role = cls.create(name=name, description=description)
            return role

        @classmethod
        def get_by_name(cls, name):
            name = name.upper()
            return cls.all().filter(cls.name == name).first()


    class User(db.Model):
        STATUS_ACTIVE = "ACTIVE"
        STATUS_SUSPENDED = "SUSPENDED"
        STATUS_DELETED = "DELETED"

        email = db.Column(db.String(75), index=True, unique=True)
        email_confirmed = db.Column(db.Boolean, default=False)
        password_hash = db.Column(db.String(250))
        require_password_change = db.Column(db.Boolean, default=False)
        reset_password_token = db.Column(db.String(100), index=True)
        reset_password_token_expiration = db.Column(db.DateTime)
        name = db.Column(db.String(250))
        status = db.Column(db.String(25), default=STATUS_ACTIVE)
        is_loggedin = db.Column(db.Boolean, default=False)
        profile_pic_url = db.Column(db.String(250))
        signup_method = db.Column(db.String(250))
        last_login = db.Column(db.DateTime)
        last_visited = db.Column(db.DateTime)
        roles = db.relationship(UserRole, secondary="user_role_role")

        # ------ FLASK-LOGIN REQUIRED METHODS ----------------------------------

        def is_active(self):
            """True, as all users are active."""
            return True

        def get_id(self):
            """Return the id """
            return self.id

        def is_authenticated(self):
            """Return True if the user is authenticated."""
            return True

        def is_anonymous(self):
            """ False, as anonymous users aren't supported."""
            return False
        # ---------- END FLASK-LOGIN REQUIREMENTS ------------------------------

        @classmethod
        def get_by_email(cls, email):
            """
            Find by email. Useful for logging in users
            """
            return cls.all().filter(cls.email == email).first()

        @classmethod
        def get_by_token(cls, token):
            """
            Find by email. Useful for logging in users
            """
            user = cls.all().filter(cls.reset_password_token == token).first()
            if user:
                print user
                now = datetime.datetime.now()
                print now
                if user.require_password_change is True \
                        and user.reset_password_token_expiration > now:
                    return user
                else:
                    user.clear_reset_password_token()
            else:
                return None

        @classmethod
        def new(cls, email, password=None, role="USER", **kwargs):
            """
            Register a new user
            """
            user = cls.get_by_email(email)
            if user:
                raise ModelError("User exists already")
            user = cls.create(email=email)
            if password:
                user.set_password(password)
            if kwargs:
                user.update(**kwargs)
            user.add_role(role)
            return user

        def password_matched(self, password):
            """
            Check if the password matched the hash
            :returns bool:
            """
            return utils.verify_encrypted_string(password, self.password_hash)

        def set_password(self, password):
            """
            Encrypt the password and save it in the DB
            """
            self.update(password_hash=utils.encrypt_string(password))

        def set_random_password(self):
            """
            Set a random password, saves it and return the readable string
            :returns string:
            """
            password = utils.generate_random_string()
            self.set_password(password)
            return password

        def set_reset_password_token(self, expiration=24):
            """
            Generate password reset token
            It returns the token generated
            """
            expiration = datetime.datetime.now() + datetime.timedelta(hours=expiration)
            while True:
                token = utils.generate_random_string(32).lower()
                if not User.all().filter(User.reset_password_token == token).first():
                    break
            self.update(require_password_change=True,
                        reset_password_token=token,
                        reset_password_token_expiration=expiration)
            return token

        def clear_reset_password_token(self):
            """
            Clear the reset password token
            """
            self.update(require_password_change=False,
                        reset_password_token=None,
                        reset_password_token_expiration=None)

        def set_require_password_change(self, req=True):
            """
            Set the require password change ON/OFF
            :params req: bool
            """
            self.update(require_password_change=req)

        def add_role(self, name):
            role = UserRole.get_by_name(name)
            if role:
                UserRoleRole.add(self.id, role.id)
            else:
                raise ModelError("Role '%s' doesn't exist" % name )

        def update_last_login(self):
            """
            TO update the last login
            :return:
            """
            self.update(last_login=datetime.datetime.now())

        def update_last_visited(self):
            """
            Update last visited
            :return:
            """
            self.update(last_visited=datetime.datetime.now())

        @classmethod
        def oauth_register(cls, provider, provider_user_id=None,
                          email=None, name=None, image_url=None,
                          **kwargs):
            """
            Register
            :param provider:
            :param provider_user_id:
            :param email:
            :param name:
            :param image_url:
            :param kwargs:
            :return:
            """
            oal = UserOauthLogin
            oauthuser = oal.all()\
                .filter(oal.provider == provider)\
                .filter(oal.provider_user_id == provider_user_id)\
                .first()
            if oauthuser:
                return oauthuser.user
            else:
                if not email:
                    raise ModelError("Email is missing")

                data = {
                    "provider": provider,
                    "provider_user_id": provider_user_id,
                    "email": email,
                    "name": name,
                    "image_url": image_url
                }

                user = cls.get_by_email(email)
                if user:
                    data.update({"user_id": user.id})
                    oal.create(**data)
                    return user
                else:
                    user = cls.new(email=email,
                                    name=name,
                                    profile_pic_url=image_url,
                                    signin_method=provider)
                    data.update({"user_id": user.id})
                    oal.create(**data)
                    return user

        def oauth_connect(self, provider, provider_user_id=None,
                          email=None, name=None, image_url=None,
                          **kwargs):
            """
            Connect an account an OAUTH
            :param provider:
            :param provider_user_id:
            :param email:
            :param name:
            :param image_url:
            :param kwargs:
            :return:
            """
            oal = UserOauthLogin
            oauthuser = oal.all()\
                .filter(oal.provider == provider)\
                .filter(oal.provider_user_id == provider_user_id)\
                .first()
            if oauthuser:
                if oauthuser.user_id == self.id:
                    return self
                else:
                    raise ModelError("Account is already linked to another user")
            else:
                data = {
                    "provider": provider,
                    "provider_user_id": provider_user_id,
                    "email": email,
                    "name": name,
                    "image_url": image_url,
                    "user_id": self.id
                }
                oal.create(**data)
                return self

    class UserRoleRole(db.Model):
        user_id = db.Column(db.Integer, db.ForeignKey(User.id))
        role_id = db.Column(db.Integer, db.ForeignKey(UserRole.id))

        @classmethod
        def add(cls, user_id, role_id):
            r = cls.all().filter(cls.user_id == user_id)\
                .filter(cls.role_id == role_id)\
                .first()
            if not r:
                cls.create(user_id=user_id, role_id=role_id)

        @classmethod
        def remove(cls, user_id, role_id):
            r = cls.all().filter(cls.user_id == user_id)\
                .filter(cls.role_id == role_id)\
                .first()
            if not r:
                r.delete(hard_delete=True)

    class UserOauthLogin(db.Model):
        user_id = db.Column(db.Integer, db.ForeignKey(User.id))
        provider = db.Column(db.String(50), index=True)
        provider_user_id = db.Column(db.String(250))
        name = db.Column(db.String(250))
        email = db.Column(db.String(250))
        image_url = db.Column(db.String(250))
        access_token = db.Column(db.String(250))
        secret = db.Column(db.String(250))
        profile_url = db.Column(db.String(250))
        user = db.relationship(User, backref="oauth_logins")

    return utils.to_struct(User=User,
                           Role=UserRole,
                           RoleRole=UserRoleRole,
                           OauthLogin=UserOauthLogin)

# File assets manager
def asset_struct(UserStruct):

    db = UserStruct.User.db

    class AssetFile(db.Model):
        LOCATION_S3 = "S3"
        LOCATION_LOCAL = "LOCAL"
        LOCATION_OTHER = "OTHER"

        user_id = db.Column(db.Integer, db.ForeignKey(UserStruct.User.id))
        name = db.Column(db.String(250))
        extension = db.Column(db.String(10))
        type = db.Column(db.String(250))
        size = db.Column(db.Integer)
        path = db.Column(db.String(250))
        location = db.Column(db.String(250))
        url = db.Column(db.String(250))
        description = db.Column(db.String(250))
        image_width = db.Column(db.Integer)
        image_height = db.Column(db.Integer)
        user = db.relationship(UserStruct.User, backref="files")

        @classmethod
        def new(cls, location, object_name):
            pass

    return utils.to_struct(File=AssetFile)


def post_struct(UserStruct):
    """
    Post Model

    """

    db = UserStruct.User.db

    class SlugNameMixin(object):
        name = db.Column(db.String(250))
        slug = db.Column(db.String(250), index=True, unique=True)

        @classmethod
        def get_by_slug(cls, slug):
            """
            Return a post by slug
            """
            return cls.all().filter(cls.slug == slug).first()

        @classmethod
        def new(cls, name, slug=None):
            slug = utils.slug(name if not slug else slug)
            return cls.create(name=name, slug=slug)

        def rename(self, name, slug=None):
            slug = utils.slug(name if not slug else slug)
            return self.update(name=name, slug=slug)

    class PostType(SlugNameMixin, db.Model):
        @property
        def total_posts(self):
            return Post.all().filter(Post.type_id == self.id).count()

    class PostCategory(SlugNameMixin, db.Model):
        @property
        def total_posts(self):
            return PostPostCategory.all()\
                .filter(PostPostCategory.category_id == self.id)\
                .count()

    class PostPostCategory(db.Model):
        post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
        category_id = db.Column(db.Integer, db.ForeignKey(PostCategory.id))

        @classmethod
        def add(cls, post_id, category_id):
            c = cls.all().filter(cls.post_id == post_id)\
                .filter(cls.category_id == category_id)\
                .first()
            if not c:
                cls.create(post_id=post_id, category_id=category_id)

        @classmethod
        def remove(cls, post_id, category_id):
            c = cls.all().filter(cls.post_id == post_id)\
                .filter(cls.category_id == category_id)\
                .first()
            if c:
                c.delete(hard_delete=True)

    class Post(db.Model):

        user_id = db.Column(db.Integer, db.ForeignKey(UserStruct.User.id))
        type_id = db.Column(db.Integer, db.ForeignKey(PostType.id))
        parent_id = db.Column(db.Integer)
        revision_id = db.Column(db.Integer)
        title = db.Column(db.String(250))
        slug = db.Column(db.String(250), index=True)
        content = db.Column(db.Text)
        excerpt = db.Column(db.Text)
        is_public = db.Column(db.Boolean, index=True, default=False)
        is_sticky = db.Column(db.Boolean, index=True, default=False)
        is_published = db.Column(db.Boolean, index=True, default=True)
        is_draft = db.Column(db.Boolean, index=True, default=False)
        is_revision = db.Column(db.Boolean, default=False)
        published_date = db.Column(db.DateTime)
        author = db.relationship(UserStruct.User, backref="posts")
        type = db.relationship(PostType, backref="posts")
        categories = db.relationship(PostCategory,
                                     secondary=PostPostCategory.__table__.name)


        @classmethod
        def new(cls, title, **kwargs):
            """
            Insert a new post
            """
            published_date = None
            is_revision = False
            is_published = False
            is_draft = False
            is_public = kwargs["is_public"] if "is_public" in kwargs else True
            parent_id = int(kwargs["parent_id"]) if "parent_id" in kwargs else None
            if "is_revision" in kwargs and kwargs["is_revision"] is True:
                if not parent_id:
                    raise ModelError("'parent_id' is missing for revision")
                is_revision =True
                is_public = False
            elif "is_draft" in kwargs and kwargs["is_draft"] is True:
                is_draft = True
                is_public = False
            elif "is_published" in kwargs and kwargs["is_published"] is True:
                is_published = True
                published_date = datetime.datetime.now()

            slug = ""
            if is_published or is_draft:
                slug = cls.create_slug(title if "slug" not in kwargs else kwargs["slug"])

            data = {
                "title": title,
                "slug": slug,
                "content": kwargs["content"] if "content" in kwargs else "",
                "excerpt": kwargs["excerpt"] if "excerpt" in kwargs else "",
                "is_published": is_published,
                "published_date": published_date,
                "is_draft": is_draft,
                "is_revision": is_revision,
                "is_public": is_public,
                "parent_id": parent_id,
                "type_id": kwargs["type_id"] if "type_id" in kwargs else None
            }
            return cls.create(**data)

        @classmethod
        def get_published(cls, id=None, slug=None):
            """
            Get a published post by id or slug
            :param id: The id of the post
            :param slug: str - The slug to look for
            """
            post = None
            if id:
                post = cls.get(id)
            elif slug:
                post = cls.get_by_slug(slug)
            return post if post and post.is_published else None

        @classmethod
        def get_published_by_category_slug(cls, slug):
            """
            Query by category slug
            :return SQLA :
            """
            return cls.all()\
                .join(PostPostCategory)\
                .join(PostCategory)\
                .filter(PostCategory.slug == slug)\
                .filter(cls.is_published == True)

        @classmethod
        def get_published_by_type_slug(cls, slug):
            """
            Query by type slug
            :return SQLA :
            """
            return cls.all()\
                .join(PostType)\
                .filter(PostType.slug == slug)\
                .filter(cls.is_published == True)

        @classmethod
        def create_slug(cls, title):
            slug_counter = 0
            _slug = utils.slug(title).lower()
            while True:
                slug = _slug
                if slug_counter > 0:
                    slug += str(slug_counter)
                    slug_counter += 1
                if not cls.get_by_slug(slug):
                    break
            return slug

        @classmethod
        def get_by_slug(cls, slug):
            """
            Return a post by slug
            """
            return cls.all().filter(cls.slug == slug).first()

        def publish(self, published_date=None):
            if self.is_draft:
                data = {
                    "is_draft": False,
                    "is_published": True,
                    "published_date": published_date or datetime.datetime.now()
                }
                self.update(**data)

        def set_type(self, type_id):
            self.update(type_id=type_id)

        def set_slug(self, title):
            slug = utils.slug(title)
            if title and slug != self.slug:
                slug = self.create_slug(slug)
                self.update(slug=slug)

        def replace_categories(self, categories_list):
            cats = PostPostCategory.all()\
                    .filter(PostPostCategory.post_id == self.id)
            cats_list = [c.category_id for c in cats]

            del_cats = list(set(cats_list) - set(categories_list))
            new_cats = list(set(categories_list) - set(cats_list))

            for dc in del_cats:
                PostPostCategory.remove(post_id=self.id, category_id=dc)

            for nc in new_cats:
                PostPostCategory.add(post_id=self.id, category_id=nc)

        @property
        def status(self):
            if self.is_published:
                return "Published"
            elif self.is_draft:
                return "Draft"
            elif self.is_revision:
                return "Revision"

        def delete_revisions(self):
            """
            Delete all revisions
            """
            try:
                Post.all()\
                    .filter(Post.post_id == self.id)\
                    .filter(Post.is_revision == True)\
                    .delete()
                Post.db.commit()
            except Exception as ex:
                Post.db.rollback()

        @property
        def total_revisions(self):
            return Post.all()\
                .filter(Post.post_id == self.id)\
                .filter(Post.is_revision == True)\
                .count()


    return utils.to_struct(Post=Post,
                           Category=PostCategory,
                           Type=PostType,
                           PostCategory=PostPostCategory
                           )

