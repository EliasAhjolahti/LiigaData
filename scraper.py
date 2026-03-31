import requests
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Haetaan data (Esimerkki-ID pelille)
game_id = "55104"
season = "2026"
url = f"https://liiga.fi/api/v1/games/{season}/{game_id}"

# Huom: Oikeassa käytössä Liigan API saattaa vaatia User-Agent-otsikon
response = requests.get(url)
data = response.json()

# Poimitaan tapahtumat (laukaukset)
# Liigan JSON-rakenteessa laukaukset löytyvät yleensä 'events' tai 'shootings' -kohdasta
events = data.get('events', [])
shots = [e for e in events if e['eventType'] in ['SHOT', 'GOAL']]

df = pd.DataFrame(shots)

# 2. Esikäsittely ja xG-laskenta
# Liigan koordinaatit ovat tyypillisesti välillä 0-100 tai kaukalo-metreinä.
# Oletetaan tässä x=0-100, y=0-100, missä maali on pisteessä (89, 50)
goal_x, goal_y = 89, 50 

def calculate_xg(row):
    # Lasketaan etäisyys maaliin
    dist = np.sqrt((row['x'] - goal_x)**2 + (row['y'] - goal_y)**2)
    # Lasketaan kulma (yksinkertaistettu)
    angle = np.abs(np.arctan2(row['y'] - goal_y, goal_x - row['x']))
    
    # Yksinkertaistettu logistinen malli (kertoimet ovat suuntaa-antavia)
    # Oikeassa mallissa käytettäisiin tuhansia aiempia laukauksia kertoimien opettamiseen
    logit = 0.5 - (0.15 * dist) + (0.05 * (1/max(angle, 0.1)))
    xg = 1 / (1 + np.exp(-logit))
    return round(xg, 3)

df['xG'] = df.apply(calculate_xg, axis=1)

# 3. Visualisointi HTML-sivulle
fig = px.scatter(df, x="x", y="y", color="xG", 
                 hover_data=['player_name', 'shotType', 'xG'],
                 title=f"Liiga Ottelu {game_id} - xG Kaukalokartta",
                 range_x=[0, 100], range_y=[0, 100],
                 color_continuous_scale="RdYlGn_r")

# Lisätään kaukalon taustakuva (vapaaehtoinen, jos sinulla on rink.png)
# fig.update_layout(images=[dict(source="rink_url", ...)])

# Tallennetaan HTML-tiedostona
fig.write_html("xg_kaukalokartta.html")
print("xG-kartta tallennettu tiedostoon xg_kaukalokartta.html")