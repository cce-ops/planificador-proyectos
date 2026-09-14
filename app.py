import streamlit as st
import pandas as pd
import networkx as nx
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import date
from pandas.tseries.offsets import CustomBusinessDay
import scipy.stats as stats
import numpy as np

st.set_page_config(page_title="Gestor PERT/Zaderenko/Gantt", layout="wide")
st.title("Planificador Avanzado de Proyectos de Ingeniería")

st.markdown("### 1. Datos de Actividades (Sucesos $i \\rightarrow j$)")
st.write("Para actividades deterministas, pon el mismo valor en los tres tiempos. Para actividades ficticias, pon duración 0.")

datos_iniciales = {
    "Actividad": ["A", "B", "C", "D", "B'", "C'"],
    "i (Origen)": [1, 1, 2, 2, 3, 4],
    "j (Destino)": [2, 3, 4, 5, 5, 5],
    "t_opt (to)": [1, 2, 3, 6, 0, 0],
    "t_prob (tm)": [1, 2, 3, 6, 0, 0],
    "t_pes (tp)": [1, 2, 3, 6, 0, 0]
}
df = pd.DataFrame(datos_iniciales)
df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

fecha_inicio = st.date_input("Fecha de inicio del proyecto", date.today())

if st.button("Calcular Proyecto Completo"):
    G = nx.DiGraph()
    # Procesar datos y calcular PERT
    for _, row in df_editado.iterrows():
        act = str(row["Actividad"]).strip()
        i = int(row["i (Origen)"])
        j = int(row["j (Destino)"])
        to, tm, tp = float(row["t_opt (to)"]), float(row["t_prob (tm)"]), float(row["t_pes (tp)"])
        
        te = (to + 4*tm + tp) / 6
        var = ((tp - to) / 6)**2
        
        G.add_edge(i, j, act=act, te=te, var=var, to=to, tm=tm, tp=tp)

    try:
        if not nx.is_directed_acyclic_graph(G):
            st.error("Error: El grafo contiene bucles (dependencias circulares).")
            st.stop()

        nodos = list(nx.topological_sort(G))
        
        # Cálculo EARLY (Hacia adelante)
        t_early = {n: 0 for n in nodos}
        for n in nodos:
            pred = list(G.predecessors(n))
            if pred:
                t_early[n] = max(t_early[p] + G[p][n]['te'] for p in pred)
                
        duracion_proyecto = t_early[nodos[-1]]
        
        # Cálculo LAST (Hacia atrás)
        t_last = {n: duracion_proyecto for n in nodos}
        for n in reversed(nodos):
            succ = list(G.successors(n))
            if succ:
                t_last[n] = min(t_last[s] - G[n][s]['te'] for s in succ)

        st.success(f"**Duración total esperada del proyecto ($T_e$):** {duracion_proyecto:.2f} días")

      # ---------------------------------------------------------
        # MATRIZ DE ZADERENKO
        # ---------------------------------------------------------
        st.markdown("### 2. Matriz de Zaderenko")
        
        # Se añade dtype=object para permitir texto vacío y números simultáneamente
        matriz = pd.DataFrame(index=nodos, columns=nodos, data="", dtype=object)
        
        for u, v, data in G.edges(data=True):
            matriz.loc[u, v] = round(data['te'], 2)
            
        matriz.loc['t_i*'] = [round(t_last[n], 2) for n in nodos]
        matriz['t_j'] = [round(t_early[n], 2) for n in nodos] + [""]
        st.dataframe(matriz, use_container_width=True)

        # ---------------------------------------------------------
        # TABLA DE RESULTADOS Y CAMINO CRÍTICO
        # ---------------------------------------------------------
        st.markdown("### 3. Tabla de Resultados y Holguras")
        tabla_res = []
        var_proyecto = 0
        actividades_criticas = []

        for u, v, data in G.edges(data=True):
            te = data['te']
            es = t_early[u]
            ef = es + te
            lf = t_last[v]
            ls = lf - te
            ht = lf - ef
            hs_i = t_last[u] - t_early[u]
            hs_j = t_last[v] - t_early[v]
            
            is_critical = abs(ht) < 1e-5
            if is_critical:
                var_proyecto += data['var']
                actividades_criticas.append(data['act'])
                
            tabla_res.append({
                "Actividad": data['act'],
                "i-j": f"{u}-{v}",
                "d_ij (te)": round(te, 2),
                "ti (ES)": round(t_early[u], 2),
                "tj (EF)": round(ef, 2),
                "ti* (LS)": round(ls, 2),
                "tj* (LF)": round(t_last[v], 2),
                "Hsi": round(hs_i, 2),
                "Hsj": round(hs_j, 2),
                "HTij": round(ht, 2),
                "CC": "CC" if is_critical else ""
            })
            
        st.dataframe(pd.DataFrame(tabla_res), use_container_width=True)

        # ---------------------------------------------------------
        # CÁLCULOS DE PROBABILIDAD (PERT)
        # ---------------------------------------------------------
        st.markdown("### 4. Probabilidad de Cumplimiento")
        desv_tipica = np.sqrt(var_proyecto)
        st.write(f"Varianza del proyecto ($\sigma^2$): **{var_proyecto:.2f}** | Desviación típica ($\sigma$): **{desv_tipica:.2f}**")
        
        col1, col2 = st.columns(2)
        with col1:
            plazo_obj = st.number_input("Plazo objetivo (días) para calcular probabilidad:", value=float(duracion_proyecto)+1)
            if desv_tipica > 0:
                z = (plazo_obj - duracion_proyecto) / desv_tipica
                prob = stats.norm.cdf(z) * 100
                st.info(f"La probabilidad de terminar en {plazo_obj} días o menos es del **{prob:.2f}%** (Z={z:.2f})")
            else:
                st.info("La varianza es 0 (proyecto totalmente determinista).")

        with col2:
            prob_obj = st.number_input("Probabilidad deseada (%) para calcular plazo:", min_value=0.1, max_value=99.9, value=95.0)
            if desv_tipica > 0:
                z_req = stats.norm.ppf(prob_obj / 100)
                plazo_req = duracion_proyecto + (z_req * desv_tipica)
                st.success(f"Para asegurar un {prob_obj}% de éxito, el plazo debe ser de **{plazo_req:.2f} días**")

        # ---------------------------------------------------------
        # CALENDARIO DE EJECUCIÓN Y GANTT
        # ---------------------------------------------------------
        st.markdown("### 5. Calendario de Ejecución y Gantt")
        bday = CustomBusinessDay(weekmask='Mon Tue Wed Thu Fri')
        fecha_ini_dt = pd.to_datetime(fecha_inicio)
        
        cal_res = []
        for res in tabla_res:
            es_d, ef_d = int(res["ti (ES)"]), int(res["tj (EF)"])
            ls_d, lf_d = int(res["ti* (LS)"]), int(res["tj* (LF)"])
            
            cal_res.append({
                "Actividad": res["Actividad"],
                "Duración": res["d_ij (te)"],
                "ES (Fecha)": (fecha_ini_dt + bday * es_d).strftime('%a %d/%m/%Y'),
                "EF (Fecha)": (fecha_ini_dt + bday * ef_d).strftime('%a %d/%m/%Y'),
                "LS (Fecha)": (fecha_ini_dt + bday * ls_d).strftime('%a %d/%m/%Y'),
                "LF (Fecha)": (fecha_ini_dt + bday * lf_d).strftime('%a %d/%m/%Y'),
                "Crítica": "Sí" if res["CC"] == "CC" else "No",
                "Inicio_Gantt": fecha_ini_dt + bday * es_d,
                "Fin_Gantt": fecha_ini_dt + bday * ef_d
            })
            
        df_cal = pd.DataFrame(cal_res)
        st.dataframe(df_cal.drop(columns=["Inicio_Gantt", "Fin_Gantt"]), use_container_width=True)

        # Filtrar actividades ficticias (duración 0) para el Gantt
        df_gantt = df_cal[df_cal["Duración"] > 0]
        fig_gantt = px.timeline(df_gantt, x_start="Inicio_Gantt", x_end="Fin_Gantt", y="Actividad", 
                                color="Crítica", color_discrete_map={"Sí": "#e74c3c", "No": "#3498db"})
        fig_gantt.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_gantt, use_container_width=True)

    except nx.NetworkXUnfeasible:
        st.error("Error estructural en el grafo.")
