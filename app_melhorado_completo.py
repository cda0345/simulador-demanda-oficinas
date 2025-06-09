import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
from shapely.geometry import Point
import random
import io
import os

# Obter o diretório atual do script
CURRENT_DIR = os.path.dirname(__file__)

# Função para determinar a categoria de serviço com base no nome da oficina
def get_service_category(office_name):
    office_name_lower = office_name.lower()
    if "funilaria" in office_name_lower or "pintura" in office_name_lower:
        return "Funilaria e Pintura"
    elif "pneu" in office_name_lower or "roda" in office_name_lower:
        return "Pneus e Rodas"
    elif "eletrica" in office_name_lower or "eletr" in office_name_lower:
        return "Elétrica"
    elif "mecanica" in office_name_lower or "motor" in office_name_lower:
        return "Mecânica"
    elif "freio" in office_name_lower:
        return "Freios"
    elif "suspensao" in office_name_lower:
        return "Suspensão"
    elif "ar condicionado" in office_name_lower or "ar-condicionado" in office_name_lower:
        return "Ar Condicionado"
    elif "direcao" in office_name_lower:
        return "Direção"
    elif "escapamento" in office_name_lower:
        return "Escapamento"
    elif "vidro" in office_name_lower or "parabrisa" in office_name_lower:
        return "Vidros"
    elif "insulfilm" in office_name_lower:
        return "Insulfilm"
    elif "som" in office_name_lower or "multimidia" in office_name_lower:
        return "Som e Multimídia"
    elif "acessorios" in office_name_lower:
        return "Acessórios"
    elif "revisao" in office_name_lower or "preventiva" in office_name_lower:
        return "Revisão e Manutenção Preventiva"
    elif "estetica" in office_name_lower or "lavagem" in office_name_lower or "polimento" in office_name_lower:
        return "Estética Automotiva"
    else:
        return "Outros Serviços"

# Função para determinar o serviço nível 2 com base no nome da oficina
def get_service_level2(office_name):
    office_name_lower = office_name.lower()
    if "troca de oleo" in office_name_lower:
        return "Troca de Óleo"
    elif "balanceamento" in office_name_lower or "geometria" in office_name_lower:
        return "Balanceamento e Geometria"
    elif "alinhamento" in office_name_lower:
        return "Alinhamento"
    elif "freio" in office_name_lower:
        return "Manutenção de Freios"
    elif "suspensao" in office_name_lower:
        return "Manutenção de Suspensão"
    elif "escapamento" in office_name_lower:
        return "Manutenção de Escapamento"
    elif "bateria" in office_name_lower:
        return "Troca de Bateria"
    elif "filtro" in office_name_lower:
        return "Troca de Filtros"
    elif "limpeza de bico" in office_name_lower:
        return "Limpeza de Bicos"
    elif "cambio" in office_name_lower:
        return "Manutenção de Câmbio"
    elif "motor" in office_name_lower:
        return "Manutenção de Motor"
    elif "ar condicionado" in office_name_lower or "ar-condicionado" in office_name_lower:
        return "Manutenção de Ar Condicionado"
    elif "direcao" in office_name_lower:
        return "Manutenção de Direção"
    elif "insulfilm" in office_name_lower:
        return "Instalação de Insulfilm"
    elif "som" in office_name_lower or "multimidia" in office_name_lower:
        return "Instalação de Som/Multimídia"
    elif "alarme" in office_name_lower:
        return "Instalação de Alarme"
    elif "rastreador" in office_name_lower:
        return "Instalação de Rastreador"
    elif "martelinho de ouro" in office_name_lower:
        return "Martelinho de Ouro"
    elif "polimento" in office_name_lower:
        return "Polimento"
    elif "cristalizacao" in office_name_lower or "vitrificacao" in office_name_lower:
        return "Cristalização/Vitrificação"
    elif "lavagem" in office_name_lower:
        return "Lavagem"
    else:
        return "Não Especificado"

def to_csv(df):
    """Converte DataFrame para CSV em bytes"""
    return df.to_csv(index=False).encode("utf-8")

# Configuração da página
st.set_page_config(page_title="Simulador Visual - Versão Estável", layout="wide")

# Carregar dados
@st.cache_data
def load_data():
    clientes_df = pd.read_csv(os.path.join(CURRENT_DIR, "clientes_com_segmento.csv"))
    oficinas_df = pd.read_csv(os.path.join(CURRENT_DIR, "oficinas_com_segmento.csv"))
    return clientes_df, oficinas_df

clientes_df, oficinas_df = load_data()

# Adicionar coluna de categoria de serviço e serviço nível 2 às oficinas
oficinas_df["categoria_servico"] = oficinas_df["nome_oficina"].apply(get_service_category)
oficinas_df["servico_nivel2"] = oficinas_df["nome_oficina"].apply(get_service_level2)

# Sidebar para filtros
st.sidebar.header("Filtros")

# Todas as opções disponíveis (sem filtros)
todas_zonas = oficinas_df["zona"].unique().tolist()
todos_bairros = oficinas_df["bairro"].unique().tolist()

# Filtro por Segmento
todos_segmentos = sorted(clientes_df["segmento"].unique().tolist())
selecionar_todos_segmentos = st.sidebar.checkbox("Selecionar todos os segmentos", key="chk_todos_segmentos")
segmentos_selecionados = st.sidebar.multiselect(
    "Segmentos",
    options=todos_segmentos,
    default=todos_segmentos if selecionar_todos_segmentos else []
)

# Aplicar filtros mantendo as opções disponíveis
clientes_filtrados_temp = clientes_df
oficinas_filtradas_temp = oficinas_df

# Filtro por segmento
if segmentos_selecionados:
    clientes_filtrados_temp = clientes_filtrados_temp[clientes_filtrados_temp["segmento"].isin(segmentos_selecionados)]
    oficinas_filtradas_temp = oficinas_df[oficinas_df["segmento"].apply(lambda x: any(item in x.split("_") for item in segmentos_selecionados))]

# Filtro por Zona
todas_zonas_sorted = sorted(todas_zonas)
selecionar_todas_zonas = st.sidebar.checkbox("Selecionar todas as zonas", key="chk_todas_zonas")
zona_selecionada = st.sidebar.multiselect(
    "Zonas",
    options=todas_zonas_sorted,
    default=todas_zonas_sorted if selecionar_todas_zonas else []
)

if zona_selecionada:
    clientes_filtrados_temp = clientes_filtrados_temp[clientes_filtrados_temp["zona"].isin(zona_selecionada)]
    oficinas_filtradas_temp = oficinas_filtradas_temp[oficinas_filtradas_temp["zona"].isin(zona_selecionada)]

clientes_por_zona = clientes_filtrados_temp
oficinas_por_zona = oficinas_filtradas_temp

# Filtro por Bairro - mantendo opções disponíveis
bairros_disponiveis = sorted(clientes_filtrados_temp["bairro"].unique().tolist())
selecionar_todos_bairros = st.sidebar.checkbox("Selecionar todos os bairros", key="chk_todos_bairros")
bairros_selecionados = st.sidebar.multiselect(
    "Bairros",
    options=bairros_disponiveis,
    default=bairros_disponiveis if selecionar_todos_bairros else []
)

if bairros_selecionados:
    clientes_filtrados_temp = clientes_filtrados_temp[clientes_filtrados_temp["bairro"].isin(bairros_selecionados)]
    oficinas_filtradas_temp = oficinas_filtradas_temp[oficinas_filtradas_temp["bairro"].isin(bairros_selecionados)]

clientes_filtrados = clientes_filtrados_temp
oficinas_filtradas = oficinas_filtradas_temp

# Filtro por Categoria de Serviço (Nível 1)
categorias_servico = sorted(clientes_df["nivel_1_servico"].unique().tolist())
selecionar_todas_categorias = st.sidebar.checkbox("Selecionar todas as categorias", key="chk_todas_categorias")
categorias_selecionadas = st.sidebar.multiselect(
    "Categorias de Serviço",
    options=categorias_servico,
    default=categorias_servico if selecionar_todas_categorias else []
)

if categorias_selecionadas:
    clientes_filtrados = clientes_filtrados[clientes_filtrados["nivel_1_servico"].isin(categorias_selecionadas)]
    oficinas_filtradas = oficinas_filtradas[oficinas_filtradas["categoria_servico"].isin(categorias_selecionadas)]

# Filtro por Serviço Específico (Nível 2)
servicos_nivel2 = sorted(clientes_df["nivel_2_servico"].unique().tolist())
selecionar_todos_servicos = st.sidebar.checkbox("Selecionar todos os serviços", key="chk_todos_servicos")
servicos_nivel2_selecionados = st.sidebar.multiselect(
    "Serviços Específicos",
    options=servicos_nivel2,
    default=servicos_nivel2 if selecionar_todos_servicos else []
)

if servicos_nivel2_selecionados:
    clientes_filtrados = clientes_filtrados[clientes_filtrados["nivel_2_servico"].isin(servicos_nivel2_selecionados)]
    oficinas_filtradas = oficinas_filtradas[oficinas_filtradas["servico_nivel2"].isin(servicos_nivel2_selecionados)]

# Seleção de oficinas principais - usando todas as oficinas disponíveis
oficinas_principais_nomes = st.sidebar.multiselect(
    "Selecione as oficinas principais",
    options=oficinas_df["nome_oficina"].unique().tolist()
)

# Filtra as oficinas principais baseado nos critérios selecionados
if oficinas_principais_nomes:
    # Primeiro seleciona as oficinas pelos nomes, sem aplicar outros filtros
    oficinas_principais_df = oficinas_df[oficinas_df["nome_oficina"].isin(oficinas_principais_nomes)].copy()
else:
    oficinas_principais_df = pd.DataFrame()

# Raio de busca com incremento de 0,5 km
raio_busca = st.sidebar.slider("Raio de busca (km)", 1.0, 20.0, 5.0, step=0.5)

# Inicializar variáveis vazias para evitar NameError
concorrentes_no_raio = pd.DataFrame()
concorrentes_ativos = []
centroide_lat = None
centroide_lon = None

# Calcular o centroide das oficinas principais se houver alguma selecionada
if not oficinas_principais_df.empty:
    centroide_lat = oficinas_principais_df["latitude"].mean()
    centroide_lon = oficinas_principais_df["longitude"].mean()

# Exibir informações principais
st.header("Informações Principais")

# Se tiver oficinas principais selecionadas, mostra 4 métricas, senão mostra 2
if not oficinas_principais_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clientes no Filtro", len(clientes_filtrados))
    col2.metric("Oficinas no Filtro", len(oficinas_filtradas))
    
    # Calcular clientes no raio
    clientes_no_raio_count = len(clientes_filtrados[clientes_filtrados.apply(
        lambda row: geodesic((row["latitude"], row["longitude"]), (centroide_lat, centroide_lon)).km <= raio_busca,
        axis=1
    )])
    
    # Calcular oficinas no raio (incluindo principais e concorrentes)
    oficinas_no_raio_count = len(oficinas_filtradas[oficinas_filtradas.apply(
        lambda row: geodesic((row["latitude"], row["longitude"]), (centroide_lat, centroide_lon)).km <= raio_busca,
        axis=1
    )])
    
    col3.metric("Clientes no Raio", clientes_no_raio_count)
    col4.metric("Oficinas no Raio", oficinas_no_raio_count)
else:
    col1, col2 = st.columns(2)
    col1.metric("Clientes no Filtro", len(clientes_filtrados))
    col2.metric("Oficinas no Filtro", len(oficinas_filtradas))

if not oficinas_principais_df.empty:
    st.subheader("Simulação com Oficinas Principais")

    # Exibir informações detalhadas das oficinas principais
    st.markdown("**Oficinas Principais Selecionadas:**")
    for _, oficina in oficinas_principais_df.iterrows():
        st.write(f"##### {oficina['nome_oficina']}")
        st.write(f"**Endereço:** {oficina['bairro']}, {oficina['zona']}")

    # Filtrar clientes dentro do raio do centroide
    clientes_no_raio = clientes_filtrados[clientes_filtrados.apply(
        lambda row: geodesic((row["latitude"], row["longitude"]), (centroide_lat, centroide_lon)).km <= raio_busca,
        axis=1
    )].copy()

    st.write(f"Clientes filtrados antes do raio: {len(clientes_filtrados)}") # Debug print
    st.write(f"Clientes encontrados no raio de {raio_busca:.1f} km a partir do centroide das oficinas principais: {len(clientes_no_raio)}")

    # Exibir distribuição por segmento dos clientes no raio
    st.subheader("Distribuição por Segmento (Clientes no Raio)")
    if not clientes_no_raio.empty:
        distribuicao_segmento_raio = clientes_no_raio["segmento"].value_counts().reset_index()
        distribuicao_segmento_raio.columns = ["Segmento", "Quantidade de Clientes no Raio"]
        st.table(distribuicao_segmento_raio)
    else:
        st.info("Nenhum cliente encontrado no raio para os segmentos selecionados.")

    # Encontrar concorrentes dentro do raio
    concorrentes_no_raio = oficinas_filtradas[oficinas_filtradas.apply(
        lambda row: geodesic((row["latitude"], row["longitude"]), (centroide_lat, centroide_lon)).km <= raio_busca,
        axis=1
    )].copy()

    # Remover oficinas principais da lista de concorrentes
    concorrentes_no_raio = concorrentes_no_raio[~concorrentes_no_raio["nome_oficina"].isin(oficinas_principais_nomes)]

    st.write(f"Concorrentes encontrados no raio de {raio_busca:.1f} km: {len(concorrentes_no_raio)}")

    # Exibir concorrentes no raio e permitir seleção
    st.subheader("Concorrentes no Raio")
    if not concorrentes_no_raio.empty:
        st.dataframe(concorrentes_no_raio[["nome_oficina", "segmento", "bairro", "categoria_servico", "servico_nivel2"]])

        # Seleção de concorrentes ativos para análise
        st.subheader("Selecione os Concorrentes Ativos para Análise")
        selecionar_tudo = st.checkbox("Selecionar todos os concorrentes no raio")
        concorrentes_ativos = []
        for i, row in concorrentes_no_raio.iterrows():
            ativo = st.checkbox(
                row["nome_oficina"],
                value=selecionar_tudo,
                key=f"chk_{i}_{row['nome_oficina']}"
            )
            if ativo:
                concorrentes_ativos.append(row)

        if concorrentes_ativos:
            st.write(f"Concorrentes ativos selecionados: {len(concorrentes_ativos)}")

            # Função para determinar a oficina mais próxima para cada cliente
            def oficina_mais_proxima(cliente):
                # Lista de oficinas candidatas (principais + concorrentes ativos)
                # Convertendo para lista de dicionários para facilitar a comparação por nome
                opcoes = oficinas_principais_df.to_dict("records") + [c.to_dict() for c in concorrentes_ativos]

                if not opcoes:
                    return None, float("inf")

                # Filtrar oficinas que realizam o serviço demandado pelo cliente
                candidatas = []
                for o in opcoes:
                    # Verificar se o segmento da oficina atende o segmento do cliente
                    oficina_segmentos = o["segmento"].split("_") # Assume que segmentos são separados por underscore
                    if cliente["segmento"] in oficina_segmentos:
                         # Verificar se a oficina realiza o serviço demandado pelo cliente
                        if o["categoria_servico"] == get_service_category(cliente["tipo_servico_demandado"]) or \
                           o["servico_nivel2"] == get_service_level2(cliente["tipo_servico_demandado"]):
                           candidatas.append(o)

                if not candidatas:
                    return None, float("inf") # Nenhum escritório que atenda o segmento e serviço do cliente

                min_distance = float("inf")
                closest_office = None

                for office in candidatas:
                    distance = geodesic((cliente["latitude"], cliente["longitude"]), (office["latitude"], office["longitude"])).km
                    if distance < min_distance:
                        min_distance = distance
                        closest_office = office

                return closest_office, min_distance

            # Aplicar a função para encontrar a oficina mais próxima para cada cliente no raio
            clientes_no_raio[["oficina_mais_proxima", "distancia_oficina_mais_proxima"]] = clientes_no_raio.apply(
                lambda row: pd.Series(oficina_mais_proxima(row)), axis=1
            )

            # Clientes atendidos pelas oficinas principais
            # Comparar por nome da oficina para maior robustez
            clientes_atendidos_principais = clientes_no_raio[
                clientes_no_raio["oficina_mais_proxima"].apply(lambda x: isinstance(x, dict) and x.get("nome_oficina") in oficinas_principais_df["nome_oficina"].tolist())
            ]

            # Clientes atendidos pelos concorrentes ativos
            # Comparar por nome da oficina para maior robustez
            concorrentes_ativos_nomes = [c["nome_oficina"] for c in concorrentes_ativos]
            clientes_atendidos_concorrentes = clientes_no_raio[
                clientes_no_raio["oficina_mais_proxima"].apply(lambda x: isinstance(x, dict) and x.get("nome_oficina") in concorrentes_ativos_nomes)
            ]

            st.subheader("Distribuição de Clientes Atendidos (no Raio)")

            # Distribuição por Segmento
            st.markdown("**Por Segmento:**")
            dist_segmento_principais = clientes_atendidos_principais["segmento"].value_counts().astype(int).reset_index()
            dist_segmento_principais.columns = ["Segmento", "Atendidos pelas Principais"]
            dist_segmento_concorrentes = clientes_atendidos_concorrentes["segmento"].value_counts().astype(int).reset_index()
            dist_segmento_concorrentes.columns = ["Segmento", "Atendidos pelos Concorrentes"]

            dist_segmento_combinada = pd.merge(dist_segmento_principais, dist_segmento_concorrentes, on="Segmento", how="outer").fillna(0)
            dist_segmento_combinada[["Atendidos pelas Principais", "Atendidos pelos Concorrentes"]] = \
                dist_segmento_combinada[["Atendidos pelas Principais", "Atendidos pelos Concorrentes"]].astype(int)
            st.table(dist_segmento_combinada)

            # Distribuição por Categoria de Serviço
            st.markdown("**Por Categoria de Serviço:**")
            dist_categoria_principais = clientes_atendidos_principais["tipo_servico_demandado"].apply(get_service_category).value_counts().astype(int).reset_index()
            dist_categoria_principais.columns = ["Categoria de Serviço", "Atendidos pelas Principais"]
            dist_categoria_concorrentes = clientes_atendidos_concorrentes["tipo_servico_demandado"].apply(get_service_category).value_counts().astype(int).reset_index()
            dist_categoria_concorrentes.columns = ["Categoria de Serviço", "Atendidos pelos Concorrentes"]

            dist_categoria_combinada = pd.merge(dist_categoria_principais, dist_categoria_concorrentes, on="Categoria de Serviço", how="outer").fillna(0)
            dist_categoria_combinada[["Atendidos pelas Principais", "Atendidos pelos Concorrentes"]] = \
                dist_categoria_combinada[["Atendidos pelas Principais", "Atendidos pelos Concorrentes"]].astype(int)
            st.table(dist_categoria_combinada)

            # Distribuição por Serviço Nível 2
            st.markdown("**Por Serviço Nível 2:**")
            dist_nivel2_principais = clientes_atendidos_principais["tipo_servico_demandado"].apply(get_service_level2).value_counts().astype(int).reset_index()
            dist_nivel2_principais.columns = ["Serviço Nível 2", "Atendidos pelas Principais"]
            dist_nivel2_concorrentes = clientes_atendidos_concorrentes["tipo_servico_demandado"].apply(get_service_level2).value_counts().astype(int).reset_index()
            dist_nivel2_concorrentes.columns = ["Serviço Nível 2", "Atendidos pelos Concorrentes"]

            dist_nivel2_combinada = pd.merge(dist_nivel2_principais, dist_nivel2_concorrentes, on="Serviço Nível 2", how="outer").fillna(0)
            dist_nivel2_combinada[["Atendidos pelas Principais", "Atendidos pelos Concorrentes"]] = \
                dist_nivel2_combinada[["Atendidos pelas Principais", "Atendidos pelos Concorrentes"]].astype(int)
            st.table(dist_nivel2_combinada)

            # Detalhes dos clientes no raio
            st.subheader("Detalhes dos Clientes no Raio")
            clientes_export = clientes_no_raio[["segmento", "zona", "bairro", "latitude", "longitude", "tipo_servico_demandado", "oficina_mais_proxima", "distancia_oficina_mais_proxima"]].copy()
            clientes_export["oficina_mais_proxima"] = clientes_export["oficina_mais_proxima"].apply(lambda x: x.get("nome_oficina") if isinstance(x, dict) else "Nenhuma")
            clientes_export["distancia_oficina_mais_proxima"] = clientes_export["distancia_oficina_mais_proxima"].apply(lambda x: f"{x:.1f} km" if x != float("inf") else "N/A")
            st.dataframe(clientes_export)

            # Botão para exportar clientes para CSV
            clientes_csv = to_csv(clientes_export)
            st.download_button(
                label="📊 Exportar Clientes para CSV",
                data=clientes_csv,
                file_name="clientes_no_raio.csv",
                mime="text/csv",
            )

            # Detalhes das oficinas (principais + concorrentes no raio)
            st.subheader("Detalhes das Oficinas (Principais e Concorrentes no Raio)")
            oficinas_export = pd.concat([oficinas_principais_df, pd.DataFrame(concorrentes_ativos)])
            st.dataframe(oficinas_export[["nome_oficina", "segmento", "zona", "bairro", "latitude", "longitude", "categoria_servico", "servico_nivel2"]])

            # Botão para exportar oficinas para CSV
            oficinas_csv = to_csv(oficinas_export)
            st.download_button(
                label="🏢 Exportar Oficinas para CSV",
                data=oficinas_csv,
                file_name="oficinas_no_raio.csv",
                mime="text/csv",
            )

    else:
        st.info("Nenhuma oficina principal selecionada para simulação.")

# Visualização no mapa
st.header("Visualização no Mapa")

# Criar mapa base com zoom adequado
if not oficinas_principais_df.empty:
    # Calcular o centro do mapa baseado nas oficinas selecionadas
    centro_lat = oficinas_principais_df['latitude'].mean()
    centro_lon = oficinas_principais_df['longitude'].mean()
    zoom_inicial = 12  # Zoom mais próximo para melhor visualização
else:
    # Centro padrão em São Paulo
    centro_lat = -23.5505
    centro_lon = -46.6333
    zoom_inicial = 10

# Criar mapa
mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=zoom_inicial)

# Adicionar marcadores para oficinas principais primeiro
if not oficinas_principais_df.empty:
    for _, oficina in oficinas_principais_df.iterrows():
        # Adicionar marcador
        folium.Marker(
            location=[float(oficina["latitude"]), float(oficina["longitude"])],
            popup=f'Oficina Principal: {oficina["nome_oficina"]}',
            icon=folium.Icon(color="green", icon="wrench", prefix="fa")
        ).add_to(mapa)
        
        # Adicionar círculo de raio
        folium.Circle(
            location=[float(oficina["latitude"]), float(oficina["longitude"])],
            radius=raio_busca * 1000,  # Converter km para metros
            color="green",
            fill=True,
            fillColor="green",
            fillOpacity=0.1,
            popup=f"Raio de {raio_busca} km",
            weight=2
        ).add_to(mapa)

# Adicionar heatmaps depois dos marcadores principais
if not clientes_filtrados.empty:
    # Heatmap para clientes Meoo
    if "Meoo" in segmentos_selecionados:
        meoo_clients = clientes_filtrados[clientes_filtrados["segmento"] == "Meoo"]
        if not meoo_clients.empty:
            heatmap_meoo_data = meoo_clients[["latitude", "longitude"]].values.tolist()
            folium.plugins.HeatMap(
                heatmap_meoo_data,
                gradient={0.4: "blue", 0.65: "lime", 1: "red"},
                min_opacity=0.3,
                radius=15,
                blur=15,
                max_zoom=16
            ).add_to(mapa)

    # Heatmap para clientes GF
    if "GF" in segmentos_selecionados:
        gf_clients = clientes_filtrados[clientes_filtrados["segmento"] == "GF"]
        if not gf_clients.empty:
            heatmap_gf_data = gf_clients[["latitude", "longitude"]].values.tolist()
            folium.plugins.HeatMap(
                heatmap_gf_data,
                gradient={0.4: "green", 0.65: "yellow", 1: "orange"},
                min_opacity=0.3,
                radius=15,
                blur=15,
                max_zoom=16
            ).add_to(mapa)

# Adicionar marcadores para concorrentes por último
if not oficinas_principais_df.empty and not concorrentes_no_raio.empty:
    concorrentes_ativos_nomes = [c["nome_oficina"] for c in concorrentes_ativos] if concorrentes_ativos else []
    for idx, concorrente in concorrentes_no_raio.iterrows():
        nome = concorrente["nome_oficina"]
        cor = "blue" if nome in concorrentes_ativos_nomes else "lightgray"
        folium.Marker(
            location=[concorrente["latitude"], concorrente["longitude"]],
            popup=f"Concorrente: {nome}",
            icon=folium.Icon(color=cor, icon="wrench", prefix="fa")
        ).add_to(mapa)

# Sempre exibir o mapa com dimensões adequadas
st_map = st_folium(mapa, width=800, height=600)

# Análise dos clientes atendidos pelos concorrentes
if len(concorrentes_ativos) > 0:
    clientes_atendidos_concorrentes = clientes_no_raio[clientes_no_raio.apply(
        lambda row: any(
            geodesic((row["latitude"], row["longitude"]), (conc["latitude"], conc["longitude"])).km <= raio_busca
            for conc in concorrentes_ativos
        ),
        axis=1
    )]

    # Distribuição por serviço (nível 2)
    dist_nivel2_concorrentes = clientes_atendidos_concorrentes["tipo_servico_demandado"].apply(get_service_level2).value_counts().astype(int).reset_index()
    dist_nivel2_concorrentes.columns = ["Serviço (Nível 2)", "Quantidade"]
    st.write("Distribuição por Serviço (Nível 2) - Concorrentes:")
    st.table(dist_nivel2_concorrentes)

    # Distribuição por categoria de serviço
    dist_categoria_concorrentes = clientes_atendidos_concorrentes["tipo_servico_demandado"].apply(get_service_category).value_counts().astype(int).reset_index()
    dist_categoria_concorrentes.columns = ["Categoria de Serviço", "Quantidade"]
    st.write("Distribuição por Categoria de Serviço - Concorrentes:")
    st.table(dist_categoria_concorrentes)

    # Distribuição por segmento
    dist_segmento_concorrentes = clientes_atendidos_concorrentes["segmento"].value_counts().reset_index()
    dist_segmento_concorrentes.columns = ["Segmento", "Quantidade"]
    st.write("Distribuição por Segmento - Concorrentes:")
    st.table(dist_segmento_concorrentes)


