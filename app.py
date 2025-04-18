from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

active_users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    active_users[request.sid] = username
    join_room('chatroom')
    emit('user_list', list(active_users.values()), broadcast=True, room='chatroom')
    emit('message', {
        'message': f"{username} has joined the chat.",
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'username': 'System'
    }, broadcast=True, room='chatroom')

@socketio.on('message')
def handle_message(data):
    message = data['message']
    username = active_users.get(request.sid, 'Unknown')
    emit('message', {
        'message': message,
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'username': username
    }, broadcast=True, room='chatroom')

@socketio.on('leave')
def handle_leave():
    username = active_users.pop(request.sid, 'Unknown')
    leave_room('chatroom')
    emit('user_list', list(active_users.values()), broadcast=True, room='chatroom')
    emit('message', {
        'message': f"{username} has left the chat.",
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'username': 'System'
    }, broadcast=True, room='chatroom')

if __name__ == '__main__':
    socketio.run(app, debug=True)