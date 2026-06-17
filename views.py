from dash import html, dcc
from datetime import datetime

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
    if signal in ['Lost', None]:
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

def last_visit_badge(last_visit, severity, C):
    mins = int((datetime.now() - last_visit).total_seconds() / 60)
    if severity == 'Extreme' and mins > 30:
        color, bg, icon = '#A32D2D', '#FCEBEB', '🚨'
    elif severity == 'Moderate' and mins > 60:
        color, bg, icon = '#854F0B', '#FAEEDA', '⚠️'
    elif mins > 120:
        color, bg, icon = '#854F0B', '#FAEEDA', '⚠️'
    else:
        color, bg, icon = '#0F6E56', '#E1F5EE', '✓'
    label = f"{icon} {mins}m ago" if mins < 60 else f"{icon} {mins//60}h {mins%60}m ago"
    return html.Span(label, style={'fontSize': '10px', 'padding': '2px 7px',
        'borderRadius': '4px', 'background': bg, 'color': color, 'fontWeight': '500'})

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

def role_badge(role):
    colors = {
        'admin':        ('#3C3489', '#EEEDFE', '👑 Admin'),
        'doctor':       ('#085041', '#E1F5EE', '👨‍⚕️ Doctor'),
        'nurse':        ('#712B13', '#FAECE7', '👩‍⚕️ Nurse'),
        'receptionist': ('#633806', '#FAEEDA', '🧾 Reception'),
    }
    color, bg, label = colors.get(role, ('#888', '#eee', role))
    return html.Span(label, style={'fontSize': '11px', 'padding': '3px 10px',
        'borderRadius': '20px', 'background': bg, 'color': color, 'fontWeight': '500'})

def input_style(C):
    return {'fontSize': '12px', 'padding': '6px 10px', 'borderRadius': '6px',
        'border': f'0.5px solid {C["input_border"]}',
        'background': C['input_bg'], 'color': C['input_text'],
        'fontFamily': 'system-ui, sans-serif', 'outline': 'none'}

def header(C, is_dark, role, username):
    return html.Div([
        html.Div([
            html.H1("🏥 Silent Hospital OS", style={
                'fontSize': '24px', 'fontWeight': '500',
                'color': C['purple'], 'margin': '0'}),
            html.P("Zero interaction. Just works.", style={
                'fontSize': '13px', 'color': C['muted'], 'margin': '4px 0 0'}),
        ]),
        html.Div([
            role_badge(role),
            html.Span(f" {username}", style={
                'fontSize': '12px', 'color': C['muted'],
                'marginLeft': '8px', 'marginRight': '16px'}),
            html.Button(
                "☀️ Light" if is_dark else "🌙 Dark",
                id='theme-toggle', n_clicks=1 if is_dark else 0,
                style={'fontSize': '12px', 'padding': '6px 14px',
                    'borderRadius': '20px',
                    'border': f'0.5px solid {C["btn_border"]}',
                    'background': C['btn_bg'], 'color': C['btn_text'],
                    'cursor': 'pointer', 'fontFamily': 'system-ui, sans-serif',
                    'marginRight': '8px'}),
            html.A("Logout →", href="/logout", style={
                'fontSize': '12px', 'color': C['red'],
                'textDecoration': 'none',
                'border': f'0.5px solid {C["red"]}',
                'padding': '6px 14px', 'borderRadius': '20px'})
        ], style={'display': 'flex', 'alignItems': 'center'})
    ], style={'display': 'flex', 'justifyContent': 'space-between',
        'alignItems': 'center', 'marginBottom': '24px'})

def card(C, children, **kwargs):
    style = {'background': C['card'], 'borderRadius': '12px',
        'padding': '20px', 'border': f'0.5px solid {C["border"]}',
        'marginBottom': '16px'}
    style.update(kwargs)
    return html.Div(children, style=style)

def section_title(title, subtitle, C):
    return html.Div([
        html.H3(title, style={'fontSize': '15px', 'fontWeight': '500',
            'margin': '0', 'color': C['text'], 'display': 'inline-block'}),
        html.Span(f" — {subtitle}", style={
            'fontSize': '11px', 'color': C['muted'], 'marginLeft': '8px'}),
    ], style={'marginBottom': '16px'})

def patient_table_header(C):
    return html.Thead(html.Tr([
        html.Th(c, style={'textAlign': 'left', 'fontSize': '12px',
            'color': C['muted'], 'fontWeight': '500', 'padding': '8px 12px',
            'borderBottom': f'0.5px solid {C["border"]}'})
        for c in ['Patient','Room','Severity','Tracking',
                  'Last Visit','Waiting','Nurse','Doctor','Discharge']
    ]))

def build_doctor_view(C, is_dark, username, doctors, nurses, patients, beds):
    my_patients = [p for p in patients if p.doctor == username]
    my_nurses   = list({p.nurse for p in my_patients if p.nurse != 'Unassigned'})
    free_nurses = [n for n in nurses if n.status == 'Free']
    busy_nurses = [n for n in nurses if n.status == 'Busy']

    return html.Div(style={
        'fontFamily': 'system-ui, sans-serif',
        'background': C['bg'], 'minHeight': '100vh', 'padding': '24px'
    }, children=[
        header(C, is_dark, 'doctor', username),
        html.Div(id='alert-banner'),

        html.Div([
            html.Div([
                html.P("My Patients", style={'fontSize': '12px', 'color': C['muted'], 'margin': '0 0 4px'}),
                html.P(str(len(my_patients)), style={'fontSize': '28px', 'fontWeight': '500', 'color': C['purple'], 'margin': '0'}),
            ], style={'background': C['card'], 'borderRadius': '12px', 'padding': '16px 20px',
                'border': f'0.5px solid {C["purple"]}', 'flex': '1', 'minWidth': '140px'}),
            html.Div([
                html.P("Nurses on my cases", style={'fontSize': '12px', 'color': C['muted'], 'margin': '0 0 4px'}),
                html.P(str(len(my_nurses)), style={'fontSize': '28px', 'fontWeight': '500', 'color': C['teal'], 'margin': '0'}),
            ], style={'background': C['card'], 'borderRadius': '12px', 'padding': '16px 20px',
                'border': f'0.5px solid {C["teal"]}', 'flex': '1', 'minWidth': '140px'}),
            html.Div([
                html.P("Free nurses available", style={'fontSize': '12px', 'color': C['muted'], 'margin': '0 0 4px'}),
                html.P(str(len(free_nurses)), style={'fontSize': '28px', 'fontWeight': '500', 'color': C['green'], 'margin': '0'}),
            ], style={'background': C['card'], 'borderRadius': '12px', 'padding': '16px 20px',
                'border': f'0.5px solid {C["green"]}', 'flex': '1', 'minWidth': '140px'}),
            html.Div([
                html.P("Waiting > 1hr", style={'fontSize': '12px', 'color': C['muted'], 'margin': '0 0 4px'}),
                html.P(str(sum(1 for p in my_patients
                    if int((datetime.now()-p.checkin).total_seconds()/60)>60)),
                    style={'fontSize': '28px', 'fontWeight': '500', 'color': C['red'], 'margin': '0'}),
            ], style={'background': C['card'], 'borderRadius': '12px', 'padding': '16px 20px',
                'border': f'0.5px solid {C["red"]}', 'flex': '1', 'minWidth': '140px'}),
        ], style={'display': 'flex', 'gap': '12px', 'flexWrap': 'wrap', 'marginBottom': '24px'}),

        html.Div([
            card(C, [
                section_title("👩‍⚕️ Nurses on My Cases", "assigned to your patients", C),
                *([html.Div([
                    html.Span(n.name, style={'fontWeight': '500', 'fontSize': '13px', 'color': C['text']}),
                    status_badge(n.status),
                    html.Span(f" → {n.patient}", style={'fontSize': '12px', 'color': C['purple'], 'marginLeft': '8px'}),
                    tracking_row(ble=n.ble, wifi=n.wifi, bt=n.bt, camera=n.camera)
                ], style={'padding': '10px 0', 'borderBottom': f'0.5px solid {C["border"]}'})
                for n in nurses if n.name in my_nurses] or
                [html.P("No nurses assigned yet", style={'fontSize': '13px', 'color': C['muted']})]),
            ], **{'flex': '1'}),

            card(C, [
                section_title("✅ Free Nurses Available", "not currently assigned", C),
                *([html.Div([
                    html.Span("🟢", style={'marginRight': '8px'}),
                    html.Span(n.name, style={'fontWeight': '500', 'fontSize': '13px', 'color': C['text']}),
                    html.Span(f" · {n.location}", style={'fontSize': '12px', 'color': C['muted'], 'marginLeft': '8px'}),
                    tracking_row(ble=n.ble, wifi=n.wifi, bt=n.bt, camera=n.camera)
                ], style={'padding': '10px 0', 'borderBottom': f'0.5px solid {C["border"]}'})
                for n in free_nurses] or
                [html.P("No free nurses right now", style={'fontSize': '13px', 'color': C['muted']})]),
            ], **{'flex': '1'}),
        ], style={'display': 'flex', 'gap': '16px', 'marginBottom': '16px'}),

        card(C, [
            section_title("🛏️ My Patients", "only patients assigned to you", C),
            html.Table([
                patient_table_header(C),
                html.Tbody(id='patient-table-body'),
            ], style={'width': '100%', 'borderCollapse': 'collapse'})
        ]),

        dcc.Interval(id='interval', interval=2000, n_intervals=0),
        dcc.Store(id='theme-store', data='light'),
        dcc.Store(id='role-store', data='doctor'),
        dcc.Store(id='user-store', data=username),
        html.Div(id='sound-trigger'),
        html.Div([html.P(id='footer-time', style={
            'fontSize': '12px', 'color': C['muted'], 'margin': '0', 'textAlign': 'center'})])
    ])

def build_nurse_view(C, is_dark, username, nurses, patients, beds):
    my_patients = [p for p in patients if p.nurse == username]
    me = next((n for n in nurses if n.name == username), None)

    return html.Div(style={
        'fontFamily': 'system-ui, sans-serif',
        'background': C['bg'], 'minHeight': '100vh', 'padding': '24px'
    }, children=[
        header(C, is_dark, 'nurse', username),
        html.Div(id='alert-banner'),

        html.Div([
            html.Div([
                html.P("My Patients", style={'fontSize': '12px', 'color': C['muted'], 'margin': '0 0 4px'}),
                html.P(str(len(my_patients)), style={'fontSize': '28px', 'fontWeight': '500', 'color': C['purple'], 'margin': '0'}),
            ], style={'background': C['card'], 'borderRadius': '12px', 'padding': '16px 20px',
                'border': f'0.5px solid {C["purple"]}', 'flex': '1'}),
            html.Div([
                html.P("My Status", style={'fontSize': '12px', 'color': C['muted'], 'margin': '0 0 4px'}),
                html.P(me.status if me else 'Unknown', style={'fontSize': '22px', 'fontWeight': '500', 'color': C['teal'], 'margin': '0'}),
            ], style={'background': C['card'], 'borderRadius': '12px', 'padding': '16px 20px',
                'border': f'0.5px solid {C["teal"]}', 'flex': '1'}),
            html.Div([
                html.P("My Location", style={'fontSize': '12px', 'color': C['muted'], 'margin': '0 0 4px'}),
                html.P(me.location if me else 'Unknown', style={'fontSize': '22px', 'fontWeight': '500', 'color': C['amber'], 'margin': '0'}),
            ], style={'background': C['card'], 'borderRadius': '12px', 'padding': '16px 20px',
                'border': f'0.5px solid {C["amber"]}', 'flex': '1'}),
        ], style={'display': 'flex', 'gap': '12px', 'flexWrap': 'wrap', 'marginBottom': '24px'}),

        card(C, [
            section_title("🛏️ My Patients", "patients assigned to you", C),
            html.Table([
                patient_table_header(C),
                html.Tbody(id='patient-table-body'),
            ], style={'width': '100%', 'borderCollapse': 'collapse'})
        ]),

        card(C, [
            section_title("📡 My Tracking Signals", "your badge signal status", C),
            html.Div([
                tracking_row(
                    ble=me.ble if me else 'Lost',
                    wifi=me.wifi if me else 'Lost',
                    bt=me.bt if me else 'Lost',
                    camera=me.camera if me else 'Lost'
                )
            ])
        ]),

        dcc.Interval(id='interval', interval=2000, n_intervals=0),
        dcc.Store(id='theme-store', data='light'),
        dcc.Store(id='role-store', data='nurse'),
        dcc.Store(id='user-store', data=username),
        html.Div(id='sound-trigger'),
        html.Div([html.P(id='footer-time', style={
            'fontSize': '12px', 'color': C['muted'], 'margin': '0', 'textAlign': 'center'})])
    ])

def build_receptionist_view(C, is_dark, username, patients, beds):
    return html.Div(style={
        'fontFamily': 'system-ui, sans-serif',
        'background': C['bg'], 'minHeight': '100vh', 'padding': '24px'
    }, children=[
        header(C, is_dark, 'receptionist', username),
        html.Div(id='alert-banner'),

        html.Div([
            html.Div([
                html.P("Total Patients", style={'fontSize': '12px', 'color': C['muted'], 'margin': '0 0 4px'}),
                html.P(str(len(patients)), style={'fontSize': '28px', 'fontWeight': '500', 'color': C['purple'], 'margin': '0'}),
            ], style={'background': C['card'], 'borderRadius': '12px', 'padding': '16px 20px',
                'border': f'0.5px solid {C["purple"]}', 'flex': '1'}),
            html.Div([
                html.P("Beds Free", style={'fontSize': '12px', 'color': C['muted'], 'margin': '0 0 4px'}),
                html.P(str(sum(1 for b in beds if b['status']=='Free')),
                    style={'fontSize': '28px', 'fontWeight': '500', 'color': C['teal'], 'margin': '0'}),
            ], style={'background': C['card'], 'borderRadius': '12px', 'padding': '16px 20px',
                'border': f'0.5px solid {C["teal"]}', 'flex': '1'}),
            html.Div([
                html.P("Waiting > 1hr", style={'fontSize': '12px', 'color': C['muted'], 'margin': '0 0 4px'}),
                html.P(str(sum(1 for p in patients
                    if int((datetime.now()-p.checkin).total_seconds()/60)>60)),
                    style={'fontSize': '28px', 'fontWeight': '500', 'color': C['red'], 'margin': '0'}),
            ], style={'background': C['card'], 'borderRadius': '12px', 'padding': '16px 20px',
                'border': f'0.5px solid {C["red"]}', 'flex': '1'}),
        ], style={'display': 'flex', 'gap': '12px', 'flexWrap': 'wrap', 'marginBottom': '24px'}),

        card(C, [
            html.H3("➕ Admit New Patient", style={'fontSize': '15px', 'fontWeight': '500',
                'margin': '0 0 16px', 'color': C['text']}),
            html.Div([
                dcc.Input(id='inp-name', placeholder='Patient full name', debounce=False,
                    style={**input_style(C), 'width': '200px'}),
                dcc.Input(id='inp-room', placeholder='Room number', debounce=False,
                    style={**input_style(C), 'width': '100px', 'marginLeft': '8px'}),
                dcc.Dropdown(id='inp-severity',
                    options=[{'label': s, 'value': s} for s in ['Extreme','Moderate','Minor']],
                    placeholder='Severity', clearable=False,
                    style={'width': '130px', 'fontSize': '12px',
                        'display': 'inline-block', 'marginLeft': '8px',
                        'verticalAlign': 'middle'}),
                html.Button("+ Admit Patient", id='admit-btn', n_clicks=0,
                    style={'fontSize': '12px', 'padding': '8px 16px', 'borderRadius': '6px',
                        'border': f'0.5px solid {C["teal"]}',
                        'background': C["teal"], 'color': '#ffffff',
                        'cursor': 'pointer', 'marginLeft': '8px',
                        'fontFamily': 'system-ui, sans-serif', 'fontWeight': '500'}),
                html.Span(id='admit-msg', style={
                    'fontSize': '11px', 'color': C['teal'], 'marginLeft': '8px'}),
            ], style={'display': 'flex', 'alignItems': 'center',
                'flexWrap': 'wrap', 'gap': '4px'}),
        ]),

        card(C, [
            section_title("🛏️ All Patients", "full patient list for reception", C),
            html.Div([
                html.Span("Discharge: ", style={'fontSize': '11px', 'color': C['muted']}),
                html.Span("✅ Doctor → 📋 Family → ", style={'fontSize': '11px', 'color': C['teal']}),
                html.Span("🏠 Reception confirms", style={'fontSize': '11px', 'color': C['purple']}),
                html.Span(" → Discharged", style={'fontSize': '11px', 'color': C['green']}),
            ], style={'marginBottom': '10px'}),
            html.Table([
                patient_table_header(C),
                html.Tbody(id='patient-table-body'),
            ], style={'width': '100%', 'borderCollapse': 'collapse'})
        ]),

        card(C, [
            section_title("🛏️ Bed Status", "real-time bed availability", C),
            *[html.Div([
                html.Span(b['room'], style={'fontWeight': '500', 'fontSize': '13px', 'color': C['text']}),
                html.Span(
                    " · FREE NOW" if b['status'] == 'Free' else f" · Free in {b['free_in']} mins",
                    style={'fontSize': '12px',
                        'color': C['teal'] if b['status'] == 'Free' else C['amber']}),
                html.Span("●", style={'float': 'right',
                    'color': C['teal'] if b['status'] == 'Free' else C['coral']})
            ], style={'padding': '10px 0', 'borderBottom': f'0.5px solid {C["border"]}',
                'fontSize': '13px'}) for b in beds]
        ]),

        dcc.Interval(id='interval', interval=2000, n_intervals=0),
        dcc.Store(id='theme-store', data='light'),
        dcc.Store(id='role-store', data='receptionist'),
        dcc.Store(id='user-store', data=username),
        html.Div(id='sound-trigger'),
        html.Div([html.P(id='footer-time', style={
            'fontSize': '12px', 'color': C['muted'], 'margin': '0', 'textAlign': 'center'})])
    ])
