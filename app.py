import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


st.set_page_config(
    page_title="Dashboard - Economia do Cuidado",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def carregar_dados_padrao():
    np.random.seed(42)
    estados = ['BA', 'PE', 'CE', 'AM']
    generos = ['Masculino', 'Feminino']
    racas = ['Preta/Parda', 'Branca']
    status_emprego = ['Empregado', 'Desempregado']
    anos = [2021, 2022, 2023, 2024, 2025, 2026]
    faixas_etarias = ['18-29 anos', '30-49 anos', '50+ anos']
    
    lista_dados = []
    for _ in range(2000):
        est = np.random.choice(estados)
        gen = np.random.choice(generos)
        rac = np.random.choice(racas)
        emp = np.random.choice(status_emprego)
        ano = np.random.choice(anos)
        faixa = np.random.choice(faixas_etarias)
        
        base_horas = 21.0 if gen == 'Feminino' else 11.0

        if rac == 'Preta/Parda': base_horas += 1.5
        if emp == 'Desempregado': base_horas += 3.0
        
        horas = max(2.0, np.random.normal(base_horas, 4.0))
        
        lista_dados.append({
            'Estado': est, 'Sexo': gen, 'Raça/Cor': rac, 
            'Situação de Emprego': emp, 'Ano': ano, 
            'Faixa Etária': faixa, 'Horas Semanais': round(horas, 1)
        })
    return pd.DataFrame(lista_dados)


df_base = carregar_dados_padrao()


st.sidebar.header("⚙️ Painel de Controle & Filtros")


arquivo_upload = st.sidebar.file_uploader("📂 Upload de dados (.csv)", type=["csv"])
if arquivo_upload is not None:
    df_base = pd.read_csv(arquivo_upload)
    st.sidebar.success("Dados carregados com sucesso!")


estados_disponiveis = sorted(df_base['Estado'].unique())
filtro_estados = st.sidebar.multiselect("Filtrar por Estado", estados_disponiveis, default=estados_disponiveis)

faixas_disponiveis = sorted(df_base['Faixa Etária'].unique())
filtro_faixa = st.sidebar.multiselect("Filtrar por Faixa Etária", faixas_disponiveis, default=faixas_disponiveis)

anos_disponiveis = sorted(df_base['Ano'].unique())
filtro_ano = st.sidebar.slider("Filtrar por Ano", min_value=int(min(anos_disponiveis)), max_value=int(max(anos_disponiveis)), value=int(max(anos_disponiveis)))


df_filtrado = df_base[
    (df_base['Estado'].isin(filtro_estados)) & 
    (df_base['Faixa Etária'].isin(filtro_faixa)) & 
    (df_base['Ano'] == filtro_ano)
]


st.title("📊 Indicador: Afazeres Domésticos não Remunerados")
st.markdown("### Análise de Desigualdade de Gênero, Raça e Carga de Trabalho")
st.write("---")


st.markdown("#### 📌 Indicadores Chave (KPIs)")
kpi1, kpi2, kpi3 = st.columns(3)

media_mulheres = df_filtrado[df_filtrado['Sexo'] == 'Feminino']['Horas Semanais'].mean()
media_homens = df_filtrado[df_filtrado['Sexo'] == 'Masculino']['Horas Semanais'].mean()
discrepancia = media_mulheres - media_homens

kpi1.metric("Média Mulheres (Horas/Semana)", f"{media_mulheres:.1f} hrs")
kpi2.metric("Média Homens (Horas/Semana)", f"{media_homens:.1f} hrs")
kpi3.metric("Discrepância de Gênero", f"+{discrepancia:.1f} hrs", delta_color="inverse", help="O quanto as mulheres trabalham a mais que os homens domesticamente.")

st.write("---")


col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("##### 🕒 Horas Semanais por Sexo e Estado")
    df_graf1 = df_filtrado.groupby(['Estado', 'Sexo'])['Horas Semanais'].mean().reset_index()
    fig_bar = px.bar(
        df_graf1, x='Estado', y='Horas Semanais', color='Sexo',
        barmode='group', color_discrete_sequence=['#E84855', '#1B9AAA'],
        labels={'Horas Semanais': 'Média de Horas'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_graf2:
    st.markdown("##### 📦 Distribuição de Horas (Boxplot)")
    fig_box = px.box(
        df_filtrado, x='Sexo', y='Horas Semanais', color='Raça/Cor',
        color_discrete_sequence=['#4A90E2', '#50E3C2'],
        labels={'Horas Semanais': 'Horas Dedicadas'}
    )
    st.plotly_chart(fig_box, use_container_width=True)


st.write("---")
st.markdown("##### 💼 Impacto do Status de Emprego nos Afazeres Domésticos")
df_graf3 = df_filtrado.groupby(['Situação de Emprego', 'Sexo'])['Horas Semanais'].mean().reset_index()
fig_emp = px.bar(
    df_graf3, x='Situação de Emprego', y='Horas Semanais', color='Sexo',
    barmode='group', color_discrete_sequence=['#E84855', '#1B9AAA']
)
st.plotly_chart(fig_emp, use_container_width=True)


st.write("---")
st.markdown("### 📚 Espaço Teórico: Economia do Cuidado & Carga Mental")

col_text1, col_text2 = st.columns(2)

with col_text1:
    st.info("""
    #### 🧠 A Carga Mental Feminina
    A carga mental não se limita ao trabalho físico visível (passar, cozinhar, limpar). Ela engloba todo o **gerenciamento invisível** do lar: planejar as refeições, listar compras, lembrar de consultas médicas e coordenar rotinas familiares. Estudos indicam que essa responsabilidade de planejamento recai majoritariamente sobre as mulheres, gerando exaustão psicológica mesmo quando as tarefas físicas são parcialmente divididas.
    """)

    st.image("https://imagenes.elpais.com/resizer/v2/ZNY34QBAKGVFNWOKFY5RSNCAIA.jpg?auth=e9ca2ea230f61ca573efa44c18dd5f20c70330de04abcfbaed87ee216618d744&width=414", caption="Gestão invisível do lar e o impacto na saúde mental.")

with col_text2:
    st.success("""
    #### 💰 A Economia do Cuidado
    A Economia do Cuidado estuda o valor econômico de atividades voltadas a cuidar de pessoas, reprodução social e manutenção doméstica. Historicamente invisibilizado, esse ecossistema de trabalho não remunerado funciona como um subsídio indireto para o mercado de trabalho convencional. Se as horas dedicadas aos afazeres domésticos fossem monetizadas, representariam uma fatia massiva do PIB nacional.
    """)
  
    st.image("https://s2-globo-gente.glbimg.com/EM-vGLp9c6Hzvzsfj1v7w9UVN-0=/0x0:650x650/924x0/smart/filters:strip_icc()/i.s3.glbimg.com/v1/AUTH_4b610c20fdd043e897c535bcf008e64c/internal_photos/bs/2026/0/B/lGG17WSWKNEhJ01sWYXQ/economia-cuidado-header-gente-2.png", caption="A base invisível que sustenta a estrutura socioeconômica produtiva.")
