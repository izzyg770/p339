"""REST API for posts."""
import flask
import ccp


def pets_sorter():
    """Sort pets."""
    # Connect to database
    connection = ccp.model.get_db()
    # Query database
    cur_posts = connection.execute(
        "SELECT "
        "p.postid, "
        "p.created, "
        "p.owner AS post_owner, "
        "p.filename AS post_filename, "
        "c.commentid, "
        "c.owner AS comment_owner, "
        "c.text AS comment_text, "
        "c.created AS comment_created, "
        "u.filename AS user_filename, "
        "u.username, "
        "u.fullname, "
        "(SELECT COUNT(*) FROM likes l WHERE l.postid = p.postid) "
        "AS like_count, "
        "CASE WHEN l.owner IS NOT NULL THEN 1 ELSE 0 END AS user_liked "
        "FROM posts p "
        "LEFT JOIN following f ON p.owner = f.username2 "
        "AND f.username1 = ? "
        "LEFT JOIN comments c ON p.postid = c.postid "
        "LEFT JOIN likes l ON p.postid = l.postid AND l.owner = ? "
        "JOIN users u ON p.owner = u.username "
        "WHERE f.username1 IS NOT NULL OR p.owner = ? "
        "GROUP BY p.postid, p.created, p.filename, "
        "p.owner, u.filename, u.username, u.fullname, "
        "c.commentid, c.owner, c.text, c.created "
        "ORDER BY p.postid DESC, c.commentid ASC",
        (logname, logname, logname)
    )

    return cur_posts.fetchall()


@insta485.app.route('/api/v1/pets/')
def get_pet():
    """Return 10 newest pet likes and ids."""
    connection = ccp.model.get_db()
    url = "/api/v1/pets/"  # base url

    # Extract query parameters with default values using tip in spec
    postid_lte = flask.request.args.get("postid_lte", default=None, type=int)
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)

    # Append parameters to the url if they are present and diff from default
    # Make sure ? will go first with args not present
    if flask.request.args.get("size"):
        url += f"?size={size}"
    if flask.request.args.get("page"):
        url += "&" if "?" in url else "?"
        url += f"page={page}"
    if flask.request.args.get("postid_lte"):
        url += "&" if "?" in url else "?"
        url += f"postid_lte={postid_lte}"

    if size < 0 or page < 0:  # Response according to SPEC they must be non neg
        context = {
            "message": "Bad Request",
            "status_code": 400
        }
        return flask.jsonify(**context), 400

    # If postid_lte is not provided default to the most recent postid
    if postid_lte is None:
        latest_post_query = connection.execute(
            "SELECT MAX(postid) AS max_postid FROM posts "
        )
        postid_lte_result = latest_post_query.fetchone()
        postid_lte = postid_lte_result["max_postid"]

    cur_posts = connection.execute(
        "WITH RecentPosts AS ( "
        "SELECT p.postid, p.owner "
        "FROM posts p "
        "WHERE p.owner = ? "
        "UNION "
        "SELECT p.postid, p.owner "
        "FROM posts p "
        "JOIN following f ON p.owner = f.username2 "
        "WHERE f.username1 = ? "
        ") "
        "SELECT rp.postid "
        "FROM RecentPosts rp "
        "WHERE (? IS NULL OR rp.postid <= ?) "
        "ORDER BY rp.postid DESC "
        "LIMIT ? OFFSET ? ",
        (logname, logname, postid_lte, postid_lte, size, page * size)
    )
    fetched_posts = cur_posts.fetchall()

    # insert correct url's into ten_posts
    ten_posts = [
        {"postid": post["postid"], "url": f"/api/v1/posts/{post['postid']}/"}
        for post in fetched_posts
    ]

    if len(fetched_posts) < size:  # no more posts to put on another page SPEC
        return flask.jsonify(results=ten_posts, next="", url=url)

    n_s = f"/api/v1/posts/?size={size}&page={page + 1}&postid_lte={postid_lte}"
    return flask.jsonify(results=ten_posts, next=n_s, url=url)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def api_get_post(postid_url_slug):
    """Return details for one post."""
    authenticate()
    logname = flask.session['username']
    connection = insta485.model.get_db()

    # Check if the post with given postid exists
    post_query = connection.execute(
        "SELECT * FROM posts WHERE postid = ?",
        (postid_url_slug,)
    )
    post = post_query.fetchone()
    if not post:  # message matches SPEC
        context = {
            "status_code": 404,
            "message": "Not Found"
        }
        return flask.jsonify(**context), 404

    owner_query = connection.execute(
        "SELECT * FROM users WHERE username = ?",
        (post["owner"],)
    )
    owner = owner_query.fetchone()

    # Retrieve comments for the post
    comments_query = connection.execute(
        "SELECT * FROM comments WHERE postid = ?",
        (postid_url_slug,)
    )
    comments = [
        {
            "commentid": comment["commentid"],
            "lognameOwnsThis": comment["owner"] == logname,
            "owner": comment["owner"],
            "ownerShowUrl": f"/users/{comment['owner']}/",
            "text": comment["text"],
            "url": f"/api/v1/comments/{comment['commentid']}/"
        }
        for comment in comments_query.fetchall()
    ]

    # Retrieve likes information for the post
    likes_query = connection.execute(
        "SELECT * FROM likes WHERE postid = ?",
        (postid_url_slug,)
    )
    likes = {
        "lognameLikesThis": False,
        "numLikes": len(likes_query.fetchall()),
        "url": None
    }

    # Check if the logged-in user likes the post
    # default is none and not liked matching SPEC
    if logname:
        user_like_query = connection.execute(
            "SELECT * FROM likes WHERE postid = ? AND owner = ?",
            (postid_url_slug, logname)
        )
        user_like = user_like_query.fetchone()
        if user_like:
            likes["lognameLikesThis"] = True
            likes["url"] = f"/api/v1/likes/{user_like['likeid']}/"

    context = {
        "comments": comments,
        "comments_url": f"/api/v1/comments/?postid={postid_url_slug}",
        "created": post["created"],
        "imgUrl": f"/uploads/{post['filename']}",
        "likes": likes,
        "owner": post["owner"],
        "ownerImgUrl": f"/uploads/{owner['filename']}",
        "ownerShowUrl": f"/users/{post['owner']}/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": postid_url_slug,
        "url": f"/api/v1/posts/{postid_url_slug}/"
    }

    return flask.jsonify(**context)
