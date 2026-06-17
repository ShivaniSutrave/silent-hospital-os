import os, random
from datetime import datetime
from flask import redirect, url_for, request
from flask_login import LoginManager, login_required, current_user
from database import db, User, Patient, PatientHistory, Staff, Queue, init_db
from login import auth
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('healthcare/train_data.csv')
df.dropna(inplace=True)

app = dash.Dash(__name__, suppress_callback_exceptions=True, url_base_pathname='/')
app.title = "Silent Hospital OS"
server = app.server
server.secret_key = os.environ.get('SECRET_KEY', 'silent-hospital-2026')
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(server)

login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = 'auth.login'
server.register_blueprint(auth)

@login_manager.user_loader
def load_user(uid): return User.query.get(int(uid))

@server.before_request
def require_login():
    open_p = ['/login','/logout','/signup']
    if not current_user.is_authenticated:
        if not any(request.path.startswith(p) for p in open_p):
            if not request.path.startswith('/_dash'):
                return redirect(url_for('auth.login'))

ALL_ROOMS = ['ICU','Ward A','Room 1','Room 2','Room 3','Ward B']

LIGHT = {
    'bg':'#F9F8FF','card':'#FFFFFF','border':'#EEEDFE',
    'text':'#1a1a2e','muted':'#6a6a8a',
    'purple':'#534AB7','teal':'#1D9E75','coral':'#D85A30',
    'amber':'#BA7517','red':'#E24B4A','green':'#639922',
    'row_alert':'#FFF5F5','row_ready':'#F0FFF8',
    'btn_bg':'transparent','btn_border':'#534AB7','btn_text':'#534AB7',
    'input_bg':'#FFFFFF','input_text':'#1a1a2e','input_border':'#CECBF6',
}
DARK = {
    'bg':'#0d0d1a','card':'#16162a','border':'#2a2a4a',
    'text':'#e8e8ff','muted':'#a0a0c0',
    'purple':'#9d97e8','teal':'#5DCAA5','coral':'#F0997B',
    'amber':'#EF9F27','red':'#F09595','green':'#97C459',
    'row_alert':'#2a1a1a','row_ready':'#0a2a1a',
    'btn_bg':'#16162a','btn_border':'#9d97e8','btn_text':'#9d97e8',
    'input_bg':'#0d0d1a','input_text':'#e8e8ff','input_border':'#2a2a4a',
}

stay_counts = df['Stay'].value_counts().reset_index()
stay_counts.columns = ['Stay','Count']
stay_order = ['0-10','11-20','21-30','31-40','41-50','51-60','61-70','71-80','81-90','91-100','More than 100 Days']
stay_counts['Stay'] = pd.Categorical(stay_counts['Stay'], categories=stay_order, ordered=True)
stay_counts = stay_counts.sort_values('Stay')

def make_charts(C):
    f1 = px.bar(stay_counts, x='Stay', y='Count', color='Count',
        color_continuous_scale=['#EEEDFE',C['purple']],
        title='Real Patient Stay Distribution (318,438 patients)')
    f1.update_layout(plot_bgcolor=C['card'],paper_bgcolor=C['card'],
        font_color=C['text'],showlegend=False,margin=dict(t=40,b=20,l=20,r=20),coloraxis_showscale=False)
    sc = df['Severity of Illness'].value_counts()
    f2 = px.pie(values=sc.values,names=sc.index,
        color_discrete_sequence=[C['coral'],C['amber'],C['teal']],title='Severity Breakdown')
    f2.update_layout(plot_bgcolor=C['card'],paper_bgcolor=C['card'],
        font_color=C['text'],margin=dict(t=40,b=20,l=20,r=20))
    return f1,f2

def badge(text,color,bg):
    return html.Span(text,style={'fontSize':'11px','fontWeight':'500',
        'padding':'3px 10px','borderRadius':'20px','background':bg,'color':color,'marginLeft':'8px'})

def sev_badge(s):
    if s=='Extreme':  return badge(s,'#A32D2D','#FCEBEB')
    if s=='Moderate': return badge(s,'#854F0B','#FAEEDA')
    return badge(s,'#0F6E56','#E1F5EE')

def sig_pill(label,signal):
    if signal in ['Lost',None]:
        return html.Span(f"x {label}",style={'fontSize':'9px','padding':'1px 5px',
            'borderRadius':'3px','background':'#FCEBEB','color':'#A32D2D','marginRight':'3px'})
    if signal=='Active':
        return html.Span(f"● {label}",style={'fontSize':'9px','padding':'1px 5px',
            'borderRadius':'3px','background':'#E1F5EE','color':'#0F6E56','marginRight':'3px'})
    dot='●' if signal=='Strong' else '◐'
    clr='#0F6E56' if signal=='Strong' else '#854F0B'
    bg='#E1F5EE' if signal=='Strong' else '#FAEEDA'
    return html.Span(f"{dot} {label}",style={'fontSize':'9px','padding':'1px 5px',
        'borderRadius':'3px','background':bg,'color':clr,'marginRight':'3px'})

def trow(ble=None,wifi=None,bt=None,brooch=None,camera=None):
    pills=[]
    if ble    is not None: pills.append(sig_pill('BLE',ble))
    if brooch is not None: pills.append(sig_pill('Brooch',brooch))
    if wifi   is not None: pills.append(sig_pill('WiFi',wifi))
    if bt     is not None: pills.append(sig_pill('BT',bt))
    if camera is not None: pills.append(sig_pill('Cam',camera))
    return html.Div(pills,style={'display':'flex','flexWrap':'wrap','marginTop':'4px','gap':'2px'})

def lv_badge(lv,sev,C):
    mins=int((datetime.now()-lv).total_seconds()/60)
    if sev=='Extreme' and mins>30:    clr,bg,icon='#A32D2D','#FCEBEB','🚨'
    elif sev=='Moderate' and mins>60: clr,bg,icon='#854F0B','#FAEEDA','⚠️'
    elif mins>120:                    clr,bg,icon='#854F0B','#FAEEDA','⚠️'
    else:                             clr,bg,icon='#0F6E56','#E1F5EE','✓'
    lbl=f"{icon} {mins}m ago" if mins<60 else f"{icon} {mins//60}h {mins%60}m ago"
    return html.Span(lbl,style={'fontSize':'10px','padding':'2px 7px',
        'borderRadius':'4px','background':bg,'color':clr,'fontWeight':'500'})

def inp_s(C):
    return {'fontSize':'12px','padding':'6px 10px','borderRadius':'6px',
        'border':f'0.5px solid {C["input_border"]}',
        'background':C['input_bg'],'color':C['input_text'],
        'fontFamily':'system-ui','outline':'none'}

def role_badge(role):
    m={'admin':('#3C3489','#EEEDFE','👑 Admin'),
       'doctor':('#085041','#E1F5EE','👨‍⚕️ Doctor'),
       'nurse':('#712B13','#FAECE7','👩‍⚕️ Nurse'),
       'receptionist':('#633806','#FAEEDA','🧾 Reception')}
    clr,bg,lbl=m.get(role,('#888','#eee',role))
    return html.Span(lbl,style={'fontSize':'11px','padding':'3px 10px',
        'borderRadius':'20px','background':bg,'color':clr,'fontWeight':'500'})

def header_bar(C,is_dark,role,username):
    return html.Div([
        html.Div([
            html.H1("🏥 Silent Hospital OS",style={'fontSize':'24px','fontWeight':'500','color':C['purple'],'margin':'0'}),
            html.P("Zero interaction. Just works.",style={'fontSize':'13px','color':C['muted'],'margin':'4px 0 0'}),
        ]),
        html.Div([
            role_badge(role),
            html.Span(f" {username}",style={'fontSize':'12px','color':C['muted'],'marginLeft':'8px','marginRight':'16px'}),
            html.Button("☀️ Light" if is_dark else "🌙 Dark",id='theme-toggle',n_clicks=1 if is_dark else 0,
                style={'fontSize':'12px','padding':'6px 14px','borderRadius':'20px',
                    'border':f'0.5px solid {C["btn_border"]}','background':C['btn_bg'],
                    'color':C['btn_text'],'cursor':'pointer','fontFamily':'system-ui','marginRight':'8px'}),
            html.A("Logout →",href="/logout",style={'fontSize':'12px','color':C['red'],
                'textDecoration':'none','border':f'0.5px solid {C["red"]}',
                'padding':'6px 14px','borderRadius':'20px'})
        ],style={'display':'flex','alignItems':'center'})
    ],style={'display':'flex','justifyContent':'space-between','alignItems':'center','marginBottom':'24px'})

def cbox(C,children,extra=None):
    s={'background':C['card'],'borderRadius':'12px','padding':'20px',
       'border':f'0.5px solid {C["border"]}','marginBottom':'16px'}
    if extra: s.update(extra)
    return html.Div(children,style=s)

def scard(t,v,c,C):
    return html.Div([
        html.P(t,style={'fontSize':'12px','color':C['muted'],'margin':'0 0 4px'}),
        html.P(v,style={'fontSize':'28px','fontWeight':'500','color':c,'margin':'0'}),
    ],style={'background':C['card'],'borderRadius':'12px','padding':'16px 20px',
        'border':f'0.5px solid {c}','flex':'1','minWidth':'130px'})

def get_staff_status(doctors,nurses,patients):
    busy_doc={p.doctor for p in patients if p.doctor!='Unassigned'}
    busy_nur={p.nurse  for p in patients if p.nurse !='Unassigned'}
    doc_pts={}; nur_pts={}
    for p in patients:
        if p.doctor!='Unassigned': doc_pts.setdefault(p.doctor,[]).append(p.name)
        if p.nurse !='Unassigned': nur_pts.setdefault(p.nurse, []).append(p.name)
    for d in doctors:
        d._busy=d.name in busy_doc
        d._pts =doc_pts.get(d.name,[])
    for n in nurses:
        n._busy=n.name in busy_nur
        n._pts =nur_pts.get(n.name,[])
    return doctors,nurses

def prow(p,role,C):
    now=datetime.now()
    wait=int((now-p.checkin).total_seconds()/60)
    row_bg=C['row_ready'] if p.nurse_done else (C['row_alert'] if wait>60 else C['card'])
    can_nurse=role in ['admin','nurse']
    can_rec  =role in ['admin','receptionist']

    if p.nurse_done and p.reception_done:
        disc=html.Span("✓ Discharged",style={'fontSize':'11px','color':C['green'],'fontWeight':'600'})
    elif p.nurse_done:
        disc=html.Div([
            html.Span("✅ Nurse done",style={'fontSize':'11px','color':C['teal'],'marginRight':'8px'}),
            html.Button("🏠 Confirm Discharge",
                id={'type':'rec-btn','index':p.id},n_clicks=0,
                style={'fontSize':'11px','padding':'4px 12px','borderRadius':'6px',
                    'border':f'1px solid {C["purple"]}',
                    'background':C["purple"]+'33' if can_rec else 'transparent',
                    'color':C['purple'] if can_rec else '#555',
                    'cursor':'pointer' if can_rec else 'default',
                    'fontFamily':'system-ui','fontWeight':'600',
                    'opacity':'1' if can_rec else '0.4'})
        ],style={'display':'flex','alignItems':'center','gap':'6px'})
    else:
        q_tag=html.Span(f"⏳#{p.queue_number} ",style={
            'fontSize':'10px','color':C['amber'],'fontWeight':'600'}) if p.queue_number else html.Span()
        disc=html.Div([
            q_tag,
            html.Button("✅ Nurse Done",
                id={'type':'nurse-btn','index':p.id},n_clicks=0,
                style={'fontSize':'11px','padding':'4px 12px','borderRadius':'6px',
                    'border':f'1px solid {C["teal"]}',
                    'background':C["teal"]+'33' if can_nurse else 'transparent',
                    'color':C['teal'] if can_nurse else '#555',
                    'cursor':'pointer' if can_nurse else 'default',
                    'fontFamily':'system-ui','fontWeight':'600',
                    'opacity':'1' if can_nurse else '0.4'}),
            html.Span(" Step 1/2",style={'fontSize':'10px','color':C['muted'],'marginLeft':'6px'}),
        ],style={'display':'flex','alignItems':'center'})

    return html.Tr([
        html.Td(p.name, style={'padding':'10px 12px','fontWeight':'600','fontSize':'13px','color':C['text']}),
        html.Td(p.room, style={'padding':'10px 12px','fontSize':'13px','color':C['muted']}),
        html.Td(sev_badge(p.severity),style={'padding':'10px 12px'}),
        html.Td(trow(brooch=p.brooch,wifi=p.wifi,camera=p.camera),style={'padding':'10px 12px'}),
        html.Td(lv_badge(p.last_visit,p.severity,C),style={'padding':'10px 12px'}),
        html.Td(html.Span(f"{wait}m",style={'color':C['red'] if wait>60 else C['teal'],'fontSize':'13px'}),style={'padding':'10px 12px'}),
        html.Td(p.nurse, style={'padding':'10px 12px','fontSize':'13px','color':C['text']}),
        html.Td(html.Span(p.doctor,style={'color':C['red'] if p.doctor=='Unassigned' else C['text'],'fontSize':'13px'}),style={'padding':'10px 12px'}),
        html.Td(disc,style={'padding':'8px 12px'}),
    ],style={'borderBottom':f'0.5px solid {C["border"]}','background':row_bg})

def ptable(rows,C):
    return html.Table([
        html.Thead(html.Tr([html.Th(c,style={'textAlign':'left','fontSize':'12px',
            'color':C['muted'],'fontWeight':'500','padding':'8px 12px',
            'borderBottom':f'0.5px solid {C["border"]}'})
            for c in ['Patient','Room','Severity','Tracking','Last Visit','Waiting','Nurse','Doctor','Discharge']])),
        html.Tbody(rows)
    ],style={'width':'100%','borderCollapse':'collapse'})

def get_db():
    d=Staff.query.filter_by(role='doctor').all()
    n=Staff.query.filter_by(role='nurse').all()
    p=Patient.query.filter_by(discharged=False).all()
    return d,n,p

# ── FIXED: One layout, all IDs always present, interval fires immediately ──
app.layout = html.Div([
    dcc.Location(id='url',refresh=False),
    dcc.Store(id='theme-store',data='light'),
    dcc.Store(id='role-store', data=''),
    dcc.Store(id='user-store', data=''),
    dcc.Interval(id='interval',interval=2000,n_intervals=0),
    html.Div(id='sound-trigger'),
    html.P(id='footer-time',style={'fontSize':'12px','color':'#a0a0c0','margin':'12px 0 0','textAlign':'center'}),
    html.Div(id='page-content'),
    # All dynamic IDs always present
    html.Div(id='stat-cards',      style={'display':'none'}),
    html.Div(id='alert-banner',    style={'display':'none'}),
    html.Div(id='patient-table-body', style={'display':'none'}),
    html.Div(id='doctor-panel',    style={'display':'none'}),
    html.Div(id='nurse-panel',     style={'display':'none'}),
    html.Div(id='bed-panel',       style={'display':'none'}),
    html.Div(id='waitlist-info',   style={'display':'none'}),
    html.Div(id='history-panel',   style={'display':'none'}),
    html.Div(id='my-nurses-panel', style={'display':'none'}),
    html.Div(id='free-nurses-panel',style={'display':'none'}),
    html.Div(id='nurse-signals',   style={'display':'none'}),
    html.Div(id='admit-msg',       style={'display':'none'}),
])

def build_page(C,is_dark,role,username,doctors,nurses,patients):
    fig_stay,fig_sev=make_charts(C)
    doctors,nurses=get_staff_status(doctors,nurses,patients)
    is_rec   = role in ['receptionist','admin']
    is_doc   = role == 'doctor'
    is_nurse = role == 'nurse'

    # admit form
    admit_section=cbox(C,[
        html.H3("➕ Admit New Patient",style={'fontSize':'15px','fontWeight':'500','color':C['text'],'margin':'0 0 12px'}),
        html.Div([
            dcc.Input(id='inp-name',placeholder='Patient name',debounce=False,style={**inp_s(C),'width':'130px'}),
            dcc.Dropdown(id='inp-room',options=[{'label':r,'value':r} for r in ALL_ROOMS],
                placeholder='Room',clearable=False,
                style={'width':'100px','fontSize':'12px','display':'inline-block','marginLeft':'8px','verticalAlign':'middle'}),
            dcc.Dropdown(id='inp-severity',options=[{'label':s,'value':s} for s in ['Extreme','Moderate','Minor']],
                placeholder='Severity',clearable=False,
                style={'width':'105px','fontSize':'12px','display':'inline-block','marginLeft':'8px','verticalAlign':'middle'}),
            dcc.Dropdown(id='inp-doctor',options=[{'label':d.name,'value':d.name} for d in doctors],
                placeholder='Doctor',clearable=True,
                style={'width':'130px','fontSize':'12px','display':'inline-block','marginLeft':'8px','verticalAlign':'middle'}),
            dcc.Dropdown(id='inp-nurse',options=[{'label':n.name,'value':n.name} for n in nurses],
                placeholder='Nurse',clearable=True,
                style={'width':'130px','fontSize':'12px','display':'inline-block','marginLeft':'8px','verticalAlign':'middle'}),
            html.Button("+ Admit",id='inp-admit-btn',n_clicks=0,
                style={'fontSize':'12px','padding':'8px 14px','borderRadius':'6px',
                    'border':f'0.5px solid {C["teal"]}','background':C['teal'],
                    'color':'#fff','cursor':'pointer','marginLeft':'8px','fontFamily':'system-ui','fontWeight':'600'}),
        ],style={'display':'flex','alignItems':'center','flexWrap':'wrap','gap':'4px'}),
    ]) if is_rec else html.Div()

    return html.Div(style={'fontFamily':'system-ui','background':C['bg'],'minHeight':'100vh','padding':'24px'},children=[
        header_bar(C,is_dark,role,username),
        # stat cards slot
        html.Div(id='stat-cards',style={'display':'flex','gap':'12px','flexWrap':'wrap','marginBottom':'24px'}),
        # alert
        html.Div(id='alert-banner'),
        # waitlist
        html.Div(id='waitlist-info',style={'marginBottom':'12px'}),
        # admit
        admit_section,
        # doctor panels
        html.Div([
            cbox(C,[html.H3("👩‍⚕️ Nurses on My Cases",style={'fontSize':'15px','fontWeight':'500','color':C['text'],'margin':'0 0 16px'}),
                html.Div(id='my-nurses-panel')],extra={'flex':'1','marginBottom':'0'}),
            cbox(C,[html.H3("✅ Free Nurses",style={'fontSize':'15px','fontWeight':'500','color':C['text'],'margin':'0 0 16px'}),
                html.Div(id='free-nurses-panel')],extra={'flex':'1','marginBottom':'0'}),
        ],style={'display':'flex','gap':'16px','marginBottom':'16px'}) if is_doc else html.Div(),
        # nurse badge
        cbox(C,[html.H3("📡 My Badge Signals",style={'fontSize':'15px','fontWeight':'500','color':C['text'],'margin':'0 0 12px'}),
            html.Div(id='nurse-signals')]) if is_nurse else html.Div(),
        # doctors + nurses + beds
        html.Div([
            cbox(C,[html.H3("👨‍⚕️ Doctors — Live",style={'fontSize':'15px','fontWeight':'500','color':C['text'],'margin':'0 0 16px'}),
                html.Div(id='doctor-panel')],extra={'flex':'1','marginBottom':'0'}),
            cbox(C,[html.H3("👩‍⚕️ Nurses — Live",style={'fontSize':'15px','fontWeight':'500','color':C['text'],'margin':'0 0 16px'}),
                html.Div(id='nurse-panel')],extra={'flex':'1','marginBottom':'0'}),
            cbox(C,[html.H3("🛏️ Room / Bed Availability",style={'fontSize':'15px','fontWeight':'500','color':C['text'],'margin':'0 0 16px'}),
                html.Div(id='bed-panel')],extra={'flex':'0.8','marginBottom':'0'}),
        ],style={'display':'flex','gap':'16px','marginBottom':'16px'}) if is_rec else html.Div(),
        # patient table
        cbox(C,[
            html.H3("🛏️ "+("All Patients" if is_rec else "My Patients"),
                style={'fontSize':'15px','fontWeight':'500','color':C['text'],'margin':'0 0 16px'}),
            html.Div(id='patient-table-body'),
        ]),
        # charts
        html.Div([
            cbox(C,[dcc.Graph(figure=fig_stay,style={'height':'260px'},config={'displayModeBar':False})],extra={'flex':'2','marginBottom':'0'}),
            cbox(C,[dcc.Graph(figure=fig_sev, style={'height':'260px'},config={'displayModeBar':False})],extra={'flex':'1','marginBottom':'0'}),
        ],style={'display':'flex','gap':'16px','marginBottom':'16px'}) if is_rec else html.Div(),
        # history
        cbox(C,[
            html.H3("📋 Discharge History",style={'fontSize':'15px','fontWeight':'500','color':C['text'],'margin':'0 0 16px'}),
            html.Div(id='history-panel'),
        ]) if is_rec else html.Div(),
    ])

@app.callback(
    Output('page-content','children'),
    Output('role-store','data'),
    Output('user-store','data'),
    Input('url','pathname')
)
def display_page(pathname):
    try:
        if not current_user.is_authenticated:
            return html.Div([dcc.Location(href='/login',id='redirect')]),'',''
        role,username=current_user.role,current_user.name
        with server.app_context():
            d,n,p=get_db()
        return build_page(LIGHT,False,role,username,d,n,p),role,username
    except Exception as e:
        print(f"display_page error: {e}")
        return html.Div(f"Error: {e}",style={'color':'red','padding':'20px'}),'',''

@app.callback(
    Output('page-content','children',allow_duplicate=True),
    Output('theme-store','data'),
    Output('role-store','data',allow_duplicate=True),
    Output('user-store','data',allow_duplicate=True),
    Input('theme-toggle','n_clicks'),
    State('theme-store','data'),State('role-store','data'),State('user-store','data'),
    prevent_initial_call=True
)
def toggle_theme(n,cur,role,username):
    new='dark' if cur=='light' else 'light'
    C=DARK if new=='dark' else LIGHT
    with server.app_context():
        d,n2,p=get_db()
    return build_page(C,new=='dark',role,username,d,n2,p),new,role,username

@app.callback(
    Output('admit-msg','children'),
    Input('inp-admit-btn','n_clicks'),
    State('inp-name','value'),State('inp-room','value'),
    State('inp-severity','value'),State('inp-doctor','value'),State('inp-nurse','value'),
    prevent_initial_call=True
)
def admit_patient(n,name,room,severity,doctor,nurse):
    if not name or not room or not severity:
        return "⚠️ Fill name, room and severity"
    with server.app_context():
        active=Patient.query.filter_by(discharged=False).all()
        busy_doc={p.doctor for p in active if p.doctor!='Unassigned'}
        busy_nur={p.nurse  for p in active if p.nurse !='Unassigned'}
        free_docs=Staff.query.filter_by(role='doctor').filter(Staff.name.notin_(busy_doc)).all()
        free_nurs=Staff.query.filter_by(role='nurse').filter(Staff.name.notin_(busy_nur)).all()
        assigned_doc=doctor or (free_docs[0].name if free_docs else 'Unassigned')
        assigned_nur=nurse  or (free_nurs[0].name if free_nurs else 'Unassigned')
        queue_pos=None
        if assigned_doc=='Unassigned' or assigned_nur=='Unassigned':
            last=Queue.query.order_by(Queue.position.desc()).first()
            queue_pos=(last.position+1) if last else 1
        p=Patient(name=name,room=room,severity=severity,
                  checkin=datetime.now(),last_visit=datetime.now(),
                  doctor=assigned_doc,nurse=assigned_nur,queue_number=queue_pos)
        db.session.add(p)
        db.session.flush()
        if queue_pos:
            db.session.add(Queue(patient_id=p.id,position=queue_pos))
        db.session.commit()
    if queue_pos:
        return f"⏳ {name} in queue #{queue_pos} — no staff free"
    return f"✅ {name} admitted! Dr: {assigned_doc} · Nurse: {assigned_nur}"

@app.callback(
    Output('admit-msg','children',allow_duplicate=True),
    Input({'type':'nurse-btn','index':dash.ALL},'n_clicks'),
    State('role-store','data'),
    prevent_initial_call=True
)
def nurse_done(clicks,role):
    from dash import ctx
    if not ctx.triggered_id: return ""
    if not any(c and c>0 for c in clicks): return ""
    if role not in ['admin','nurse']: return "Not authorized"
    pid=ctx.triggered_id['index']
    with server.app_context():
        p=Patient.query.get(pid)
        if p and not p.nurse_done:
            p.nurse_done=True
            p.last_visit=datetime.now()
            db.session.commit()
    return ""

@app.callback(
    Output('admit-msg','children',allow_duplicate=True),
    Input({'type':'rec-btn','index':dash.ALL},'n_clicks'),
    State('role-store','data'),
    prevent_initial_call=True
)
def reception_done(clicks,role):
    from dash import ctx
    if not ctx.triggered_id: return ""
    if not any(c and c>0 for c in clicks): return ""
    if role not in ['admin','receptionist']: return "Not authorized"
    pid=ctx.triggered_id['index']
    with server.app_context():
        p=Patient.query.get(pid)
        if p and p.nurse_done and not p.reception_done:
            p.reception_done=True
            p.discharged=True
            p.checkout=datetime.now()
            db.session.add(PatientHistory(
                patient_name=p.name,room=p.room,severity=p.severity,
                doctor=p.doctor,nurse=p.nurse,
                checkin=p.checkin,checkout=p.checkout,
                queue_number=p.queue_number))
            # auto-assign queue
            active=Patient.query.filter_by(discharged=False).all()
            busy_doc={pt.doctor for pt in active if pt.doctor!='Unassigned'}
            busy_nur={pt.nurse  for pt in active if pt.nurse !='Unassigned'}
            queued=Queue.query.order_by(Queue.position).all()
            free_d=Staff.query.filter_by(role='doctor').filter(Staff.name.notin_(busy_doc)).all()
            free_n=Staff.query.filter_by(role='nurse').filter(Staff.name.notin_(busy_nur)).all()
            for q in queued:
                qp=Patient.query.get(q.patient_id)
                if not qp: db.session.delete(q); continue
                if free_d and qp.doctor=='Unassigned': qp.doctor=free_d.pop(0).name
                if free_n and qp.nurse =='Unassigned': qp.nurse =free_n.pop(0).name
                if qp.doctor!='Unassigned' and qp.nurse!='Unassigned':
                    qp.queue_number=None; db.session.delete(q)
            db.session.commit()
    return ""

@app.callback(
    Output('stat-cards',      'children'),
    Output('alert-banner',    'children'),
    Output('patient-table-body','children'),
    Output('doctor-panel',    'children'),
    Output('nurse-panel',     'children'),
    Output('bed-panel',       'children'),
    Output('waitlist-info',   'children'),
    Output('history-panel',   'children'),
    Output('my-nurses-panel', 'children'),
    Output('free-nurses-panel','children'),
    Output('nurse-signals',   'children'),
    Output('footer-time',     'children'),
    Output('sound-trigger',   'children'),
    Input('interval','n_intervals'),
    State('theme-store','data'),State('role-store','data'),State('user-store','data'),
)
def update_live(n,theme,role,username):
    C=DARK if theme=='dark' else LIGHT
    with server.app_context():
        try:
            rname=current_user.name if current_user.is_authenticated else username
            rrole=current_user.role if current_user.is_authenticated else role
        except:
            rname=username; rrole=role

        doctors=Staff.query.filter_by(role='doctor').all()
        nurses =Staff.query.filter_by(role='nurse').all()
        patients=Patient.query.filter_by(discharged=False).all()

        for s in doctors+nurses:
            if random.random()<0.05:
                s.ble   =random.choice(['Strong','Strong','Weak','Lost'])
                s.wifi  =random.choice(['Strong','Strong','Weak'])
                s.bt    =random.choice(['Strong','Weak','Lost'])
                s.camera=random.choice(['Active','Active','Active','Lost'])
        for p in patients:
            if random.random()<0.04:
                p.brooch=random.choice(['Strong','Strong','Weak'])
                p.wifi  =random.choice(['Strong','Strong','Weak'])
                p.camera=random.choice(['Active','Active','Active','Lost'])
        db.session.commit()

        doctors,nurses=get_staff_status(doctors,nurses,patients)

        if rrole=='nurse':   show_pts=[p for p in patients if p.nurse==rname]
        elif rrole=='doctor': show_pts=[p for p in patients if p.doctor==rname]
        else:                 show_pts=patients

        rows=[prow(p,rrole,C) for p in show_pts]
        ptbl=ptable(rows,C) if rows else html.P("No patients yet",style={'color':C['muted'],'fontSize':'13px'})

        # Doctor/Nurse panels
        doc_rows=[html.Div([
            html.Div([html.Span(d.name,style={'fontWeight':'600','fontSize':'13px','color':C['text']}),
                badge('Busy','#993C1D','#FAECE7') if d._busy else badge('Available','#0F6E56','#E1F5EE')]),
            html.Div([html.Span(d.location,style={'fontSize':'12px','color':C['muted']}),
                html.Span(f" · {', '.join(d._pts)}" if d._pts else " · Available",
                    style={'fontSize':'12px','color':C['coral'] if d._pts else C['teal'],'marginLeft':'6px'})],
                style={'marginTop':'4px'}),
            trow(ble=d.ble,wifi=d.wifi,bt=d.bt,camera=d.camera)
        ],style={'padding':'10px 0','borderBottom':f'0.5px solid {C["border"]}'}) for d in doctors]

        nur_rows=[html.Div([
            html.Div([html.Span(n.name,style={'fontWeight':'600','fontSize':'13px','color':C['text']}),
                badge('Busy','#993C1D','#FAECE7') if n._busy else badge('Free','#0F6E56','#E1F5EE')]),
            html.Div([html.Span(n.location,style={'fontSize':'12px','color':C['muted']}),
                html.Span(f" · {', '.join(n._pts)}" if n._pts else " · Free",
                    style={'fontSize':'12px','color':C['purple'] if n._pts else C['teal'],'marginLeft':'6px'})],
                style={'marginTop':'4px'}),
            trow(ble=n.ble,wifi=n.wifi,bt=n.bt,camera=n.camera)
        ],style={'padding':'10px 0','borderBottom':f'0.5px solid {C["border"]}'}) for n in nurses]

        # Bed panel
        occupied={p.room for p in patients}
        bed_rows=[html.Div([
            html.Span('🟢 ' if r not in occupied else '🔴 '),
            html.Span(r,style={'fontWeight':'500','fontSize':'13px','color':C['text']}),
            html.Span(' · FREE' if r not in occupied else ' · Occupied',
                style={'fontSize':'12px','color':C['teal'] if r not in occupied else C['red'],'marginLeft':'6px'}),
        ],style={'padding':'8px 0','borderBottom':f'0.5px solid {C["border"]}'}) for r in ALL_ROOMS]

        # Doctor-specific panels
        my_nurse_names=list({p.nurse for p in show_pts if p.nurse not in ['Unassigned',None]})
        my_nurses_panel=[html.Div([
            html.Span(n.name,style={'fontWeight':'600','fontSize':'13px','color':C['text']}),
            badge('Busy','#993C1D','#FAECE7'),
            html.Span(f" · {', '.join(n._pts)}",style={'fontSize':'12px','color':C['purple'],'marginLeft':'8px'}),
            trow(ble=n.ble,wifi=n.wifi,bt=n.bt,camera=n.camera)
        ],style={'padding':'10px 0','borderBottom':f'0.5px solid {C["border"]}'})
        for n in nurses if n.name in my_nurse_names] or [html.P("No nurses on your cases yet",style={'color':C['muted'],'fontSize':'13px'})]

        free_nurses=[n for n in nurses if not n._busy]
        free_nurses_panel=[html.Div([
            html.Span("🟢 "),
            html.Span(n.name,style={'fontWeight':'600','fontSize':'13px','color':C['text']}),
            html.Span(f" · {n.location}",style={'fontSize':'12px','color':C['muted'],'marginLeft':'8px'}),
            trow(ble=n.ble,wifi=n.wifi,bt=n.bt,camera=n.camera)
        ],style={'padding':'10px 0','borderBottom':f'0.5px solid {C["border"]}'})
        for n in free_nurses] or [html.P("No free nurses",style={'color':C['muted'],'fontSize':'13px'})]

        me=next((n for n in nurses if n.name==rname),None)
        nurse_sig=trow(ble=me.ble if me else 'Lost',wifi=me.wifi if me else 'Lost',
            bt=me.bt if me else 'Lost',camera=me.camera if me else 'Lost')

        # Alerts
        now=datetime.now()
        alerts=[]; play_sound=False
        for p in show_pts:
            lv=int((now-p.last_visit).total_seconds()/60)
            wt=int((now-p.checkin).total_seconds()/60)
            if p.severity=='Extreme' and lv>30:
                alerts.append(f"🚨 {p.name} ({p.room}) — no visit in {lv}m!"); play_sound=True
            elif wt>120:
                alerts.append(f"⚠️ {p.name} ({p.room}) — waiting {wt}m!"); play_sound=True

        alert_banner=html.Div()
        if alerts:
            alert_banner=html.Div([
                html.Span("🔔 ",style={'fontWeight':'700','color':'#A32D2D'}),
                *[html.Span(f"{a}  ",style={'fontSize':'12px','color':'#A32D2D'}) for a in alerts]
            ],style={'background':'#FCEBEB','border':'1px solid #F09595','borderRadius':'8px',
                'padding':'10px 16px','marginBottom':'16px','display':'flex','alignItems':'center','flexWrap':'wrap','gap':'8px'})

        sound=html.Div(id='_sound',**({'data-play':str(n)} if play_sound else {}),
            style={'display':'none'}) if play_sound else html.Div(style={'display':'none'})
        footer=f"✅ Silent Hospital OS | 318,438 real patients | {now.strftime('%I:%M:%S %p')}"

        # Stat cards
        busy_d=sum(1 for d in doctors if d._busy)
        free_d=sum(1 for d in doctors if not d._busy)
        busy_n=sum(1 for nu in nurses if nu._busy)
        free_n=sum(1 for nu in nurses if not nu._busy)
        waiting=sum(1 for p in show_pts if int((now-p.checkin).total_seconds()/60)>60)

        if rrole=='receptionist':
            scards=[scard("Total Patients",str(len(patients)),C['purple'],C),
                    scard("Doctors Busy",str(busy_d),C['coral'],C),
                    scard("Nurses Busy",str(busy_n),C['amber'],C),
                    scard("Doctors Free",str(free_d),C['teal'],C),
                    scard("Nurses Free",str(free_n),C['green'],C),
                    scard("Waiting >1hr",str(waiting),C['red'],C)]
        elif rrole=='doctor':
            scards=[scard("My Patients",str(len(show_pts)),C['purple'],C),
                    scard("Free Nurses",str(free_n),C['green'],C),
                    scard("Waiting >1hr",str(waiting),C['red'],C)]
        elif rrole=='nurse':
            done=sum(1 for p in show_pts if p.nurse_done)
            scards=[scard("My Patients",str(len(show_pts)),C['purple'],C),
                    scard("Care Complete",str(done),C['green'],C),
                    scard("Pending",str(len(show_pts)-done),C['amber'],C)]
        else:
            scards=[scard("Total Patients",str(len(patients)),C['purple'],C),
                    scard("Doctors Available",str(free_d),C['teal'],C),
                    scard("Nurses Free",str(free_n),C['green'],C),
                    scard("Waiting >1hr",str(waiting),C['red'],C),
                    scard("Model Accuracy","74.56%",C['purple'],C)]

        # Waitlist
        queued=Queue.query.order_by(Queue.position).all()
        wl_pts=[Patient.query.get(q.patient_id) for q in queued]
        wl_pts=[p for p in wl_pts if p]
        waitlist_div=html.Div([
            html.Span("⏳ Queue — waiting for staff: ",style={'fontSize':'12px','fontWeight':'600','color':C['amber']}),
            *[html.Span(f"#{i+1} {p.name}",style={'fontSize':'11px','padding':'2px 8px','borderRadius':'10px',
                'background':C['amber']+'22','color':C['amber'],'marginLeft':'6px','fontWeight':'500'})
              for i,p in enumerate(wl_pts)],
        ],style={'padding':'8px 12px','borderRadius':'8px',
            'border':f'1px solid {C["amber"]}','background':C['amber']+'11'}) if wl_pts else html.Div()

        # History
        history=PatientHistory.query.order_by(PatientHistory.id.desc()).limit(20).all()
        if history:
            hist_rows=[html.Tr([
                html.Td(h.patient_name,style={'padding':'8px 12px','fontSize':'12px','color':C['text'],'fontWeight':'600'}),
                html.Td(h.room or '-',  style={'padding':'8px 12px','fontSize':'12px','color':C['muted']}),
                html.Td(h.severity or '-',style={'padding':'8px 12px','fontSize':'12px','color':C['muted']}),
                html.Td(h.doctor or '-', style={'padding':'8px 12px','fontSize':'12px','color':C['teal']}),
                html.Td(h.nurse  or '-', style={'padding':'8px 12px','fontSize':'12px','color':C['purple']}),
                html.Td(h.checkin.strftime('%d %b %H:%M')  if h.checkin  else '-',style={'padding':'8px 12px','fontSize':'11px','color':C['muted']}),
                html.Td(h.checkout.strftime('%d %b %H:%M') if h.checkout else '-',style={'padding':'8px 12px','fontSize':'11px','color':C['muted']}),
            ],style={'borderBottom':f'0.5px solid {C["border"]}'}) for h in history]
            hist_table=html.Table([
                html.Thead(html.Tr([html.Th(c,style={'textAlign':'left','fontSize':'11px','color':C['muted'],
                    'fontWeight':'500','padding':'8px 12px','borderBottom':f'0.5px solid {C["border"]}'})
                    for c in ['Patient','Room','Severity','Doctor','Nurse','Check-in','Check-out']])),
                html.Tbody(hist_rows)
            ],style={'width':'100%','borderCollapse':'collapse'})
        else:
            hist_table=html.P("No discharge history yet",style={'color':C['muted'],'fontSize':'13px'})

    return (scards,alert_banner,ptbl,doc_rows,nur_rows,bed_rows,
            waitlist_div,hist_table,my_nurses_panel,free_nurses_panel,nurse_sig,footer,sound)

app.clientside_callback(
    """function(c){if(c&&c.props&&c.props['data-play']){try{var x=new(window.AudioContext||window.webkitAudioContext)();var o=x.createOscillator();var g=x.createGain();o.connect(g);g.connect(x.destination);o.type='sine';o.frequency.setValueAtTime(880,x.currentTime);g.gain.setValueAtTime(0.2,x.currentTime);g.gain.exponentialRampToValueAtTime(0.001,x.currentTime+0.6);o.start(x.currentTime);o.stop(x.currentTime+0.6);}catch(e){}}return '';}""",
    Output('sound-trigger','title'),Input('sound-trigger','children'),
)

@server.route('/dashboard')
@login_required
def dashboard_view(): return redirect('/')

if __name__=='__main__':
    port=int(os.environ.get('PORT',8050))
    app.run(host='0.0.0.0',port=port,debug=False,dev_tools_ui=False)
