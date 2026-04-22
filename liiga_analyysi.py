import json
import pandas as pd
import numpy as np
import plotly.express as px
import os

def aja_analyysi():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'data.json')
    
    # --- SANASTOT NIMILLE (Koska JSON:ssa on vain ID:t) ---
    joukkue_nimet = {
        "951626834": "Ilves",
        "362185137": "Tappara",
        "951626834.0": "Ilves",
        "362185137.0": "Tappara"
    }
    
    # Voit täydentää tätä listaa pelin jälkeen
    pelaaja_nimet = {
        "60972169": "L. Henman",
        "30984675": "Pelaaja X", # Esimerkki ID kuvastasi
        "60862140": "Maalivahti"
    }

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
            
        shot_list = []
        
        for e in events:
            x_raw = e.get('shotX')
            y_raw = e.get('shotY')
            if x_raw is None or y_raw is None: continue

            # --- KOORDINAATTIEN SKAALAUS (Liigan 0-1000 -> 0-100) ---
            # Jaetaan X ja Y niin, että ne täyttävät koko kaukalon
            x = float(x_raw) / 10.0
            y = float(y_raw) / 10.0
            
            # Käännetään Y-akseli, jos se on ylösalaisin
            y = 100 - y 

            # Selvitetään joukkue ja pelaaja
            t_id = str(e.get('shootingTeamId'))
            p_id = str(e.get('shooterId'))
            
            j_nimi = joukkue_nimet.get(t_id, f"Joukkue {t_id}")
            p_nimi = pelaaja_nimet.get(p_id, f"ID: {p_id}")
            
            e_type = str(e.get('eventType', '')).upper()
            is_goal = 'GOAL' in e_type or e.get('type') == 'Goal' # Tarkistetaan molemmat
            tulos = 'MAALI' if is_goal else 'Laukaus'

            shot_list.append({
                'x': x, 'y': y,
                'Pelaaja': p_nimi,
                'Joukkue': j_nimi,
                'Tulos': tulos,
                'Koko': 15 if is_goal else 8
            })

        df = pd.DataFrame(shot_list)

        # Luodaan visualisointi
        fig = px.scatter(df, x="x", y="y", 
                         color="Joukkue", 
                         symbol="Tulos",
                         size="Koko",
                         hover_data=['Pelaaja', 'Joukkue', 'Tulos'],
                         color_discrete_map={"Ilves": "#00FF00", "Tappara": "#FF8C00"},
                         range_x=[0, 100], range_y=[0, 100],
                         title="Liiga Otteluvisualisointi: Ilves - Tappara")

        # --- KAUKALON GRAFIIKKA ---
        # Keskiviiva
        fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=100, line_color="red", opacity=0.5)
        # Siniviivat (Liigan standardi n. 33% ja 66%)
        fig.add_shape(type="line", x0=33, y0=0, x1=33, y1=100, line_color="blue", opacity=0.5)
        fig.add_shape(type="line", x0=67, y0=0, x1=67, y1=100, line_color="blue", opacity=0.5)
        # Maalit ja päätyviivat (11% ja 89%)
        fig.add_shape(type="line", x0=11, y0=0, x1=11, y1=100, line_color="red", opacity=0.3)
        fig.add_shape(type="line", x0=89, y0=0, x1=89, y1=100, line_color="red", opacity=0.3)
        fig.add_shape(type="rect", x0=10, y0=47, x1=11, y1=53, fillcolor="red", line_color="red")
        fig.add_shape(type="rect", x0=89, y0=47, x1=90, y1=53, fillcolor="red", line_color="red")

        fig.update_layout(
            template="plotly_dark",
            width=1000, height=600,
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False)
        )
        
        fig.write_html(os.path.join(script_dir, "liiga_kaukalo_valmis.html"))
        print(f"Valmista! Käsiteltiin {len(df)} laukausta.")

    except Exception as e:
        print(f"Virhe: {e}")

if __name__ == "__main__":
    aja_analyysi()