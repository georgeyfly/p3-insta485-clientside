"""REST API for posts."""
import flask
import insta485
import insta485.views.index as views
# GET / api/v1 / Return API resource URLs
# GET / api/v1/posts / Return 10 newest post urls and ids
# GET / api/v1/posts /?size = N	Return N newest post urls and ids
# GET / api/v1/posts /?page = N	Return N’th page of post urls and ids
# GET / api/v1/posts /?postid_lte = N	Return post urls and ids no newer than post id N
# GET / api/v1/posts/<postid > /	Return one post, including comments and likes
# POST / api/v1/likes /?postid = <postid > Create a new like for the specified post id
# DELETE / api/v1/likes/<likeid > /	Delete the like based on the like id
# POST / api/v1/comments /?postid = <postid > Create a new comment based on the text in the JSON body for the specified post id
# DELETE / api/v1/comments/<commentid > /	Delete the comment based on the comment id

@insta485.app.route('/api/v1/')
def get_api():
    """
    Return a list of services available. 
    Does not require user to be authenticated.
    """
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context)

@insta485.app.route('/api/v1/posts/')
def get_posts():
    """
    Return the 10 newest posts. 
    The posts should meet the following criteria: 
    each post is made by a user which the logged in user follows 
    or the post is made by the logged in user. 
    The URL of the next page of posts is returned in next. 
    Note that postid is an int, not a string.
    # The URL of the next page of posts is returned in next
    # Request results no newer than postid with ?postid_lte = N
    # Request a specific number of results with ?size=N
    # Request a specific page of results with ?page = N
    # page 0-index 
    """
    # authorization
    doAuth, username = doAuthorize()
    if not doAuth:
        return flask.jsonify(context_403), 403
    
    # normal query
    conneciton = insta485.model.get_db()
    query = """
        SELECT postid
        FROM posts
        WHERE owner IN (
            SELECT username2
            FROM following
            WHERE username1 = ?
        )
        OR owner = ?
        ORDER BY postid DESC
    """
    # query args
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    postid_lte = flask.request.args.get("postid_lte", default=None, type=int)
    arg_list = [username, username]
    if size < 0 or page < 0:
        return flask.jsonify(context_400), 400
    if postid_lte is not None:
        query = query.replace("ORDER BY postid DESC",
                              "AND postid <= ? ORDER BY postid DESC")
        arg_list.append(postid_lte)
    query += "LIMIT ? OFFSET ?"
    arg_list.append(size)
    arg_list.append(page * size)
    cur = conneciton.execute(query, arg_list)
    results = cur.fetchall()

    # add url to results
    url = "/api/v1/posts/"
    for result in results:
        result["url"] = url + str(result["postid"]) + "/"

    # get next_page_url
    next_page_url = ""
    if len(results) == size:
        newest_postid_lte = results[0]["postid"]
        next_page_url = f"/api/v1/posts/?size={size}&page={page+1}&postid_lte={newest_postid_lte}"
    
    # get url
    if flask.request.query_string.decode() != "":
        url = flask.request.path + '?' + flask.request.query_string.decode()
    else:
        url = flask.request.path
    # combine all
    context = {
        "next": next_page_url,
        "results": results,
        "url": url
    }
    return flask.jsonify(context), 200


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid.
    """
    # authorization
    doAuth, username = doAuthorize()
    if not doAuth:
        return flask.jsonify(context_403), 403
    
    # query
    conneciton = insta485.model.get_db()

    # query comments
    query = """
        SELECT commentid, owner, text
        FROM comments
        WHERE postid = ?
    """
    cur = conneciton.execute(query, (postid_url_slug,))
    comment_results = cur.fetchall()
    for result in comment_results:
        comment_owner = result["owner"]
        comment_id = result["commentid"]
        result["lognameOwnsThis"] = comment_owner == username
        result["ownerShowUrl"] = f"/users/{comment_owner}/"
        result["url"] = f"/api/v1/comments/{comment_id}/"
    # query post
    query = """
        SELECT *
        FROM posts
        WHERE postid = ?
    """
    cur = conneciton.execute(query, (postid_url_slug,))
    post_results = cur.fetchone()
    if post_results is None:
        return flask.jsonify(context_404), 404
    owner = post_results['owner']
    imgUrl = post_results['filename']
    created = post_results['created']
    
    # query owner
    query = """
        SELECT filename
        FROM users
        WHERE username = ?
    """
    cur = conneciton.execute(query, (owner,))
    owner_imgUrl = cur.fetchone()['filename']
    
    # query likes
    query = """
        SELECT *
        FROM likes
        WHERE owner = ? AND postid = ?
    """
    cur = conneciton.execute(query, (username, postid_url_slug))
    like_result = cur.fetchone()
    if like_result is None:
        lognameLikesThis = False;
        like_url = None 
    else:
        likeid = like_result['likeid']
        lognameLikesThis = True;
        like_url = f"/api/v1/likes/{likeid}/"
    query = """
        SELECT *
        FROM likes
        WHERE postid = ?
    """
    cur = conneciton.execute(query, (postid_url_slug,))
    numlikes = len(cur.fetchall())

    context = {
        "comments": comment_results,
        "comments_url": f"/api/v1/comments/?postid={postid_url_slug}",
        "created": created,
        "imgUrl": f"/uploads/{imgUrl}",
        "likes": {
            "lognameLikesThis": lognameLikesThis,
            "numLikes": numlikes,
            "url": like_url
        },
        "owner": owner,
        "ownerImgUrl": f"/uploads/{owner_imgUrl}",
        "ownerShowUrl": f"/users/{owner}/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": postid_url_slug,
        "url": flask.request.path,
    }
    return flask.jsonify(context), 200

@insta485.app.route('/api/v1/likes/', methods=['POST'])
def post_like():
    # authorization
    doAuth, username = doAuthorize()
    if not doAuth:
        return flask.jsonify(context_403), 403
    
    postid = flask.request.args.get("postid", None)
    connection = insta485.model.get_db()
    query = """
        SELECT likeid
        FROM likes
        WHERE owner = ? AND postid = ?
    """
    cur = connection.execute(query, (username, postid))
    likeid = cur.fetchone()
    doCreate = False
    if likeid is None:
        doCreate = True
        query = """
            INSERT INTO likes (owner, postid)
            VALUES (?,?)
        """
        cur = connection.execute(query, (username, postid))
        connection.commit()
        likeid = cur.lastrowid
    else:
        likeid = likeid['likeid']
    context = {
        "likeid": likeid,
        "url": f"/api/v1/likes/{likeid}/"
    }
    if doCreate:
        return flask.jsonify(context), 201
    return flask.jsonify(context), 200
    # return flask.jsonify(context), 201 if doCreate else flask.jsonify(context), 200


@insta485.app.route('/api/v1/likes/<likeid>/', methods=['DELETE'])
def delete_like(likeid):
    # authorization
    doAuth, username = doAuthorize()
    if not doAuth:
        return flask.jsonify(context_403), 403
    # query
    connection = insta485.model.get_db()
    query = """
        SELECT owner
        FROM likes
        WHERE likeid = ?
    """
    cur = connection.execute(query, (likeid,))
    like_result = cur.fetchone()
    if like_result is None:
        return flask.jsonify(context_404), 404
    owner = like_result['owner']
    if owner != username:
        return flask.jsonify(context_403), 403
    query = """
        DELETE 
        FROM likes
        WHERE likeid = ?
    """
    connection.execute(query, (likeid,))
    connection.commit()
    return flask.jsonify({}), 204

@insta485.app.route('/api/v1/comments/', methods=['POST'])
def post_comment():
    # authorization
    doAuth, username = doAuthorize()
    if not doAuth:
        return flask.jsonify(context_403), 403
    
    # get parameter
    postid = flask.request.args.get('postid', None)
    text = flask.request.json.get('text', '')

    # post comment
    connection = insta485.model.get_db()
    query = """
        INSERT INTO comments (owner, postid, text)
        VALUES (?,?,?)
    """
    cur = connection.execute(query, (username, postid, text))
    connection.commit()
    # query = """
    #     SELECT last_insert_rowid()
    # """
    # cur = connection.execute(query)
    # commentid = cur.fetchone()['last_insert_rowid()']
    commentid = cur.lastrowid

    context = {
        "commentid": commentid,
        "lognameOwnsThis": True,
        "owner": username,
        "ownerShowUrl": f"/users/{username}/",
        "text": text,
        "url": f"/api/v1/comments/{commentid}/"
    }
    return flask.jsonify(context), 201


@insta485.app.route('/api/v1/comments/<commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    # authorization
    doAuth, username = doAuthorize()
    if not doAuth:
        return flask.jsonify(context_403), 403
    # query
    connection = insta485.model.get_db()
    query = """
        SELECT owner
        FROM comments
        WHERE commentid = ?
    """
    cur = connection.execute(query, (commentid,))
    comment_result = cur.fetchone()
    if comment_result is None:
        return flask.jsonify(context_404), 404
    owner = comment_result['owner']
    if owner != username:
        return flask.jsonify(context_403), 403
    query = """
        DELETE 
        FROM comments
        WHERE commentid = ?
    """
    connection.execute(query, (commentid,))
    connection.commit()
    return flask.jsonify({}), 204

def doAuthorize():
    if 'logname' in flask.session:
        return True, flask.session['logname']
    # 1. no authorization
    authorization = flask.request.authorization
    if authorization is None:
        return False, None
    
    username = flask.request.authorization.get('username')
    password = flask.request.authorization.get('password')

    # 2. no username or password
    if not username or not password:
        return False, username
    # 3. password match
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (username,)
    )
    query = cur.fetchone()
    old_password_hash_true = query['password']
    old_password_hash_input = views.password_hash_input(password, views.get_salt(
        old_password_hash_true
        )
    )
    if old_password_hash_input == old_password_hash_true:
        return True, username
    # 4. password not match
    return False, username

context_403 = {
    "message": "Forbidden",
    "status_code": 403
}

context_400 = {
    "message": "Bad Request",
    "status_code": 400
}

context_404 = {
    "message": "Not Found",
    "status_code": 404
}
