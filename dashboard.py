import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('healthcare/train_data.csv')
df.dropna(inplace=True)

now = datetime.now()

doctors = [
    {'name': 'Dr. Smith',  'location': 'ICU',      'status': 'Busy',      'free_in': 20,
     'ble': 'Strong', 'wifi': 'Strong', 'bt': 'Strong', 'camera': 'Active'},
    {'name': 'Dr. Patel',  'location': 'Room 2',   'status': 'Available', 'free_in': 0,
     'ble': 'Strong', 'wifi': 'Strong', 'bt': 'Weak',   'camera': 'Active'},
    {'name': 'Dr. Aisha',  'location': 'Corridor', 'status': 'Available', 'free_in': 0,
     'ble': 'Lost',   'wifi': 'Weak',   'bt': 'Strong', 'camera': 'Active'},
    {'name': 'Dr. James',  'location': 'Ward A',   'status': 'Busy',      'free_in': 45,
     'ble': 'Strong', 'wifi': 'Weak',   'bt': 'Strong', 'camera': 'Active'},
]

nurses = [
    {'name': 'Nurse Priya',  'location': 'Ward A',    'status': 'Free',     'patient': 'Mr. James',
     'ble': 'Strong', 'wifi': 'Strong', 'bt': 'Strong', 'camera': 'Active'},
    {'name': 'Nurse Aisha',  'location': 'ICU',       'status': 'Busy',     'patient': 'Mr. Ahmed',
     'ble': 'Strong', 'wifi': 'Strong', 'bt': 'Strong', 'camera': 'Active'},
    {'name': 'Nurse Rachel', 'location': 'Room 3',    'status': 'Free',     'patient': 'Ms. Sara',
     'ble': 'Weak',   'wifi': 'Strong', 'bt': 'Weak',   'camera': 'Active'},
    {'name': 'Nurse Sandra', 'location': 'Ward B',    'status': 'Busy',     'patient': 'Mrs. Patel',
     'ble': 'Lost',   'wifi': 'Weak',   'bt': 'Lost',   'camera': 'Active'},
    {'name': 'Nurse Meena',  'location': 'Reception', 'status': 'On Break', 'patient': None,
     'ble': 'Lost',   'wifi': 'Lost',   'bt': 'Lost',   'camera': 'Lost'},
]

initial_patients = [
    {'name': 'Mr. Ahmed',  'room': 'ICU',    'severity': 'Extreme',
     'checkin': (now - timedelta(minutes=5)).isoformat(),
     'last_visit': (now - timedelta(minutes=3)).isoformat(),
     'nurse': 'Nurse Aisha',  'doctor': 'Dr. Smith',
     'doc_ready': False, 'family_signed': False, 'reception_done': False,
     'brooch': 'Strong', 'wifi': 'Strong', 'camera': 'Active'},
    {'name': 'Mrs. Patel', 'room': 'Ward A', 'severity': 'Moderate',
     'checkin': (now - timedelta(minutes=95)).isoformat(),
     'last_visit': (now - timedelta(minutes=80)).isoformat(),
     'nurse': 'Nurse Sandra', 'doctor': 'Unassigned',
     'doc_ready': False, 'family_signed': False, 'reception_done': False,
     'brooch': 'Weak',   'wifi': 'Strong', 'camera': 'Active'},
    {'name': 'Mr. James',  'room': 'Room 3', 'severity': 'Minor',
     'checkin': (now - timedelta(minutes=20)).isoformat(),
     'last_visit': (now - timedelta(minutes=15)).isoformat(),
     'nurse': 'Nurse Priya',  'doctor': 'Dr. James',
     'doc_ready': False, 'family_signed': False, 'reception_done': False,
     'brooch': 'Strong', 'wifi': 'Strong', 'camera': 'Active'},
    {'name': 'Ms. Sara',   'room': 'Room 1', 'severity': 'Extreme',
     'checkin': (now - timedelta(minutes=130)).isoformat(),
     'last_visit': (now - timedelta(minutes=120)).isoformat(),
     'nurse': 'Nurse Rachel', 'doctor': 'Unassigned',
     'doc_ready': False, 'family_signed': False, 'reception_done': False,
     'brooch': 'Lost',   'wifi': 'Weak',   'camera': 'Active'},
    {'name': 'Mr. Khan',   'room': 'Ward B', 'severity': 'Moderate',
     'checkin': (now - timedelta(minutes=40)).isoformat(),
     'last_visit': (now - timedelta(minutes=35)).isoformat(),
     'nurse': 'Assigned',     'doctor': 'Unassigned',
     'doc_ready': False, 'family_signed': False, 'reception_done': False,
     'brooch': 'Strong', 'wifi': 'Strong', 'camera': 'Active'},
]

beds = [
    {'room': 'ICU',    'status': 'Occupied', 'free_in': 180},
    {'room': 'Ward A', 'status': 'Occupied', 'free_in': 105},
    {'room': 'Room 3', 'status': 'Occupied', 'free_in': 90},
    {'room': 'Room 1', 'status': 'Occupied', 'free_in': 300},
    {'room': 'Ward B', 'status': 'Free',     'free_in': 0},
    {'room': 'Room 2', 'status': 'Free',     'free_in': 0},
]

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Silent Hospital OS"

LIGHT = {
    'bg': '#F9F8FF', 'card': '#FFFFFF', 'border': '#EEEDFE',
    'text': '#1a1a2e', 'muted': '#6a6a8a',
    'purple': '#534AB7', 'teal': '#1D9E75', 'coral': '#D85A30',
    'amber': '#BA7517', 'red': '#E24B4A', 'green': '#639922',
    'row_alert': '#FFF5F5', 'row_ready': '#F0FFF8',
    'btn_bg': 'transparent', 'btn_border': '#534AB7', 'btn_text': '#534AB7',
    'input_bg': '#FFFFFF', 'input_text': '#1a1a2e', 'input_border': '#CECBF6',
}

DARK = {
    'bg': '#0d0d1a', 'card': '#16162a', 'border': '#2a2a4a',
    'text': '#e8e8ff', 'muted': '#a0a0c0',
    'purple': '#9d97e8', 'teal': '#5DCAA5', 'coral': '#F0997B',
    'amber': '#EF9F27', 'red': '#F09595', 'green': '#97C459',
    'row_alert': '#2a1a1a', 'row_ready': '#0a2a1a',
    'btn_bg': '#16162a', 'btn_border': '#9d97e8', 'btn_text': '#9d97e8',
    'input_bg': '#0d0d1a', 'input_text': '#e8e8ff', 'input_border': '#2a2a4a',
}

stay_counts = df['Stay'].value_counts().reset_index()
stay_counts.columns = ['Stay', 'Count']
stay_order = ['0-10','11-20','21-30','31-40','41-50',
              '51-60','61-70','71-80','81-90','91-100','More than 100 Days']
stay_counts['Stay'] = pd.Categorical(stay_counts['Stay'], categories=stay_order, ordered=True)
stay_counts = stay_counts.sort_values('Stay')

def make_charts(C):
    fig_stay = px.bar(stay_counts, x='Stay', y='Count', color='Count',
        color_continuous_scale=['#EEEDFE', C['purple']],
        title='Real Patient Stay Distribution (318,438 patients)')
    fig_stay.update_layout(plot_bgcolor=C['card'], paper_bgcolor=C['card'],
        font_color=C['text'], showlegend=False,
        margin=dict(t=40, b=20, l=20, r=20), coloraxis_showscale=False)
    sev_counts = df['Severity of Illness'].value_counts()
    fig_sev = px.pie(values=sev_counts.values, names=sev_counts.index,
        color_discrete_sequence=[C['coral'], C['amber'], C['teal']],
        title='Severity of Illness Breakdown')
    fig_sev.update_layout(plot_bgcolor=C['card'], paper_bgcolor=C['card'],
        font_color=C['text'], margin=dict(t=40, b=20, l=20, r=20))
    return fig_stay, fig_sev

def badge(text, color, bg):
    return html.Span(text, style={'fontSize': '11px', 'fontWeight': '500',
        'padding': '3px 10px', 'borderRadius': '20px',
        'background': bg, 'color': color, 'marginLeft': '8px'})

def status_badge(status):
    if status == 'Busy': return badge(status, '#993C1D', '#FAECE7')
    elif status in ['Available','Free']: return badge(status, '#0F6E56', '#E1F5EE')
    else: return badge(status, '#854F0B', '#FAEEDA')

def severity_badge(sev):
    if sev == 'Extreme': return badge(sev, '#A32D2D', '#FCEBEB')
    elif sev == 'Moderate': return badge(sev, '#854F0B', '#FAEEDA')
    else: return badge(sev, '#0F6E56', '#E1F5EE')

def sig_pill(label, signal):
    if signal == 'Lost':
        return html.Span(f"✕ {label}", style={
            'fontSize': '9px', 'padding': '1px 5px', 'borderRadius': '3px',
            'background': '#FCEBEB', 'color': '#A32D2D', 'marginRight': '3px'})
    dot   = '●' if signal == 'Strong' else '◐'
    color = '#0F6E56' if signal == 'Strong' else '#854F0B'
    bg    = '#E1F5EE' if signal == 'Strong' else '#FAEEDA'
    return html.Span(f"{dot} {label}", style={
        'fontSize': '9px', 'padding': '1px 5px', 'borderRadius': '3px',
        'background': bg, 'color': color, 'marginRight': '3px'})

def tracking_row(ble=None, wifi=None, bt=None, brooch=None, camera=None):
    pills = []
    if ble    is not None: pills.append(sig_pill('BLE',    ble))
    if brooch is not None: pills.append(sig_pill('Brooch', brooch))
    if wifi   is not None: pills.append(sig_pill('WiFi',   wifi))
    if bt     is not None: pills.append(sig_pill('BT',     bt))
    if camera is not None: pills.append(sig_pill('Camera', camera))
    return html.Div(pills, style={'display': 'flex', 'flexWrap': 'wrap',
        'marginTop': '4px', 'gap': '2px'})

def last_visit_badge(last_visit_iso, severity, C):
    lv   = datetime.fromisoformat(last_visit_iso)
    mins = int((datetime.now() - lv).total_seconds() / 60)
    if severity == 'Extreme' and mins > 30:
        color, bg, icon = '#A32D2D', '#FCEBEB', '🚨'
    elif severity == 'Moderate' and mins > 60:
        color, bg, icon = '#854F0B', '#FAEEDA', '⚠️'
    elif mins > 120:
        color, bg, icon = '#854F0B', '#FAEEDA', '⚠️'
    else:
        color, bg, icon = '#0F6E56', '#E1F5EE', '✓'
    if mins < 60:
        label = f"{icon} {mins}m ago"
    else:
        label = f"{icon} {mins//60}h {mins%60}m ago"
    return html.Span(label, style={
        'fontSize': '10px', 'padding': '2px 7px',
        'borderRadius': '4px', 'background': bg, 'color': color,
        'fontWeight': '500'})

def discharge_btn(label, symbol, id_type, idx, done, enabled, active_color):
    if not enabled:
        color, bg, border = '#555555', 'transparent', '#555555'
    elif done:
        color, bg, border = active_color, f'{active_color}22', active_color
    else:
        color, bg, border = active_color, 'transparent', active_color
    return html.Button(f"{symbol} {label}",
        id={'type': id_type, 'index': idx},
        n_clicks=1 if done else 0,
        style={'fontSize': '11px', 'padding': '4px 10px',
            'borderRadius': '6px', 'border': f'1px solid {border}',
            'background': bg, 'color': color, 'cursor': 'pointer',
            'fontFamily': 'system-ui, sans-serif', 'fontWeight': '500',
            'marginRight': '4px', 'transition': 'all 0.2s'})

def input_style(C):
    return {'fontSize': '12px', 'padding': '6px 10px', 'borderRadius': '6px',
        'border': f'0.5px solid {C["input_border"]}',
        'background': C['input_bg'], 'color': C['input_text'],
        'fontFamily': 'system-ui, sans-serif', 'outline': 'none'}

SOUND_JS = """
function playAlert() {
    try {
        var ctx = new (window.AudioContext || window.webkitAudioContext)();
        var oscillator = ctx.createOscillator();
        var gainNode = ctx.createGain();
        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(880, ctx.currentTime);
        gainNode.gain.setValueAtTime(0.3, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.8);
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + 0.8);
    } catch(e) {}
}
"""

def build_layout(C, is_dark):
    fig_stay, fig_sev = make_charts(C)
    return html.Div(style={
        'fontFamily': 'system-ui, sans-serif',
        'background': C['bg'], 'minHeight': '100vh',
        'padding': '24px', 'transition': 'all 0.3s'
    }, children=[

        html.Script(SOUND_JS),

        html.Div([
            html.Div([
                html.H1("🏥 Silent Hospital OS", style={
                    'fontSize': '24px', 'fontWeight': '500',
                    'color': C['purple'], 'margin': '0'}),
                html.P("Zero interaction. Just works.", style={
                    'fontSize': '13px', 'color': C['muted'], 'margin': '4px 0 0'}),
            ]),
            html.Button(
                "☀️  Light Mode" if is_dark else "🌙  Dark Mode",
                id='theme-toggle', n_clicks=1 if is_dark else 0,
                style={'fontSize': '12px', 'padding': '8px 18px',
                    'borderRadius': '20px',
                    'border': f'0.5px solid {C["btn_border"]}',
                    'background': C['btn_bg'], 'color': C['btn_text'],
                    'cursor': 'pointer', 'fontFamily': 'system-ui, sans-serif'})
        ], style={'display': 'flex', 'justifyContent': 'space-between',
            'alignItems': 'center', 'marginBottom': '24px'}),

        html.Div(id='alert-banner'),

        html.Div(id='stat-cards', style={
            'display': 'flex', 'gap': '12px',
            'flexWrap': 'wrap', 'marginBottom': '24px'}),

        html.Div([
            html.Div([
                html.Div([
                    html.H3("👨‍⚕️ Doctor Availability", style={
                        'fontSize': '15px', 'fontWeight': '500',
                        'margin': '0', 'color': C['text'], 'display': 'inline-block'}),
                    html.Span(" — BLE · WiFi · BT · Camera", style={
                        'fontSize': '11px', 'color': C['muted'], 'marginLeft': '8px'}),
                ], style={'marginBottom': '16px'}),
                html.Div(id='doctor-panel'),
            ], style={'background': C['card'], 'borderRadius': '12px',
                'padding': '20px', 'border': f'0.5px solid {C["border"]}', 'flex': '1'}),

            html.Div([
                html.Div([
                    html.H3("👩‍⚕️ Nurse Assignment", style={
                        'fontSize': '15px', 'fontWeight': '500',
                        'margin': '0', 'color': C['text'], 'display': 'inline-block'}),
                    html.Span(" — BLE · WiFi · BT · Camera", style={
                        'fontSize': '11px', 'color': C['muted'], 'marginLeft': '8px'}),
                ], style={'marginBottom': '16px'}),
                html.Div(id='nurse-panel'),
            ], style={'background': C['card'], 'borderRadius': '12px',
                'padding': '20px', 'border': f'0.5px solid {C["border"]}', 'flex': '1'}),
        ], style={'display': 'flex', 'gap': '16px', 'marginBottom': '16px'}),

        html.Div([
            html.Div([
                html.H3("🛏️ Patient Status — Live", style={
                    'fontSize': '15px', 'fontWeight': '500',
                    'margin': '0', 'color': C['text'], 'display': 'inline-block'}),
                html.Span(" — Brooch · WiFi · Camera | Receptionist: Add new patient", style={
                    'fontSize': '11px', 'color': C['muted'], 'marginLeft': '8px'}),
            ], style={'marginBottom': '12px'}),

            html.Div([
                dcc.Input(id='inp-name', placeholder='Patient name', debounce=False,
                    style={**input_style(C), 'width': '150px'}),
                dcc.Input(id='inp-room', placeholder='Room', debounce=False,
                    style={**input_style(C), 'width': '80px', 'marginLeft': '8px'}),
                dcc.Dropdown(id='inp-severity',
                    options=[{'label': s, 'value': s} for s in ['Extreme','Moderate','Minor']],
                    placeholder='Severity', clearable=False,
                    style={'width': '120px', 'fontSize': '12px',
                        'display': 'inline-block', 'marginLeft': '8px',
                        'verticalAlign': 'middle'}),
                html.Button("+ Admit Patient", id='admit-btn', n_clicks=0, style={
                    'fontSize': '12px', 'padding': '6px 14px', 'borderRadius': '6px',
                    'border': f'0.5px solid {C["teal"]}',
                    'background': C["teal"], 'color': '#ffffff',
                    'cursor': 'pointer', 'marginLeft': '8px',
                    'fontFamily': 'system-ui, sans-serif', 'fontWeight': '500'}),
                html.Span(id='admit-msg', style={
                    'fontSize': '11px', 'color': C['teal'], 'marginLeft': '8px'}),
            ], style={'display': 'flex', 'alignItems': 'center',
                'flexWrap': 'wrap', 'gap': '4px', 'marginBottom': '12px'}),

            html.Div([
                html.Span("Discharge: ", style={'fontSize': '11px', 'color': C['muted']}),
                html.Span("✅ Doctor", style={'fontSize': '11px', 'color': C['teal'], 'marginLeft': '4px'}),
                html.Span(" → 📋 Family", style={'fontSize': '11px', 'color': C['amber']}),
                html.Span(" → 🏠 Reception", style={'fontSize': '11px', 'color': C['purple']}),
                html.Span(" → Patient discharged", style={'fontSize': '11px', 'color': C['green']}),
            ], style={'marginBottom': '10px'}),

            html.Table([
                html.Thead(html.Tr([
                    html.Th(c, style={
                        'textAlign': 'left', 'fontSize': '12px',
                        'color': C['muted'], 'fontWeight': '500',
                        'padding': '8px 12px',
                        'borderBottom': f'0.5px solid {C["border"]}'
                    }) for c in ['Patient','Room','Severity','Tracking','Last Visit','Waiting','Nurse','Doctor','Discharge']
                ])),
                html.Tbody(id='patient-table-body'),
            ], style={'width': '100%', 'borderCollapse': 'collapse'})
        ], style={'background': C['card'], 'borderRadius': '12px',
            'padding': '20px', 'border': f'0.5px solid {C["border"]}', 'marginBottom': '16px'}),

        html.Div([
            html.Div([
                html.H3("🛏️ Bed Management", style={
                    'fontSize': '15px', 'fontWeight': '500',
                    'margin': '0 0 16px', 'color': C['text']}),
                *[html.Div([
                    html.Span(b['room'], style={'fontWeight': '500', 'fontSize': '13px', 'color': C['text']}),
                    html.Span(
                        " · FREE NOW" if b['status'] == 'Free' else f" · Free in {b['free_in']} mins",
                        style={'fontSize': '12px',
                            'color': C['teal'] if b['status'] == 'Free' else C['amber']}),
                    html.Span("●", style={'float': 'right',
                        'color': C['teal'] if b['status'] == 'Free' else C['coral']})
                ], style={'padding': '10px 0',
                    'borderBottom': f'0.5px solid {C["border"]}',
                    'fontSize': '13px'}) for b in beds]
            ], style={'background': C['card'], 'borderRadius': '12px',
                'padding': '20px', 'border': f'0.5px solid {C["border"]}', 'flex': '1.2'}),

            html.Div([
                dcc.Graph(figure=fig_stay, style={'height': '280px'}, config={'displayModeBar': False})
            ], style={'background': C['card'], 'borderRadius': '12px',
                'padding': '20px', 'border': f'0.5px solid {C["border"]}', 'flex': '2'}),

            html.Div([
                dcc.Graph(figure=fig_sev, style={'height': '280px'}, config={'displayModeBar': False})
            ], style={'background': C['card'], 'borderRadius': '12px',
                'padding': '20px', 'border': f'0.5px solid {C["border"]}', 'flex': '1.2'}),
        ], style={'display': 'flex', 'gap': '16px', 'marginBottom': '16px'}),

        dcc.Interval(id='interval', interval=2000, n_intervals=0),
        dcc.Store(id='theme-store', data='light'),
        dcc.Store(id='patients-store', data=initial_patients),
        dcc.Store(id='alert-store', data=0),

        html.Div(id='sound-trigger'),

        html.Div([
            html.P(id='footer-time', style={
                'fontSize': '12px', 'color': C['muted'],
                'margin': '0', 'textAlign': 'center'})
        ])
    ])

app.layout = html.Div([
    html.Div(id='page-content', children=build_layout(LIGHT, False)),
])

@app.callback(
    Output('page-content', 'children'),
    Output('theme-store', 'data'),
    Input('theme-toggle', 'n_clicks'),
    State('theme-store', 'data'),
    prevent_initial_call=True
)
def toggle_theme(n, current_theme):
    if current_theme == 'light':
        return build_layout(DARK, True), 'dark'
    return build_layout(LIGHT, False), 'light'

@app.callback(
    Output('patients-store', 'data'),
    Output('admit-msg', 'children'),
    Input('admit-btn', 'n_clicks'),
    State('inp-name', 'value'),
    State('inp-room', 'value'),
    State('inp-severity', 'value'),
    State('patients-store', 'data'),
    prevent_initial_call=True
)
def admit_patient(n, name, room, severity, pts):
    if not name or not room or not severity:
        return pts, "⚠️ Fill all fields"
    pts.append({
        'name': name, 'room': room, 'severity': severity,
        'checkin': datetime.now().isoformat(),
        'last_visit': datetime.now().isoformat(),
        'nurse': 'Unassigned', 'doctor': 'Unassigned',
        'doc_ready': False, 'family_signed': False, 'reception_done': False,
        'brooch': 'Strong', 'wifi': 'Strong', 'camera': 'Active'
    })
    return pts, f"✅ {name} admitted!"

@app.callback(
    Output('patients-store', 'data', allow_duplicate=True),
    Input({'type': 'doc-btn', 'index': dash.ALL}, 'n_clicks'),
    State('patients-store', 'data'),
    prevent_initial_call=True
)
def doctor_approve(n_clicks, pts):
    from dash import ctx
    if not ctx.triggered_id: return pts
    idx = ctx.triggered_id['index']
    if idx < len(pts):
        pts[idx]['doc_ready'] = True
        pts[idx]['last_visit'] = datetime.now().isoformat()
    return pts

@app.callback(
    Output('patients-store', 'data', allow_duplicate=True),
    Input({'type': 'family-btn', 'index': dash.ALL}, 'n_clicks'),
    State('patients-store', 'data'),
    prevent_initial_call=True
)
def family_sign(n_clicks, pts):
    from dash import ctx
    if not ctx.triggered_id: return pts
    idx = ctx.triggered_id['index']
    if idx < len(pts) and pts[idx]['doc_ready']:
        pts[idx]['family_signed'] = True
    return pts

@app.callback(
    Output('patients-store', 'data', allow_duplicate=True),
    Input({'type': 'reception-btn', 'index': dash.ALL}, 'n_clicks'),
    State('patients-store', 'data'),
    prevent_initial_call=True
)
def reception_confirm(n_clicks, pts):
    from dash import ctx
    if not ctx.triggered_id: return pts
    idx = ctx.triggered_id['index']
    if idx < len(pts) and pts[idx]['doc_ready'] and pts[idx]['family_signed']:
        pts[idx]['reception_done'] = True
    pts = [p for p in pts if not (p['doc_ready'] and p['family_signed'] and p['reception_done'])]
    return pts

@app.callback(
    Output('footer-time', 'children'),
    Output('patient-table-body', 'children'),
    Output('stat-cards', 'children'),
    Output('doctor-panel', 'children'),
    Output('nurse-panel', 'children'),
    Output('alert-banner', 'children'),
    Output('sound-trigger', 'children'),
    Input('interval', 'n_intervals'),
    State('theme-store', 'data'),
    State('patients-store', 'data'),
)
def update_live(n, theme, pts):
    C = DARK if theme == 'dark' else LIGHT
    current = datetime.now().strftime('%I:%M:%S %p')
    footer = f"✅ Silent Hospital OS — Running live | Model trained on 318,438 real patients | Last updated: {current}"

    for d in doctors:
        if random.random() < 0.05:
            d['ble']    = random.choice(['Strong','Strong','Weak','Lost'])
            d['wifi']   = random.choice(['Strong','Strong','Weak'])
            d['bt']     = random.choice(['Strong','Weak','Lost'])
            d['camera'] = random.choice(['Active','Active','Active','Lost'])

    for nu in nurses:
        if random.random() < 0.05:
            nu['ble']    = random.choice(['Strong','Strong','Weak','Lost'])
            nu['wifi']   = random.choice(['Strong','Strong','Weak'])
            nu['bt']     = random.choice(['Strong','Weak','Lost'])
            nu['camera'] = random.choice(['Active','Active','Active','Lost'])

    for p in pts:
        if random.random() < 0.04:
            p['brooch'] = random.choice(['Strong','Strong','Weak'])
            p['wifi']   = random.choice(['Strong','Strong','Weak'])
            p['camera'] = random.choice(['Active','Active','Active','Lost'])

    doctor_rows = [html.Div([
        html.Div([
            html.Span(d['name'], style={'fontWeight': '500', 'fontSize': '14px', 'color': C['text']}),
            status_badge(d['status']),
        ]),
        html.Div([
            html.Span(d['location'], style={'fontSize': '12px', 'color': C['muted']}),
            html.Span(
                f" · Free in {d['free_in']} mins" if d['free_in'] > 0 else " · Available NOW",
                style={'fontSize': '12px', 'color': C['teal']}),
        ]),
        tracking_row(ble=d['ble'], wifi=d['wifi'], bt=d['bt'], camera=d['camera'])
    ], style={'padding': '12px 0', 'borderBottom': f'0.5px solid {C["border"]}'}) for d in doctors]

    nurse_rows = [html.Div([
        html.Div([
            html.Span(nu['name'], style={'fontWeight': '500', 'fontSize': '14px', 'color': C['text']}),
            status_badge(nu['status']),
        ]),
        html.Div([
            html.Span(nu['location'], style={'fontSize': '12px', 'color': C['muted']}),
            html.Span(
                f" · Handling {nu['patient']}" if nu['patient'] else " · No patient",
                style={'fontSize': '12px', 'color': C['purple']}),
        ]),
        tracking_row(ble=nu['ble'], wifi=nu['wifi'], bt=nu['bt'], camera=nu['camera'])
    ], style={'padding': '12px 0', 'borderBottom': f'0.5px solid {C["border"]}'}) for nu in nurses]

    now_live = datetime.now()
    rows = []
    critical_alerts = []
    play_sound = False

    for i, p in enumerate(pts):
        checkin  = datetime.fromisoformat(p['checkin'])
        lv_time  = datetime.fromisoformat(p.get('last_visit', p['checkin']))
        wait     = int((now_live - checkin).total_seconds() / 60)
        lv_mins  = int((now_live - lv_time).total_seconds() / 60)
        all_done = p['doc_ready'] and p['family_signed'] and p['reception_done']
        row_bg   = C['row_ready'] if all_done else (C['row_alert'] if wait > 60 else C['card'])

        if p['severity'] == 'Extreme' and lv_mins > 30:
            critical_alerts.append(f"🚨 {p['name']} ({p['room']}) — Extreme patient, no visit in {lv_mins} mins!")
            play_sound = True
        elif wait > 120:
            critical_alerts.append(f"⚠️ {p['name']} ({p['room']}) — Waiting {wait} mins!")
            play_sound = True

        steps = html.Div([
            discharge_btn("Doctor",    "✅", "doc-btn",       i, p['doc_ready'],    True,                                    C['teal']),
            discharge_btn("Family",    "📋", "family-btn",    i, p['family_signed'], p['doc_ready'],                          C['amber']),
            discharge_btn("Reception", "🏠", "reception-btn", i, p['reception_done'], p['doc_ready'] and p['family_signed'],  C['purple']),
            html.Span("✓ Done", style={'fontSize': '11px', 'color': C['green'], 'marginLeft': '6px', 'fontWeight': '500'})
            if all_done else
            html.Span(f"{1 if not p['doc_ready'] else 2 if not p['family_signed'] else 3}/3",
                style={'fontSize': '10px', 'color': C['muted'], 'marginLeft': '6px'})
        ], style={'display': 'flex', 'alignItems': 'center'})

        rows.append(html.Tr([
            html.Td(p['name'], style={'padding': '10px 12px', 'fontWeight': '500', 'fontSize': '13px', 'color': C['text']}),
            html.Td(p['room'], style={'padding': '10px 12px', 'fontSize': '13px', 'color': C['muted']}),
            html.Td(severity_badge(p['severity']), style={'padding': '10px 12px'}),
            html.Td(tracking_row(
                brooch=p.get('brooch','Strong'),
                wifi=p.get('wifi','Strong'),
                camera=p.get('camera','Active')
            ), style={'padding': '10px 12px'}),
            html.Td(last_visit_badge(
                p.get('last_visit', p['checkin']),
                p['severity'], C
            ), style={'padding': '10px 12px'}),
            html.Td(html.Span(f"{wait} mins", style={
                'color': C['red'] if wait > 60 else C['teal'],
                'fontWeight': '500' if wait > 60 else '400', 'fontSize': '13px'}),
                style={'padding': '10px 12px'}),
            html.Td(p['nurse'], style={'padding': '10px 12px', 'fontSize': '13px', 'color': C['text']}),
            html.Td(html.Span(p['doctor'], style={
                'color': C['red'] if p['doctor'] == 'Unassigned' else C['text'],
                'fontSize': '13px'}), style={'padding': '10px 12px'}),
            html.Td(steps, style={'padding': '8px 12px'}),
        ], style={'borderBottom': f'0.5px solid {C["border"]}', 'background': row_bg}))

    alert_banner = html.Div()
    if critical_alerts:
        alert_banner = html.Div([
            html.Div([
                html.Span("🔔 CRITICAL ALERTS — ", style={
                    'fontWeight': '500', 'fontSize': '13px', 'color': '#A32D2D'}),
                *[html.Span(f"{a}  ", style={
                    'fontSize': '12px', 'color': '#A32D2D'})
                  for a in critical_alerts]
            ], style={
                'background': '#FCEBEB', 'border': '1px solid #F09595',
                'borderRadius': '8px', 'padding': '10px 16px',
                'marginBottom': '16px', 'display': 'flex',
                'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '8px'
            })
        ])

    sound_trigger = html.Div(
        id='_sound',
        **({'data-play': str(n)} if play_sound else {}),
        style={'display': 'none'}
    ) if play_sound else html.Div(style={'display': 'none'})

    waiting_over = sum(1 for p in pts
        if int((now_live - datetime.fromisoformat(p['checkin'])).total_seconds()/60) > 60)

    stat_cards = [
        html.Div([
            html.P(t, style={'fontSize': '12px', 'color': C['muted'], 'margin': '0 0 4px'}),
            html.P(v, style={'fontSize': '28px', 'fontWeight': '500', 'color': c, 'margin': '0'}),
        ], style={'background': C['card'], 'borderRadius': '12px',
            'padding': '16px 20px', 'border': f'0.5px solid {c}',
            'flex': '1', 'minWidth': '140px'})
        for t, v, c in [
            ("Total Patients",    str(len(pts)), C['purple']),
            ("Doctors Available", str(sum(1 for d in doctors if d['status'] == 'Available')), C['teal']),
            ("Nurses Free",       str(sum(1 for nu in nurses if nu['status'] == 'Free')), C['green']),
            ("Beds Free",         str(sum(1 for b in beds if b['status'] == 'Free')), C['amber']),
            ("Waiting > 1hr",     str(waiting_over), C['red']),
            ("Model Accuracy",    "74.56%", C['purple']),
        ]
    ]

    return footer, rows, stat_cards, doctor_rows, nurse_rows, alert_banner, sound_trigger

app.clientside_callback(
    """
    function(children) {
        if (children && children.props && children.props['data-play']) {
            try {
                var ctx = new (window.AudioContext || window.webkitAudioContext)();
                var o = ctx.createOscillator();
                var g = ctx.createGain();
                o.connect(g); g.connect(ctx.destination);
                o.type = 'sine';
                o.frequency.setValueAtTime(880, ctx.currentTime);
                g.gain.setValueAtTime(0.2, ctx.currentTime);
                g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.6);
                o.start(ctx.currentTime);
                o.stop(ctx.currentTime + 0.6);
            } catch(e) {}
        }
        return '';
    }
    """,
    Output('sound-trigger', 'title'),
    Input('sound-trigger', 'children'),
)

if __name__ == '__main__':
    app.run(debug=False, dev_tools_ui=False)
