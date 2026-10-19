import streamlit as st
import numpy as np
import plotly.graph_objects as go
import random

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Proyek 11: Delivery Route Challenge",
    page_icon="🚚",
    layout="wide"
)

# Custom Styling CSS (Dark Theme Elegan & Bersih)
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { width: 100%; background-color: #0284c7; color: white; font-weight: bold; border-radius: 8px; padding: 10px; }
    .stButton>button:hover { background-color: #0369a1; }
    div[data-testid="stSidebar"] { background-color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

st.title("🚚 PROYEK 11: DELIVERY ROUTE CHALLENGE")
st.markdown("**Komputasi Graf · Heuristik Nearest Neighbor vs. Manual Human Challenge**")
st.markdown("---")

# 2. Sidebar Pengaturan Skenario
st.sidebar.header("🎛️ Pengaturan Skenario")
num_nodes = st.sidebar.slider("Jumlah Titik Tujuan Pelanggan", 5, 10, 8)

if st.sidebar.button("🎲 Acak Skenario Peta Baru"):
    st.session_state.seed = random.randint(1, 10000)

if 'seed' not in st.session_state:
    st.session_state.seed = 42

# 3. Pembangkitan Data Koordinat (Depot & Pelanggan)
random.seed(st.session_state.seed)
np.random.seed(st.session_state.seed)

nodes = [{'id': 'Depot', 'x': 0, 'y': 0, 'label': '🏠 Depot Utama'}]
for i in range(1, num_nodes + 1):
    nodes.append({
        'id': i,
        'x': int(random.randint(-16, 16)),
        'y': int(random.randint(-16, 16)),
        'label': f'📍 Tujuan {i}'
    })

def hitung_jarak(p1, p2):
    return np.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

# 4. Algoritma Nearest Neighbor (Greedy TSP)
unvisited = nodes[1:].copy()
current = nodes[0]
nn_path = [0]
total_nn_dist = 0

while unvisited:
    nearest_idx = min(range(len(unvisited)), key=lambda i: hitung_jarak(current, unvisited[i]))
    total_nn_dist += hitung_jarak(current, unvisited[nearest_idx])
    current = unvisited[nearest_idx]
    nn_path.append(next(i for i, n in enumerate(nodes) if n['id'] == current['id']))
    unvisited.pop(nearest_idx)

# Perjalanan Pulang ke Depot
total_nn_dist += hitung_jarak(current, nodes[0])
nn_path.append(0)

# 5. Tata Letak Utama (Dua Kolom)
col1, col2 = st.columns([2, 1])

# Inisialisasi variabel rute user
user_path = None
total_user_dist = None
is_valid_user = False

with col2:
    st.subheader("📊 Metrik & Validasi")
    
    # Metrik Nearest Neighbor
    st.markdown(f"""
    <div style="background:#1e293b; padding:15px; border-radius:10px; border-left:5px solid #38bdf8; margin-bottom:15px;">
        <b style="color:#38bdf8; font-size:15px;">🤖 Nearest Neighbor (Otomatis)</b>
        <p style="font-size:24px; margin:4px 0; font-weight:bold; color:white;">{total_nn_dist:.2f} km</p>
        <small style="color:#94a3b8;"><b>Urutan Rute:</b><br>{' → '.join([str(nodes[i]['id']) for i in nn_path])}</small>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👤 Tantangan Manual (Human)")
    default_text = ", ".join([str(n['id']) for n in nodes[1:]])
    user_input = st.text_input("Urutan kunjungan pelanggan (pisahkan dengan koma):", default_text)
    
    try:
        user_list = [int(x.strip()) for x in user_input.split(',')]
        target_set = set(range(1, num_nodes + 1))
        
        if len(user_list) == num_nodes and set(user_list) == target_set:
            user_path = [0] + [next(i for i, n in enumerate(nodes) if n['id'] == uid) for uid in user_list] + [0]
            total_user_dist = sum(hitung_jarak(nodes[user_path[i]], nodes[user_path[i+1]]) for i in range(len(user_path)-1))
            is_valid_user = True
            
            st.success("✅ **Validasi Rute: LULUS**\nSemua titik dikunjungi tepat 1 kali & kembali ke Depot.")
            st.markdown(f"**Total Jarak Rute Manual:** `{total_user_dist:.2f} km`")
            
            diff = total_user_dist - total_nn_dist
            if diff > 0:
                st.info(f"💡 Algoritma Nearest Neighbor lebih hemat **{diff:.2f} km** dibanding rute manual ini.")
            elif diff < 0:
                st.balloons()
                st.success(f"🔥 **Luar biasa!** Rute manual berhasil mengalahkan algoritma sebesar **{-diff:.2f} km**!")
            else:
                st.warning("⚖️ Rute manual memiliki total jarak yang persis sama dengan algoritma.")
        else:
            st.error(f"❌ Harap masukkan seluruh angka 1 sampai {num_nodes} tanpa ada duplikat atau angka terlewat.")
    except:
        st.warning("⚠️ Harap masukkan format angka yang benar (Contoh: `1, 2, 3, 4, 5, 6`)")

with col1:
    st.subheader("🗺️ Visualisasi Peta Rute Pengiriman")
    
    # Membangun Plotly Figure dengan Native Frame Animation (Anti Kedap-Kedip)
    fig = go.Figure()

    # Trace 1: Rute Nearest Neighbor
    nn_x = [nodes[i]['x'] for i in nn_path]
    nn_y = [nodes[i]['y'] for i in nn_path]
    fig.add_trace(go.Scatter(
        x=nn_x, y=nn_y, mode='lines+markers',
        name='🤖 Nearest Neighbor',
        line=dict(color='#38bdf8', width=3),
        marker=dict(size=6)
    ))

    # Trace 2: Rute Manual (jika valid)
    if is_valid_user and user_path:
        man_x = [nodes[i]['x'] for i in user_path]
        man_y = [nodes[i]['y'] for i in user_path]
        fig.add_trace(go.Scatter(
            x=man_x, y=man_y, mode='lines',
            name='👤 Manual Challenge',
            line=dict(color='#f43f5e', width=2, dash='dash')
        ))

    # Trace 3: Node Lokasi (Depot Square Besar vs Pelanggan Circle)
    fig.add_trace(go.Scatter(
        x=[n['x'] for n in nodes],
        y=[n['y'] for n in nodes],
        mode='markers+text',
        text=[n['label'] for n in nodes],
        textposition='top center',
        textfont=dict(color='white', size=11),
        marker=dict(
            size=[28 if n['id']=='Depot' else 16 for n in nodes],
            color=['#f59e0b' if n['id']=='Depot' else '#10b981' for n in nodes],
            symbol=['square' if n['id']=='Depot' else 'circle' for n in nodes],
            line=dict(width=2, color='white')
        ),
        name='Lokasi (Depot & Pelanggan)'
    ))

    # Trace 4: Marker Kurir Bergerak (Bintang Merah)
    fig.add_trace(go.Scatter(
        x=[nodes[nn_path[0]]['x']],
        y=[nodes[nn_path[0]]['y']],
        mode='markers',
        marker=dict(size=22, color='#ef4444', symbol='star'),
        name='🚚 Posisi Kurir'
    ))

    # Membuat Frame Animasi Mulus untuk Plotly
    frames = []
    for step in range(len(nn_path)):
        curr_node = nodes[nn_path[step]]
        sub_x = [nodes[i]['x'] for i in nn_path[:step+1]]
        sub_y = [nodes[i]['y'] for i in nn_path[:step+1]]
        
        frame_data = [
            go.Scatter(x=sub_x, y=sub_y, mode='lines+markers', line=dict(color='#38bdf8', width=4)),
        ]
        if is_valid_user and user_path:
            frame_data.append(go.Scatter(x=man_x, y=man_y, mode='lines', line=dict(color='#f43f5e', width=2, dash='dash')))
        
        frame_data.append(go.Scatter(
            x=[n['x'] for n in nodes], y=[n['y'] for n in nodes],
            mode='markers+text', text=[n['label'] for n in nodes],
            textposition='top center', textfont=dict(color='white', size=11),
            marker=dict(
                size=[28 if n['id']=='Depot' else 16 for n in nodes],
                color=['#f59e0b' if n['id']=='Depot' else '#10b981' for n in nodes],
                symbol=['square' if n['id']=='Depot' else 'circle' for n in nodes],
                line=dict(width=2, color='white')
            )
        ))
        
        frame_data.append(go.Scatter(
            x=[curr_node['x']], y=[curr_node['y']],
            mode='markers', marker=dict(size=24, color='#ef4444', symbol='star')
        ))
        
        frames.append(go.Frame(data=frame_data, name=f'frame_{step}'))

    fig.frames = frames

    # Menambahkan Tombol Play & Slider Animasi di Bawah Grafik Plotly
    fig.update_layout(
        paper_bgcolor='#1e293b', plot_bgcolor='#0f172a',
        font=dict(color='white'),
        xaxis=dict(showgrid=True, gridcolor='#334155', zeroline=False, range=[-19, 19]),
        yaxis=dict(showgrid=True, gridcolor='#334155', zeroline=False, range=[-19, 19]),
        margin=dict(l=20, r=20, t=20, b=20),
        height=510,
        legend=dict(orientation="h", y=1.1, x=0),
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 600, "redraw": True}, "fromcurrent": True}],
                    "label": "▶️ Putar Animasi Kurir",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}],
                    "label": "⏸️ Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 10},
            "showactive": False,
            "type": "buttons",
            "x": 0,
            "xanchor": "left",
            "y": -0.08,
            "yanchor": "top"
        }],
        sliders=[{
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 12, "color": "#38bdf8"},
                "prefix": "Langkah Animasi: ",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": 300, "easing": "cubic-in-out"},
            "pad": {"b": 10, "t": 30},
            "len": 0.9,
            "x": 0.1,
            "y": -0.08,
            "steps": [
                {
                    "args": [[f"frame_{k}"], {"frame": {"duration": 300, "redraw": True}, "mode": "immediate"}],
                    "label": f"Kunjungan {k}",
                    "method": "animate"
                } for k in range(len(nn_path))
            ]
        }]
    )

    st.plotly_chart(fig, use_container_width=True)

# 6. Catatan Analisis Teoretis & Eksperimental Model
st.markdown("---")
st.subheader("💡 Analisis Teoretis & Eksperimental Model")
st.info("""
* **Batas Interpretasi Algoritma:** *Nearest Neighbor* adalah algoritma **heuristik greedy** yang mengambil keputusan lokal terbaik pada setiap langkah perjalanan. Algoritma ini memiliki kompleksitas komputasi yang rendah dan sangat cepat, namun **tidak menjamin** rute terpendek yang mutlak optimal secara global (*Global Optimum*).
* **Evaluasi Perbandingan (Manusia vs Algoritma):** Pada konfigurasi spasial tertentu, pengamatan spasial manusia dapat mengenali pola geometri global (seperti kluster melingkar atau bentuk simetris) sehingga rute manual dapat menghindari lintasan memutar di akhir perjalanan yang merupakan kelemahan khas dari sifat *short-sighted* (*miopia*) algoritma *Nearest Neighbor*.
""")