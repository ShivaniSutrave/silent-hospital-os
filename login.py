from flask import Blueprint, render_template_string, redirect, url_for, request
from flask_login import login_user, logout_user, login_required
from database import db, User
from markupsafe import Markup

auth = Blueprint('auth', __name__)

STYLE = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: system-ui, sans-serif;
    background: #0d0d1a;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}
.card {
    background: #16162a;
    border: 0.5px solid #2a2a4a;
    border-radius: 16px;
    padding: 36px;
    width: 420px;
}
.logo { font-size: 32px; text-align: center; margin-bottom: 8px; }
h1 { font-size: 20px; font-weight: 500; color: #9d97e8; text-align: center; margin-bottom: 4px; }
.sub { font-size: 12px; color: #a0a0c0; text-align: center; margin-bottom: 24px; }
.section-label {
    font-size: 10px; color: #6a6a8a; text-transform: uppercase;
    letter-spacing: 0.08em; margin-bottom: 10px;
}
.tab-row { display: flex; gap: 8px; margin-bottom: 16px; }
.tab {
    flex: 1; padding: 10px; background: #0d0d1a;
    border: 0.5px solid #2a2a4a; border-radius: 8px;
    text-align: center; cursor: pointer;
    font-size: 12px; color: #a0a0c0; transition: all 0.2s;
}
.tab:hover { border-color: #9d97e8; color: #9d97e8; background: #12122a; }
.tab.active { border-color: #534AB7; color: #9d97e8; background: #12122a; }
.tab .icon { font-size: 18px; display: block; margin-bottom: 3px; }
.name-list {
    max-height: 200px; overflow-y: auto;
    border: 0.5px solid #2a2a4a; border-radius: 8px;
    margin-bottom: 16px; display: none;
}
.name-list.show { display: block; }
.name-item {
    padding: 11px 14px; cursor: pointer;
    border-bottom: 0.5px solid #1a1a2e;
    display: flex; align-items: center; gap: 10px;
    transition: background 0.15s;
}
.name-item:last-child { border-bottom: none; }
.name-item:hover { background: #12122a; }
.name-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    background: #2a2a4a; display: flex; align-items: center;
    justify-content: center; font-size: 15px; flex-shrink: 0;
}
.name-label { flex: 1; font-size: 13px; font-weight: 500; color: #e8e8ff; }
.name-sub { font-size: 10px; color: #6a6a8a; margin-top: 2px; }
.name-arrow { color: #534AB7; font-size: 14px; }
.divider { height: 0.5px; background: #2a2a4a; margin: 16px 0; }
label { font-size: 12px; color: #a0a0c0; display: block; margin-bottom: 6px; margin-top: 12px; }
input, select {
    width: 100%; padding: 12px 14px;
    background: #0d0d1a; border: 0.5px solid #2a2a4a;
    border-radius: 8px; color: #e8e8ff; font-size: 14px;
    font-family: system-ui, sans-serif; outline: none;
}
input:focus, select:focus { border-color: #9d97e8; }
select option { background: #0d0d1a; color: #e8e8ff; }
.selected-box {
    background: #12122a; border: 0.5px solid #534AB7;
    border-radius: 8px; padding: 12px 14px; margin-bottom: 4px;
    display: flex; align-items: center; gap: 10px;
}
.selected-box .s-icon { font-size: 22px; }
.selected-box .s-name { font-size: 14px; font-weight: 500; color: #e8e8ff; }
.selected-box .s-role { font-size: 11px; color: #9d97e8; margin-top: 2px; }
.btn {
    width: 100%; padding: 13px; background: #534AB7;
    color: white; border: none; border-radius: 8px;
    font-size: 14px; font-weight: 500; cursor: pointer;
    font-family: system-ui, sans-serif; margin-top: 16px;
}
.btn:hover { background: #6b62d4; }
.btn-ghost {
    width: 100%; padding: 11px; background: transparent;
    color: #9d97e8; border: 0.5px solid #2a2a4a;
    border-radius: 8px; font-size: 13px; cursor: pointer;
    font-family: system-ui, sans-serif; margin-top: 10px;
    text-align: center; text-decoration: none; display: block;
}
.btn-ghost:hover { border-color: #9d97e8; background: #12122a; }
.error {
    background: #2a1a1a; border: 0.5px solid #F09595;
    border-radius: 8px; padding: 10px 14px;
    color: #F09595; font-size: 12px; margin-top: 12px;
}
.success {
    background: #0a2a1a; border: 0.5px solid #5DCAA5;
    border-radius: 8px; padding: 10px 14px;
    color: #5DCAA5; font-size: 12px; margin-bottom: 14px;
}
.hint { text-align: center; color: #6a6a8a; font-size: 12px; margin-top: 8px; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d0d1a; }
::-webkit-scrollbar-thumb { background: #2a2a4a; border-radius: 2px; }
"""

def name_list_html(users, role, icon):
    if not users:
        return f'<div class="name-item"><span class="name-label" style="color:#6a6a8a">No {role}s registered yet</span></div>'
    html = ''
    for u in users:
        html += f'''<div class="name-item" onclick="selectUser('{u.username}','{u.name}','{role}','{icon}')">
            <div class="name-avatar">{icon}</div>
            <div style="flex:1">
                <div class="name-label">{u.name}</div>
                <div class="name-sub">{role.capitalize()}</div>
            </div>
            <span class="name-arrow">→</span>
        </div>'''
    return html

LOGIN_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<title>Silent Hospital OS — Login</title>
<style>{{ style }}</style>
</head>
<body>
<div class="card">
    <div class="logo">🏥</div>
    <h1>Silent Hospital OS</h1>
    <p class="sub">Who are you? Select your role</p>

    {% if success %}<div class="success">✅ {{ success }}</div>{% endif %}

    <p class="section-label">I am a...</p>
    <div class="tab-row">
        <div class="tab" onclick="showRole('doctor')" id="tab-doctor">
            <span class="icon">👨‍⚕️</span>Doctor
        </div>
        <div class="tab" onclick="showRole('nurse')" id="tab-nurse">
            <span class="icon">👩‍⚕️</span>Nurse
        </div>
        <div class="tab" onclick="showRole('reception')" id="tab-reception">
            <span class="icon">🧾</span>Reception
        </div>
        <div class="tab" onclick="showRole('admin')" id="tab-admin">
            <span class="icon">👑</span>Admin
        </div>
    </div>

    <div class="name-list" id="list-doctor">{{ doctors }}</div>
    <div class="name-list" id="list-nurse">{{ nurses }}</div>
    <div class="name-list" id="list-reception">{{ receptionists }}</div>
    <div class="name-list" id="list-admin">{{ admins }}</div>

    <div id="login-form" style="display:none">
        <div class="selected-box">
            <span class="s-icon" id="sel-icon"></span>
            <div>
                <div class="s-name" id="sel-name"></div>
                <div class="s-role" id="sel-role"></div>
            </div>
        </div>

        {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}

        <form method="POST">
            <input type="hidden" name="username" id="hidden-user">
            <label>Password</label>
            <input type="password" name="password" id="pw"
                   placeholder="Enter your password" required>
            <button class="btn" type="submit">Login →</button>
        </form>
        <a href="#" class="btn-ghost" onclick="clearSel()">← Choose different role</a>
    </div>

    <div class="hint" id="hint">Select your role above to see the staff list</div>

    <div class="divider"></div>
    <a href="/signup" class="btn-ghost" style="margin-top:0">New staff? Set up your account</a>
</div>
<script>
var activeRole = null;
function showRole(role) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.name-list').forEach(l => l.classList.remove('show'));
    document.getElementById('tab-' + role).classList.add('active');
    document.getElementById('list-' + role).classList.add('show');
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('hint').style.display = 'none';
    activeRole = role;
}
function selectUser(username, name, role, icon) {
    document.getElementById('hidden-user').value = username;
    document.getElementById('sel-icon').textContent = icon;
    document.getElementById('sel-name').textContent = name;
    document.getElementById('sel-role').textContent = role.charAt(0).toUpperCase() + role.slice(1);
    document.querySelectorAll('.name-list').forEach(l => l.classList.remove('show'));
    document.getElementById('login-form').style.display = 'block';
    setTimeout(() => document.getElementById('pw').focus(), 100);
}
function clearSel() {
    document.getElementById('login-form').style.display = 'none';
    if (activeRole) {
        document.getElementById('list-' + activeRole).classList.add('show');
    }
}
</script>
</body>
</html>"""

SIGNUP_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<title>Silent Hospital OS — Set Up Account</title>
<style>{{ style }}</style>
</head>
<body>
<div class="card">
    <div class="logo">🏥</div>
    <h1>Set Up Your Account</h1>
    <p class="sub">New staff member? Create your login here</p>

    {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}

    <form method="POST">
        <label>Your Full Name</label>
        <input type="text" name="name"
               placeholder="e.g. Dr. Sarah Johnson" required autofocus>

        <label>Your Role</label>
        <select name="role" required>
            <option value="" disabled selected>Select your role</option>
            <option value="doctor">👨‍⚕️ Doctor</option>
            <option value="nurse">👩‍⚕️ Nurse</option>
            <option value="receptionist">🧾 Receptionist</option>
            <option value="admin">👑 Admin</option>
        </select>

        <label>Set Your Password</label>
        <input type="password" name="password"
               placeholder="Choose a secure password (min 4 chars)" required>

        <button class="btn" type="submit">Create Account →</button>
    </form>
    <a href="/login" class="btn-ghost">← Back to Login</a>
</div>
</body>
</html>"""

@auth.route('/login', methods=['GET', 'POST'])
def login():
    error   = None
    success = request.args.get('success')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard_view'))
        error = "Wrong password. Please try again."

    doctors       = User.query.filter_by(role='doctor').all()
    nurses        = User.query.filter_by(role='nurse').all()
    receptionists = User.query.filter_by(role='receptionist').all()
    admins        = User.query.filter_by(role='admin').all()

    return render_template_string(LOGIN_TEMPLATE,
        style=Markup(STYLE),
        error=error,
        success=success,
        doctors=Markup(name_list_html(doctors, 'doctor', '👨‍⚕️')),
        nurses=Markup(name_list_html(nurses, 'nurse', '👩‍⚕️')),
        receptionists=Markup(name_list_html(receptionists, 'receptionist', '🧾')),
        admins=Markup(name_list_html(admins, 'admin', '👑')))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        role     = request.form.get('role', '')

        if not name or not password or not role:
            error = "Please fill all fields"
        elif len(password) < 4:
            error = "Password must be at least 4 characters"
        else:
            base = name.lower().replace(' ', '').replace('.', '')
            username = base
            count = 1
            while User.query.filter_by(username=username).first():
                username = base + str(count)
                count += 1
            user = User(username=username, role=role, name=name)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(
                url_for('auth.login') +
                f'?success=Welcome {name}! Find your name in the list and login.')

    return render_template_string(SIGNUP_TEMPLATE,
        style=Markup(STYLE), error=error)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
