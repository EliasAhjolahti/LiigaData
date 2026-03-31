import json
import pandas as pd
import numpy as np
import plotly.express as px

def process_local_json():
    try:
        # 1. Luetaan tallentamasi JSON-tiedosto
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Liigan JSON-rakenne (polku saattaa vaihdella, säädä tarvittaessa)
        # Yleensä: data['events'] tai data['game']['shots']
        events = data.get('events', [])
        if not events and 'game' in data:
            events = data['game'].get('shots', [])

        shot_list = []
        for e in events:
            # Poimitaan vain laukaukset ja maalit
            e_type = str(e.get('eventType', '')).upper()
            if 'SHOT' in e_type or 'GOAL' in e_type:
                # Liigan koordinaatit (yleensä 0-100)
                x = float(e.get('x', 0))
                y = float(e.get('y', 0))
                
                # Käännetään kaikki laukaukset hyökkäämään kohti pistettä (89, 50)
                if x < 50:
                    x = 100 - x
                    y = 100 - y

                shot_list.append({
                    'x': x,
                    'y': y,
                    'player': e.get('playerName', 'Tuntematon'),
                    'team': e.get('teamName', 'Joukkue'),
                    'is_goal': 1 if 'GOAL' in e_type else 0
                })

        df = pd.DataFrame(shot_list)

        # 2. xG-laskenta (Logistinen malli)
        def calculate_xg(row):
            # Etäisyys maalin keskipisteestä (89, 50)
            dist = np.sqrt((row['x'] - 89)**2 + (row['y'] - 50)**2)
            # Mitä pienempi etäisyys, sitä suurempi xG
            # Kerroin -0.15 on tyypillinen jääkiekon xG-malleissa
            logit = 0.8 - (0.15 * dist) 
            xg = 1 / (1 + np.exp(-logit))
            return round(xg, 3)

        df['xG'] = df.apply(calculate_xg, axis=1)

        # 3. Luodaan frontend.html
        fig = px.scatter(df, x="x", y="y", 
                         color="xG", 
                         size=df['xG'] + 0.2,
                         symbol="is_goal",
                         hover_data=['player', 'xG', 'team'],
                         color_continuous_scale="RdYlGn_r",
                         range_x=[0, 100], range_y=[0, 100],
                         title="Liiga xG-Analyysi (Paikallinen data)")

        # Piirretään maalin ääriviivat visualisointiin
        fig.add_shape(type="rect", x0=88, y0=45, x1=90, y1=55, line=dict(color="White"))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#111",
            plot_bgcolor="#111",
            width=1000, height=600
        )

        fig.write_html("frontend.html")
        print("Valmista tuli! Avaa 'frontend.html' selaimessasi.")

    except FileNotFoundError:
        print("Virhe: Tiedostoa 'data.json' ei löytynyt. Tallenna se ensin!")
    except Exception as e:
        print(f"Virhe koodissa: {e}")

if __name__ == "__main__":
    process_local_json()