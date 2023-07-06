"""
Insta485 index (main) view.

URLs include:
/
"""
import hashlib
import flask
import insta485
from flask import send_from_directory
import arrow
import uuid
import pathlib
insta485.app.secret_key = insta485.config.SECRET_KEY

@insta485.app.route('/')
## logname, posts: owner, owner_img_url, img_url, post_id, timestamp, comment, likes
def show_index():
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    cur = connection.execute(
        """
        SELECT * FROM posts 
        WHERE owner IN ( 
            SELECT username2 FROM following
            WHERE username1 = ?
        ) OR owner = ?
        """,
        (flask.session['logname'], flask.session['logname'])
    )
    # add likes and comments
    posts = cur.fetchall()
    # Add database info to context
    for post in posts:
        # add comments to post
        cur = connection.execute(
            "SELECT owner, text "
            "FROM comments "
            "WHERE postid = ? ",
            (post['postid'],)
        )
        comments = cur.fetchall()
        # add likes to post
        cur = connection.execute(
            "SELECT owner "
            "FROM likes "
            "WHERE postid = ?",
            (post['postid'],)
        )

        likes = cur.fetchall()
        # add owner_url to post
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (post['owner'],)
        )
        owner_url = cur.fetchall()
        # is logname like post
        cur = connection.execute(
            "SELECT likeid "
            "FROM likes "
            "WHERE postid = ? AND owner = ?",
            (post['postid'], flask.session['logname'])
        )
        doLike = cur.fetchall()
        if len(doLike) == 1:
            post['doLike'] = True
        else:
            post['doLike'] = False
        post['comments'] = comments
        post['likes'] = len(likes)
        post['owner_url'] = owner_url[0]['filename']
        post['timestamp'] = arrow.get(post['created']).to('US/Eastern').humanize()
    context = {"posts": posts}
    return flask.render_template("index.html", **context)


@insta485.app.route('/users/<user_url_slug>/')
def show_user(user_url_slug):
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    # Connect to database
    connection = insta485.model.get_db()
    # total posts postid img_url
    cur = connection.execute(
        "SELECT filename, postid "
        "FROM posts "
        "WHERE owner = ?",
        (user_url_slug,)
    )
    posts = cur.fetchall()

    # followers
    cur = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2 = ?",
        (user_url_slug,)
    )
    followers = cur.fetchall()
    # following
    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ?",
        (user_url_slug,)
    )
    following = cur.fetchall()
    # name
    cur = connection.execute(
        "SELECT fullname "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug,)
    )
    fullname = cur.fetchone()['fullname']
    # isFollow
    cur = connection.execute(
        "SELECT created "
        "FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (flask.session['logname'], user_url_slug)
    )
    created = cur.fetchall()
    if len(created) != 0:
        logFollowUser = True
    else:
        logFollowUser = False

    # 
    context = {"username": user_url_slug,
               "posts": posts, 
               "total_posts": len(posts),
               "following": len(following),
               "followers": len(followers),
               "fullname": fullname,
               "logFollowUser": logFollowUser
               }
    return flask.render_template('user.html', **context)

@insta485.app.route('/users/<user_url_slug>/followers/')
def show_followers(user_url_slug):
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    # followers
    cur = connection.execute(
        "SELECT username1, username2 "
        "FROM following "
        "WHERE username2 = ?",
        (user_url_slug,)
    )
    followers = cur.fetchall()
    # user_img_url
    for follower in followers:
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (follower['username1'],)
        )
        user_img_url = cur.fetchone()
        follower['user_img_url'] = user_img_url['filename']

        # isFollow
        cur = connection.execute(
            "SELECT created "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (flask.session['logname'], follower['username1'])
        )
        created = cur.fetchall()
        if len(created) != 0:
            logFollowUser = True
        else:
            logFollowUser = False
        follower['logFollowUser'] = logFollowUser
    context = {"followers": followers}
    return flask.render_template('followers.html', **context)

@insta485.app.route('/users/<user_url_slug>/following/')
def show_following(user_url_slug):
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    # followers
    cur = connection.execute(
        "SELECT username1, username2 "
        "FROM following "
        "WHERE username1 = ?",
        (user_url_slug,)
    )
    following = cur.fetchall()
    # user_img_url
    for follow in following:
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (follow['username2'],)
        )
        user_img_url = cur.fetchone()
        follow['user_img_url'] = user_img_url['filename']
        # isFollow
        cur = connection.execute(
            "SELECT created "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (flask.session['logname'], follow['username2'])
        )
        created = cur.fetchall()
        if len(created) != 0:
            logFollowUser = True
        else:
            logFollowUser = False
        follow['logFollowUser'] = logFollowUser
    context = {"following": following}
    return flask.render_template('following.html', **context)

@insta485.app.route('/posts/<postid_url_slug>/')
def show_posts(postid_url_slug):
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    # Connect to database
    connection = insta485.model.get_db()
    # filename, owner, timestamp
    cur = connection.execute(
        "SELECT filename, owner, created "
        "FROM posts "
        "WHERE postid = ?",
        (postid_url_slug,)
    )
    post = cur.fetchone()
    # owner_img_url
    cur = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ?",
        (post['owner'],)
    )
    owner_img_url = cur.fetchone()
    # likes
    cur = connection.execute(
        "SELECT likeid "
        "FROM likes "
        "WHERE postid = ?",
        (postid_url_slug,)
    )
    likes = len(cur.fetchall())
    # doLike
    cur = connection.execute(
        "SELECT likeid "
        "FROM likes "
        "WHERE owner = ? AND postid = ?",
        (flask.session['logname'], postid_url_slug)
    )
    doLike = len(cur.fetchall()) == 1
    # comments
    cur = connection.execute(
        "SELECT text, owner, commentid "
        "FROM comments "
        "WHERE postid = ?",
        (postid_url_slug,)
    )
    comments = cur.fetchall()
    context = {"owner": post['owner'],
               "owner_img_url": owner_img_url['filename'],
               "img_url": post['filename'],
               "timestamp": arrow.get(post['created']).to('US/Eastern')\
                .humanize(),
               "comments": comments,
               "likes": likes,
               "postid": postid_url_slug,
               "doLike": doLike
               }
    return flask.render_template('post.html', **context)

@insta485.app.route('/explore/')
def show_explore():
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    # not_following db query
    connection = insta485.model.get_db()
    cur = connection.execute(
        """
        SELECT username, filename 
        FROM users 
        WHERE username NOT IN (
            SELECT username2 
            FROM following 
            WHERE username1 = ?
        )
        """,
        (flask.session['logname'],)
    )
    not_following = cur.fetchall()
    for nfollow in not_following:
        nfollow['user_img_url'] = nfollow['filename']
    context = {
        "not_following": not_following
    }
    return flask.render_template("explore.html", **context)

@insta485.app.route('/uploads/<filename>')
def uploaded_file(filename):
    if 'logname' not in flask.session:
        flask.abort(403)
    upload_folder = insta485.app.config["UPLOAD_FOLDER"]
    file_path = upload_folder / filename
    if not file_path.is_file():
        flask.abort(404)
    return flask.send_from_directory(upload_folder, filename)

@insta485.app.route('/likes/', methods=['POST'])
def handle_like():
    target = flask.request.args.get('target')
    if not target:
        target = flask.url_for('show_index')
    connection = insta485.model.get_db()
    logname = flask.session['logname']
    operation = flask.request.form.get('operation')
    postid = flask.request.form.get('postid')
    check = connection.execute(
        "SELECT likeid "
        "FROM likes "
        "WHERE postid = ? AND owner = ?",
        (postid, logname)
    ).fetchall()

    if operation == 'like':
        if len(check) == 0:
            connection.execute(
                "INSERT INTO likes (postid, owner) "
                "VALUES (?,?)",
                (postid, logname)
            )
            connection.commit()
            return flask.redirect(target)
        return flask.abort(409)
    
    if operation == 'unlike':
        if len(check) == 1:
            connection.execute(
                "DELETE FROM likes "
                "WHERE postid = ? AND owner = ?",
                (postid, logname)
            )
            connection.commit()
            return flask.redirect(target)
        return flask.abort(409)

@insta485.app.route('/comments/', methods=['POST'])
def handle_comment():
    target = flask.request.args.get('target')
    if not target:
        target = flask.url_for('show_index')
    connection = insta485.model.get_db()
    logname = flask.session['logname']
    operation = flask.request.form.get('operation')
    postid = flask.request.form.get('postid')
    # create comments
    if operation == 'create':
        # check empty comment
        text = flask.request.form.get('text')
        if text is None:
            flask.abort(400)
        connection.execute(
            "INSERT INTO comments (postid, owner, text) "
            "VALUES (?,?,?)",
            (postid, logname, text)
        )
        connection.commit()
        return flask.redirect(target)
    # delete comment
    if operation == 'delete':
        commentid = flask.request.form.get('commentid')
        connection.execute(
            "DELETE FROM comments "
            "WHERE owner = ? AND commentid = ?",
            (logname, commentid)
        )
        connection.commit()
        return flask.redirect(target)

@insta485.app.route('/following/', methods=['POST'])
def handle_following():
    target = flask.request.args.get('target')
    if not target:
        target = flask.url_for('show_index')
    operation = flask.request.form.get('operation')
    username = flask.request.form.get('username')
    connection = insta485.model.get_db()
    # follow
    if operation == 'follow':
        connection.execute(
            "INSERT INTO following (username1, username2) "
            "VALUES (?,?)",
            (flask.session['logname'], username)
        )
        connection.commit()
    elif operation == 'unfollow':
        connection.execute(
            "DELETE FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (flask.session['logname'], username)
        )
        connection.commit()
    return flask.redirect(target)

############################### handle_post#####################################
@insta485.app.route('/posts/', methods=['POST'])
def handle_post():
    target = flask.request.args.get('target')
    if target is None:
        target = flask.url_for('show_user', user_url_slug=flask.session['logname'])
    operation = flask.request.form.get('operation')
    if operation == 'create':
        handle_post_create()
    elif operation == 'delete':
        handle_post_delete()
    return flask.redirect(target)

def handle_post_create():
    fileobj = flask.request.files.get('file')
    if fileobj is None:
        flask.abort(400)
    filename = save_file(fileobj, fileobj.filename)
    connection = insta485.model.get_db()
    connection.execute(
        "INSERT INTO posts (filename, owner) "
        "VALUES (?,?)",
        (filename, flask.session['logname'])
    )
    connection.commit()

def handle_post_delete():
    postid = flask.request.form.get('postid')
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT owner "
        "FROM posts "
        "WHERE postid = ?",
        (postid,)
    )
    username = cur.fetchone()['owner']
    if username != flask.session['logname']:
        flask.abort(403)
    # delete file
    cur = connection.execute(
        "SELECT filename "
        "FROM posts "
        "WHERE postid = ?",
        (postid,)
    )
    filename = cur.fetchone()['filename']
    file_path = insta485.app.config["UPLOAD_FOLDER"] / filename
    if file_path.exists():
        file_path.unlink()
    connection.execute(
        "DELETE FROM posts "
        "WHERE postid = ?",
        (postid,)
    )
    connection.commit()
############################### handle_account##################################
@insta485.app.route('/accounts/', methods=['POST'])
def handle_account():
    target = flask.request.args.get('target')
    if target is None:
        target = flask.url_for('show_index')
    operation = flask.request.form.get('operation')
    if operation == 'login':
        handle_account_login()
    elif operation == 'create':
        handle_account_create()
    elif operation == 'delete':
        handle_account_delete()
    elif operation == 'edit_account':
        handle_account_edit()
    elif operation == 'update_password':
        handle_account_update()
    return flask.redirect(target)

@insta485.app.route('/accounts/login/', methods=['GET'])
def login():
    if 'logname' not in flask.session:
        return flask.render_template('login.html')
    return flask.redirect(flask.url_for('show_index'))

@insta485.app.route('/accounts/create/', methods=['GET'])
def create():
    return flask.render_template('create.html')

@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for('login'))

@insta485.app.route('/accounts/delete/', methods=['GET'])
def delete():
    return flask.render_template('delete.html')


@insta485.app.route('/accounts/edit/', methods=['GET'])
def show_edit():
    connection = insta485.model.get_db()
    # owner_img_url
    cur = connection.execute(
        "SELECT filename, email, fullname "
        "FROM users "
        "WHERE username = ?",
        (flask.session['logname'],)
    )
    info = cur.fetchone()
    owner_img_url = info['filename']
    email = info['email']
    fullname = info['fullname']
    context = {'email': email,
               'owner_img_url': owner_img_url,
               'fullname': fullname}
    return flask.render_template('edit.html', **context)

@insta485.app.route('/accounts/password/', methods=['GET'])
def password():
    return flask.render_template('password.html')

@insta485.app.route('/accounts/auth/', methods=['GET'])
def show_auth():
    if 'logname' in flask.session:
        return '', 200
    else: 
        flask.abort(403)

def handle_account_login():
    # check username & password
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    if username is None or password is None:
        flask.abort(400)
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (username,)
    )
    # password = password_hash('password')
    password_hash_true = cur.fetchone()
    # if username exist/ not
    if password_hash_true is None:
        flask.abort(403)
    else:
        password_hash_true = password_hash_true['password']
        password_hash_inpu = password_hash_input(
            password, get_salt(password_hash_true)
        )
        if password_hash_true == password_hash_inpu:
            flask.session['logname'] = username
        else:
            flask.abort(403)

def handle_account_create():
    # check username & password & fullname & email & file
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    fullname = flask.request.form.get('fullname')
    email = flask.request.form.get('email')
    fileobj = flask.request.files["file"]
    if username is None or password is None or \
        fullname is None or email is None or fileobj is None:
        flask.abort(400)
    filename = save_file(fileobj, fileobj.filename)
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (username,)
    )
    password_hash_true = cur.fetchone()
    # if username exist/ not
    if password_hash_true is not None:
        flask.abort(409)
    else:
        password_hash_true = password_hash(password)
        connection.execute(
            "INSERT INTO users (username, fullname, email, filename, password) "
            "VALUES (?,?,?,?,?)",
            (username, fullname, email, filename, password_hash_true)
        )
        connection.commit()
        flask.session['logname'] = username

def handle_account_delete():
    if 'logname' not in flask.session:
        flask.abort(403)
    connection = insta485.model.get_db()
    # delete post
    cur = connection.execute(
        "SELECT filename "
        "FROM posts "
        "WHERE owner = ?",
        (flask.session['logname'],)
    )
    posts_filename = cur.fetchall()
    for post_filename in posts_filename:
        file_path = insta485.app.config["UPLOAD_FOLDER"] / post_filename['filename']
        if file_path.exists():
            file_path.unlink()
    # delete profile
    cur = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ?",
        (flask.session['logname'],)
    )
    filename = cur.fetchone()['filename']
    file_path = insta485.app.config["UPLOAD_FOLDER"] / filename
    if file_path.exists():
        file_path.unlink()
    # delete db
    connection.execute(
        "DELETE "
        "FROM users "
        "WHERE username = ?",
        (flask.session['logname'],)
    )
    connection.commit()
    flask.session.clear()


def handle_account_edit():
    if 'logname' not in flask.session:
        flask.abort(403)
    fullname = flask.request.form.get('fullname')
    email = flask.request.form.get('email')
    fileobj = flask.request.files.get("file")
    if fullname is None or email is None:
        flask.abort(400)
    connection = insta485.model.get_db()
    # delete old file
    if fileobj:
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (flask.session['logname'],)
        )
        old_filename = cur.fetchone()['filename']
        file_path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"]) / old_filename
        if file_path.exists():
            file_path.unlink()
        # update new file
        new_filename = save_file(fileobj, fileobj.filename)
        connection.execute(
            "UPDATE users "
            "SET filename = ? "
            "WHERE username = ?",
            (new_filename, flask.session['logname'])
        )
        connection.commit()
    # update email and fullname
    connection.execute(
        "UPDATE users "
        "SET fullname = ?, email = ? "
        "WHERE username = ?",
        (fullname, email, flask.session['logname'])
    )
    connection.commit()


def handle_account_update():
    """
    """
    if 'logname' not in flask.session:
        flask.abort(403)
    password = flask.request.form.get('password')
    new_password1 = flask.request.form.get('new_password1')
    new_password2 = flask.request.form.get('new_password2')
    if password is None or new_password1 is None or new_password2 is None:
        flask.abort(400)
    # check old password
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (flask.session['logname'],)
    )
    query = cur.fetchone()
    old_password_hash_true = query['password']
    old_password_hash_input = password_hash_input(password, get_salt(
        old_password_hash_true
        )
    )
    if old_password_hash_true != old_password_hash_input:
        flask.abort(403)
    # check new password match
    if new_password1 != new_password2:
        flask.abort(401)
    # update new password
    new_password_hash = password_hash(new_password1)
    connection.execute(
        "UPDATE users "
        "SET password = ? "
        "WHERE username = ?",
        (new_password_hash, flask.session['logname'])
    )
    connection.commit()

####################################function####################################
def get_salt(password_hashed):
    """
    get salt from hashed password, return '' if no hash algorithm is used
    """
    parts = password_hashed.split('$')
    if len(parts) < 2:
        return ''
    return parts[1]

def password_hash_input(psword, salt):
    """
    get hashed password with password and salt
    """
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + psword
    hash_obj.update(password_salted.encode('utf-8'))
    password_hashed = hash_obj.hexdigest()
    if salt == '':
        return psword
    password_db_string = "$".join([algorithm, salt, password_hashed])
    return password_db_string


def password_hash(psword):
    """
    return hashed password if password is given
    """
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + psword
    hash_obj.update(password_salted.encode('utf-8'))
    password_hashed = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hashed])
    return password_db_string

def save_file(fileobj, filename):
    """
    Compute base name (filename without directory).  We use a UUID to avoid
    clashes with existing files, and ensure that the name is compatible with the
    filesystem. For best practive, we ensure uniform file extensions (e.g.
    lowercase).
    """
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    return uuid_basename
