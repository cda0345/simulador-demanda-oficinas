
import streamlit as st
import pandas as pd
import folium
import numpy as np
from streamlit_folium import folium_static
from folium.plugins import HeatMap

st.set_page_config(page_title="Simulador Visual - Versão Estável", layout="wide")

# Haversine para distância vetorizada
def haversine_np(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))

def distancia_km_np(lat1, lon1, lat2, lon2):
    return haversine_np(lat1, lon1, lat2, lon2)

# Categorização de serviço
def categorizar_servico(servico):
    servico = servico.lower()
    if "troca" in servico or "óleo" in servico or "freio" in servico or "suspensão" in servico:
        return "Mecanica Basica"
    elif "motor" in servico or "transmissão" in servico or "elétrica" in servico:
        return "Mecanica Avançada"
    else:
        return "Funilaria"

# Carregar dados
clientes = pd.read_csv("clientes_f_real_12k.csv")
clientes["categoria"] = clientes["tipo_servico_demandado"].apply(categorizar_servico)
oficinas = pd.read_csv("oficinas_real_nomes.csv")

# Filtros laterais
st.sidebar.title("Filtros")
regioes_disponiveis = sorted(oficinas["regiao"].dropna().unique())
regiao_selecionada = st.sidebar.selectbox("Selecione a região:", regioes_disponiveis)

oficinas_regiao = oficinas[oficinas["regiao"] == regiao_selecionada]
lista_oficinas = ["Selecione"] + list(oficinas_regiao["nome_oficina"])
oficina_sel = st.sidebar.selectbox("Escolha a oficina principal:", lista_oficinas)

raio_km = st.sidebar.slider("Raio de atuação (km):", 1, 30, 1)

if oficina_sel != "Selecione":
    oficina_principal = oficinas_regiao[oficinas_regiao["nome_oficina"] == oficina_sel].iloc[0]
    lat_o, lon_o = oficina_principal["latitude"], oficina_principal["longitude"]

    # Aplicar raio sobre toda a base
    clientes["distancia"] = distancia_km_np(lat_o, lon_o, clientes["latitude"], clientes["longitude"])
    clientes_no_raio = clientes[clientes["distancia"] <= raio_km].copy()

    oficinas["distancia"] = distancia_km_np(lat_o, lon_o, oficinas["latitude"], oficinas["longitude"])
    concorrentes = oficinas[(oficinas["nome_oficina"] != oficina_sel) & (oficinas["distancia"] <= raio_km)]

    selecionar_tudo = st.sidebar.checkbox("Selecionar todos os concorrentes", value=True)
    concorrentes_ativos = []
    st.sidebar.markdown(f"### Concorrentes no raio ({len(concorrentes)})")
    for i, row in concorrentes.iterrows():
        ativo = st.sidebar.checkbox(row["nome_oficina"], value=selecionar_tudo, key=f"chk_{i}_{row['nome_oficina']}")
        if ativo:
            concorrentes_ativos.append(row)
    concorrentes_df = pd.DataFrame(concorrentes_ativos)

    def oficina_mais_proxima(cliente):
        opcoes = [oficina_principal] + concorrentes_ativos
        candidatas = [o for o in opcoes if cliente["tipo_servico_demandado"] in eval(o["servicos_realizados"])]
        if not candidatas:
            return "Não Atendido"
        return min(candidatas, key=lambda o: distancia_km_np(cliente["latitude"], cliente["longitude"], o["latitude"], o["longitude"]))["nome_oficina"]

    clientes_no_raio["atribuida_para"] = clientes_no_raio.apply(oficina_mais_proxima, axis=1)

    total = len(clientes_no_raio)
    principal = (clientes_no_raio["atribuida_para"] == oficina_sel).sum()
    concorrentes_total = clientes_no_raio["atribuida_para"].isin(concorrentes_df["nome_oficina"]).sum() if not concorrentes_df.empty else 0

    st.metric("Clientes no raio", total)
    st.metric("Atendidos pela principal", principal)
    st.metric("Atendidos por concorrentes", concorrentes_total)

    st.subheader("Distribuição por Categoria de Serviço")
    dist_total = clientes_no_raio["categoria"].value_counts().rename("Total")
    dist_principal = clientes_no_raio[clientes_no_raio["atribuida_para"] == oficina_sel]["categoria"].value_counts().rename("Principal")
    dist_concorrente = clientes_no_raio[clientes_no_raio["atribuida_para"].isin(concorrentes_df["nome_oficina"] if not concorrentes_df.empty else [])]["categoria"].value_counts().rename("Concorrentes")
    df = pd.concat([dist_total, dist_principal, dist_concorrente], axis=1).fillna(0).astype(int)
    st.dataframe(df)

    m = folium.Map(location=[lat_o, lon_o], zoom_start=13)
    folium.Marker([lat_o, lon_o], popup="Oficina Principal", icon=folium.Icon(color="red")).add_to(m)
    folium.Circle([lat_o, lon_o], radius=raio_km*1000, color="red", fill=True, fill_opacity=0.1).add_to(m)

    for _, row in concorrentes_df.iterrows():
        folium.Marker([row["latitude"], row["longitude"]], popup=row["nome_oficina"], icon=folium.Icon(color="blue")).add_to(m)

    HeatMap(data=clientes_no_raio[["latitude", "longitude"]].sample(min(len(clientes_no_raio), 3000)).values, radius=12).add_to(m)
    folium_static(m)
else:
    st.info("Selecione uma oficina para visualizar o cenário.")
