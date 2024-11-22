from flask import Blueprint, flash, redirect, render_template, request, url_for, flash
from flask_login import login_required, current_user
from .models import user as User, post as Post, connect as Connect, approvedconnection as ApprovedConnection, db
from  sqlalchemy.sql.expression import func
from sqlalchemy import text
from werkzeug.utils import secure_filename
import os
from . import *

views = Blueprint('views', __name__)

@views.route('/')
def index():
    """Displays six random alumni and schools"""
    alumni = User.query.order_by(func.rand()).limit(4)
    schools = db.session.execute(text('SELECT DISTINCT school FROM user  ORDER BY RAND() LIMIT 8'))
    return render_template("index.html", alumni=alumni, schools=schools)

@views.route('/home')
@login_required 
def home():
    """Displays home page with six random alumni from the same alma mata"""
    alumni = User.query.filter_by().order_by(func.rand())
    return render_template("home.html", user=current_user, alumni=alumni)

@views.route('/about')
def about():
    """Returns about page"""
    return render_template("about.html")

@views.route('/profile', methods=['GET'])
@login_required 
def profile():
    """Returns profile of alumnus of interest"""
    id = request.args.get('id')
    query = text('SELECT * FROM user WHERE id = :val')
    alumnus = db.session.execute(query, {'val': id})
    return render_template("profile.html", user=current_user, alumnus=alumnus)

@views.route('/request_connection', methods=['GET'])
@login_required
def requestconnection():
    """Writes connection to connect table and redirects to connection page"""
    id = request.args.get('id')
    connreq = Connect(initid=current_user.id, recid=id)
    db.session.add(connreq)
    db.session.commit()
    flash('Connection request sent!', category='success')
    return redirect(url_for('views.connections'))

@views.route('/connectprofile', methods=['GET'])
@login_required 
def connectprofile():
    """Returns profile of alumnus connected with"""
    id = request.args.get('id')
    alumnus = db.session.execute(text('SELECT * FROM user WHERE id = :val', {'val': id}))
    return render_template("connectprofile.html", user=current_user, alumnus=alumnus)

@views.route('/pendingrequest')
@login_required
def connection_request():
    """Returns alumni who have been sent a connection request"""
    query = text('SELECT * FROM user INNER JOIN connect ON\
         user.id = connect.recid WHERE connect.initid = :val')
    requested_connections = db.session.execute(query, {'val': current_user.id})
    return render_template('pendingrequests.html', requested_connections = requested_connections)

@views.route('/connections')
@login_required
def connections():
    """Returns alumni connections"""
    query = text('SELECT * FROM user INNER JOIN approvedconnection ON\
         user.id = approvedconnection.connectb WHERE approvedconnection.connecta  = :val')
    query1=text('SELECT * FROM user INNER JOIN approvedconnection ON\
         user.id = approvedconnection.connecta WHERE approvedconnection.connectb = :val')
    approved_sent_connections = db.session.execute(query, {'val': current_user.id})
    approved_request_connections = db.session.execute(query1, {'val': current_user.id})
    return render_template('connections.html', approved_sent_connections = approved_sent_connections,\
         approved_request_connections = approved_request_connections)

@views.route('/pendingapproval')
@login_required
def connection_approve():
    """Returns alumni who want to connect"""
    query=text('SELECT * FROM user INNER JOIN connect ON user.id = connect.initid WHERE\
         connect.recid = :val')
    approve_connections = db.session.execute(query, {'val': current_user.id})
    return render_template('pendingapprovals.html', approve_connections = approve_connections)

@views.route('/approval', methods=['GET'])
@login_required
def connection_approval():
    """Approve connection requests"""
    approve = request.args.get('approve')

    if (approve != 404):
        connapp = ApprovedConnection(connecta=current_user.id, connectb=approve)
        db.session.add(connapp)
        Connect.query.filter(Connect.initid == approve).delete()
        db.session.commit()
        flash('Connection approved!', category='success')
        return redirect(url_for('views.connection_approval'))

@views.route('/declinereq', methods=['GET'])
@login_required
def connection_sent_decline():
    """Decline sent connection request(s)"""
    decline = request.args.get('decline')

    if (decline != 404):
        Connect.query.filter(Connect.recid == decline).delete()
        db.session.commit()
        flash('Connection request removed!', category='success')
        return redirect(url_for('views.connection_request'))

@views.route('/decline', methods=['GET'])
@login_required
def connection_decline():
    """Decline received connection request(s)"""
    decline = request.args.get('decline')

    if (decline != 404):
        Connect.query.filter(Connect.initid == decline).delete()
        db.session.commit()
        flash('Connection declined!', category='success')
        return redirect(url_for('views.connection_approval'))

@views.route('/posts')
@login_required 
def posts():
    """Returns posts by alma mater alumni"""
    query = text('SELECT * FROM user INNER JOIN post ON user.id = post.userid WHERE\
         user.school = :val ORDER BY post.date DESC')
    posts = db.session.execute(query, {'val': current_user.school})
    return render_template("posts.html", user=current_user, posts=posts)

@views.route('/post', methods=['GET', 'POST'])
@login_required 
def post():
    """Writes posts to DB"""
    if request.method == 'POST':
        text = request.form.get('text')

        if len(text) < 10:
            flash('Post is too short!', category='error')
        elif len(text) > 10000:
            flash('Post is too long!', category='error')
        else:
            new_post = Post(text=text, userid=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash('Post is added successfully!', category='success')
            return redirect(url_for("views.post"))

    return render_template("post.html")    

@views.route('/deletepost', methods=['GET'])
@login_required
def delete_post():
    """Delete a post"""
    id = request.args.get('id')
    Post.query.filter(Post.id == id).delete()
    db.session.commit()
    return redirect(url_for("views.post"))

@views.route('/myprofile', methods=['GET', 'POST'])
@login_required 
def my_profile():
    """Returns profile of current user"""
    if request.method == 'POST':
        bio = request.form.get('bio')
        db.session.query(User).\
            filter(User.id == current_user.id).\
                update({'bio': bio})
        db.session.commit()
        return redirect(url_for("views.my_profile"))

    return render_template("myprofile.html", user=current_user)


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@views.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files["files[]"]
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for("views.my_profile"))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            from main import app
            basedir = os.path.abspath(os.path.dirname(__file__))
            file.save(os.path.join(basedir,
                                       app.config['UPLOAD_FOLDER'], filename))
            filepath = UPLOAD_FOLDER + '/' + filename
            query = text('UPDATE user SET avatar = :val WHERE id = :ID')
            db.session.execute(query, {'val': filepath, 'ID': current_user.id} )
            db.session.commit()
            flash('Profile picture successfully uploaded')
            return redirect(url_for("views.my_profile"))
        else:
            flash("Something went wrong please try again and make sure image is a jpg, jpeg, png, or gif")
            return redirect(url_for("views.my_profile"))     

@views.route('/chats')
@login_required 
def chats():
    """Messages sent to or received from fellow alumni"""

    # Get connections
    query = text('SELECT * FROM user INNER JOIN approvedconnection ON\
         user.id = approvedconnection.connectb WHERE approvedconnection.connecta  = :val')
    query1 = text('SELECT * FROM user INNER JOIN approvedconnection ON\
         user.id = approvedconnection.connecta WHERE approvedconnection.connectb = :val')
    approved_sent_connections = db.session.execute(query, {'val': current_user.id})
    approved_request_connections = db.session.execute(query1, {'val': current_user.id})

    return render_template("chats.html", approved_sent_connections=approved_sent_connections,\
         approved_request_connections=approved_request_connections)
