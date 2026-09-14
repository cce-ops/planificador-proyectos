import streamlit as st
import pandas as pd
import networkx as nx
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import date
from pandas.tseries.offsets import CustomBusinessDay
import scipy.stats as stats
import numpy as np

st.set_page_config(page_title="Gestor PERT/Gantt Unificado", layout="wide")
st.title("Planificador de Proyectos de Ingeniería")

# Crear pestañas para separar los niveles de dificultad
tab1, tab2 = st.tabs(["Modo Básico (Actividades y Precedencias)", "Modo Avanzado (Nodos y Método Zaderenko)"])

# -----------------------------------------------------------------------------
# PESTAÑA 1: MODO BÁSICO (ACTIVITY ON NODE)
# -----------------------------------------------------------------------------
with tab1:
    st.markdown("### 1. Datos de Entrada (Modo Básico)")
    datos_basicos = {
        "Tarea": ["A", "B", "C", "D", "E", "F"],
        "Duración": [2, 3, 3, 4, 3, 5],
        "Predecesores": ["", "A", "A", "B", "C", "D,E"]
    }
    df_basico = pd.DataFrame(datos_basicos)
    df_editado_basico = st.data_editor(df_basico, num_rows="dynamic", use_container_width=True, key="tabla_basica")

    if st.button("Calcular Proyecto Básico", key="btn_basico"):
        G_basico = nx.DiGraph()
        for _, row in df_editado_basico.iterrows():
            tarea = str(row["Tarea"]).strip()
            G_basico.add_node(tarea, dur=int(row["Duración"]))
            predecesores = str(row["Predecesores"]).split(",")
            for p in predecesores:
                p = p.strip()
                if p:
                    G_basico.add_edge(p, tarea)
                    
        try:
            orden_topologico = list(nx.topological_sort(G_basico))
            
            es, ef = {}, {}
            for nodo in orden_topologico:
                es[nodo] = max([ef[pred] for pred in G_basico.predecessors(nodo)], default=0)
                ef[nodo] = es[nodo] + G_basico.nodes[nodo]["dur"]
                
            duracion_total = max(ef.values())
            st.success(f"**Duración total del proyecto:** {duracion_total} días laborables")
            
            ls, lf = {}, {}
            for nodo in reversed(orden_topologico):
                sucesores = list(G_basico.successors(nodo))
                if not sucesores:
                    lf[nodo] = duracion_total
                else:
                    lf[nodo] = min([ls[succ] for succ in sucesores])
                ls[nodo] = lf[nodo] - G_basico.nodes[nodo]["dur"]
                
            # Tabla de Resultados
            tabla_basica_res = []
            for nodo in orden_topologico:
                ht = lf[nodo] - es[nodo] - G_basico.nodes[nodo]["dur"]
                tabla_basica_res.append({
                    "Actividad": nodo, "d_ij": G_basico.nodes[nodo]["dur"],
                    "ES": es[nodo], "EF": ef[nodo], "LS": ls[nodo], "LF": lf[nodo],
                    "Holgura": ht, "CC": "Sí" if ht == 0 else ""
                })
            st.dataframe(pd.DataFrame(tabla_basica_res), use_container_width=True)

            col1_bas, col2_bas = st.columns(2)
            # Gantt
            with col1_bas:
                bday = CustomBusinessDay(weekmask='Mon Tue Wed Thu Fri')
                fecha_ini = pd.to_datetime(date.today())
                gantt_data = []
                for nodo in orden_topologico:
                    gantt_data.append({
                        "Tarea": nodo,
                        "Inicio": fecha_ini + bday * int(es[nodo]),
                        "Fin": fecha_ini + bday * int(ef[nodo]),
                        "Crítica": "Sí" if ls[nodo] - es[nodo] == 0 else "No"
                    })
                fig_gantt_b = px.timeline(pd.DataFrame(gantt_data), x_start="Inicio", x_end="Fin", y="Tarea", 
                                        color="Crítica", color_discrete_map={"Sí": "#e74c3c", "No": "#3498db"})
                fig_gantt_b.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_gantt_b, use_container_width=True)
                
            # Grafo PERT Básico
            with col2_bas:
                fig, ax = plt.subplots(figsize=(6, 4))
                posiciones = nx.spring_layout(G_basico, seed=42)
                criticos = [n for n in orden_topologico if ls[n] - es[n] == 0]
                colores = ["#e74c3c" if n in criticos else "#3498db" for n in G_basico.nodes()]
                nx.draw(G_basico, posiciones, with_labels=True, node_size=2000, node_color=colores, 
                        font_weight="bold", edge_color="gray", arrows=True, ax=ax)
                st.pyplot(fig)

        except nx.NetworkXUnfeasible:
            st.error("Error: Bucle detectado en las precedencias.")


# -----------------------------------------------------------------------------
# PESTAÑA 2: MODO AVANZADO (ACTIVITY ON ARROW & ZADERENKO)
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("### 1. Datos de Actividades Sucesos (i $\\rightarrow$ j)")
    datos_avanzados = {
        "Actividad": ["A", "B", "C", "D", "B'", "C'"],
        "i (Origen)": [1, 1, 2, 2, 3, 4],
        "j (Destino)": [2, 3, 4, 5, 5, 5],
        "t_opt": [1, 2, 3, 6, 0, 0],
        "t_prob": [1, 2, 3, 6, 0, 0],
        "t_pes": [1, 2, 3, 6, 0, 0]
    }
    df_avanz = pd.DataFrame(datos_avanzados)
    df_editado_avanz = st.data_editor(df_avanz, num_rows="dynamic", use_container_width=True, key="tabla_avanzada")

    if st.button("Calcular Proyecto Avanzado", key="btn_avanz"):
        G_avanz = nx.DiGraph()
        for _, row in df_editado_avanz.iterrows():
            act = str(row["Actividad"]).strip()
            i, j = int(row["i (Origen)"]), int(row["j (Destino)"])
            to, tm, tp = float(row["t_opt"]), float(row["t_prob"]), float(row["t_pes"])
            te = (to + 4*tm + tp) / 6
            var = ((tp - to) / 6)**2
            G_avanz.add_edge(i, j, act=act, te=te, var=var)

        try:
            nodos = list(nx.topological_sort(G_avanz))
            
            # Tiempos Sucesos
            t_early = {n: 0 for n in nodos}
            for n in nodos:
                pred = list(G_avanz.predecessors(n))
                if pred:
                    t_early[n] = max(t_early[p] + G_avanz[p][n]['te'] for p in pred)
            
            duracion_proy = t_early[nodos[-1]]
            
            t_last = {n: duracion_proy for n in nodos}
            for n in reversed(nodos):
                succ = list(G_avanz.successors(n))
                if succ:
                    t_last[n] = min(t_last[s] - G_avanz[n][s]['te'] for s in succ)

            # Resultados y Camino Crítico
            tabla_res_avanz = []
            var_proy = 0
            
            for u, v, data in G_avanz.edges(data=True):
                te = data['te']
                es, ef = t_early[u], t_early[u] + te
                lf, ls = t_last[v], t_last[v] - te
                ht = lf - ef
                is_critical = abs(ht) < 1e-5
                
                if is_critical:
                    var_proy += data['var']
                    G_avanz[u][v]['is_critical'] = True
                else:
                    G_avanz[u][v]['is_critical'] = False
                    
                tabla_res_avanz.append({
                    "Actividad": data['act'], "i-j": f"{u}-{v}", "te": round(te, 2),
                    "ti": round(t_early[u], 2), "tj": round(ef, 2),
                    "ti*": round(ls, 2), "tj*": round(t_last[v], 2),
                    "Hsi": round(t_last[u] - t_early[u], 2), "Hsj": round(t_last[v] - t_early[v], 2),
                    "HTij": round(ht, 2), "CC": "CC" if is_critical else ""
                })

            st.success(f"**Duración total esperada ($T_e$):** {duracion_proy:.2f} días")
            
            # Gráficos y Tablas
            col1_a, col2_a = st.columns(2)
            
            with col1_a:
                st.markdown("**Matriz de Zaderenko**")
                matriz = pd.DataFrame(index=nodos, columns=nodos, data="", dtype=object)
                for u, v, data in G_avanz.edges(data=True):
                    matriz.loc[u, v] = round(data['te'], 2)
                matriz.loc['t_i*'] = [round(t_last[n], 2) for n in nodos]
                matriz['t_j'] = [round(t_early[n], 2) for n in nodos] + [""]
                st.dataframe(matriz, use_container_width=True)

                st.markdown("**Tabla de Resultados**")
                st.dataframe(pd.DataFrame(tabla_res_avanz), use_container_width=True)
                
                st.markdown("**Probabilidad de Cumplimiento (Estadística)**")
                desv = np.sqrt(var_proy)
                st.write(f"Varianza ($\sigma^2$): {var_proy:.2f} | Desviación ($\sigma$): {desv:.2f}")
                plazo_obj = st.number_input("Plazo objetivo (días):", value=float(duracion_proy)+1)
                if desv > 0:
                    prob = stats.norm.cdf((plazo_obj - duracion_proy) / desv) * 100
                    st.info(f"Probabilidad de éxito: **{prob:.2f}%**")
                
            with col2_a:
                st.markdown("**Diagrama PERT (Sucesos y Actividades)**")
                fig_a, ax_a = plt.subplots(figsize=(8, 5))
                pos_a = nx.spring_layout(G_avanz, seed=42)
                
                nx.draw_networkx_nodes(G_avanz, pos_a, node_size=1200, node_color="#f1f2f6", edgecolors="black", ax=ax_a)
                nx.draw_networkx_labels(G_avanz, pos_a, font_size=10, font_weight="bold", ax=ax_a)
                
                edge_colors = ['red' if G_avanz[u][v]['is_critical'] else 'gray' for u, v in G_avanz.edges()]
                nx.draw_networkx_edges(G_avanz, pos_a, edge_color=edge_colors, arrows=True, node_size=1200, ax=ax_a)
                
                edge_labels = {(u, v): G_avanz[u][v]['act'] for u, v in G_avanz.edges()}
                nx.draw_networkx_edge_labels(G_avanz, pos_a, edge_labels=edge_labels, font_color='blue', ax=ax_a)
                
                st.pyplot(fig_a)

                st.markdown("**Diagrama de Gantt**")
                bday = CustomBusinessDay(weekmask='Mon Tue Wed Thu Fri')
                fecha_ini_dt = pd.to_datetime(date.today())
                cal_res = []
                for res in tabla_res_avanz:
                    if res["te"] > 0:
                        cal_res.append({
                            "Actividad": res["Actividad"],
                            "Inicio": fecha_ini_dt + bday * int(res["ti"]),
                            "Fin": fecha_ini_dt + bday * int(res["tj"]),
                            "Crítica": "Sí" if res["CC"] == "CC" else "No"
                        })
                fig_gantt_a = px.timeline(pd.DataFrame(cal_res), x_start="Inicio", x_end="Fin", y="Actividad", 
                                        color="Crítica", color_discrete_map={"Sí": "#e74c3c", "No": "#3498db"})
                fig_gantt_a.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_gantt_a, use_container_width=True)

        except nx.NetworkXUnfeasible:
            st.error("Error estructural en el grafo.")
