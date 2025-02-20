from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_cors import CORS
import eventlet 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')# Enable CORS for all origins
CORS(app)  # Add CORS support

# Store active users and rooms (for demo, ideally this would be a DB)
users = {}

@app.route('/')
def home():
    return render_template('index.html')


@socketio.on('join')
def on_join(data):
    username = data.get('username')
    room = data.get('room')
    if username and room:
        join_room(room)
        users[username] = {'room': room}
        print(f'{username} has joined room {room}')
        
        # Notify everyone in the room (including sender)
        emit('message', {'username': 'Server', 'msg': f'{username} has joined the room {room}'}, room=room, include_self=True)

@socketio.on('leave')
def on_leave(data):
    username = data.get('username')
    room = users.get(username, {}).get('room')
    if room:
        leave_room(room)
        print(f'{username} has left room {room}')  # Debugging log on server
        emit('message', {'username': 'Server', 'msg': f'{username} has left the room {room}'}, room=room)
        del users[username]
        
@socketio.on('message')
def handle_message(data):
    msg = data.get('msg')
    sender = data.get('sender')
    room = users.get(sender, {}).get('room')

    if msg and sender and room:
        print(f'{sender} (to all in room {room}): {msg}')
        emit('message', {'username': sender, 'msg': msg}, room=room, include_self=True)  # Sender sees their message




if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # Listen on all interfaces
