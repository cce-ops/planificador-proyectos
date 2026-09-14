import streamlit as st
import pandas as pd
import networkx as nx
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import date
from pandas.tseries.offsets import CustomBusinessDay

st.set_page_config(page_title="Generador PERT/Gantt", layout="wide")
st.title("Planificador Dinámico de Proyectos de Ingeniería")

# 1. Entrada de datos interactiva
st.write("**Define las tareas, duraciones y dependencias (separadas por comas):**")
datos_iniciales = {
    "Tarea": ["A", "B", "C", "D", "E", "F"],
    "Duración": [2, 3, 3, 4, 3, 5],
    "Predecesores": ["", "A", "A", "B", "C", "D,E"]
}
df = pd.DataFrame(datos_iniciales)
df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("Calcular y Generar Diagramas"):
    G = nx.DiGraph()
    for _, row in df_editado.iterrows():
        tarea = str(row["Tarea"]).strip()
        G.add_node(tarea, dur=int(row["Duración"]))
        predecesores = str(row["Predecesores"]).split(",")
        for p in predecesores:
            p = p.strip()
            if p:
                G.add_edge(p, tarea)
                
    try:
        orden_topologico = list(nx.topological_sort(G))
        
        # 2. Cálculo hacia adelante (Tiempos Early: ti, tj)
        es, ef = {}, {}
        for nodo in orden_topologico:
            es[nodo] = max([ef[pred] for pred in G.predecessors(nodo)], default=0)
            ef[nodo] = es[nodo] + G.nodes[nodo]["dur"]
            
        duracion_total = max(ef.values())
        st.success(f"**Duración total del proyecto estimado:** {duracion_total} días")
        
        # 3. Cálculo hacia atrás (Tiempos Last: ti*, tj*)
        ls, lf = {}, {}
        for nodo in reversed(orden_topologico):
            sucesores = list(G.successors(nodo))
            if not sucesores:
                lf[nodo] = duracion_total
            else:
                lf[nodo] = min([ls[succ] for succ in sucesores])
            ls[nodo] = lf[nodo] - G.nodes[nodo]["dur"]
            
        # 4. Generación de la Tabla de Resultados (Camino Crítico)
        tabla_resultados = []
        for nodo in orden_topologico:
            ti = es[nodo]
            tj = ef[nodo]
            ti_ast = ls[nodo]
            tj_ast = lf[nodo]
            dij = G.nodes[nodo]["dur"]
            ht_ij = tj_ast - ti - dij
            
            tabla_resultados.append({
                "Actividad": nodo,
                "d_ij": dij,
                "ti (ES)": ti,
                "tj (EF)": tj,
                "ti* (LS)": ti_ast,
                "tj* (LF)": tj_ast,
                "HT_ij (Holgura)": ht_ij,
                "CC": "CC" if ht_ij == 0 else ""
            })
            
        df_resultados = pd.DataFrame(tabla_resultados)
        st.write("**Tabla de Resultados y Camino Crítico (CC)**")
        st.dataframe(df_resultados, use_container_width=True)

        # 5. Generación del Diagrama de Gantt
        fecha_inicio_proyecto = pd.to_datetime(date.today())
        # Configuración de días laborables efectivos (lunes a viernes)
        bday = CustomBusinessDay(weekmask='Mon Tue Wed Thu Fri')
        
        df_gantt = []
        for nodo in orden_topologico:
            inicio_real = fecha_inicio_proyecto + bday * int(es[nodo])
            fin_real = fecha_inicio_proyecto + bday * int(ef[nodo])
            df_gantt.append({
                "Tarea": nodo,
                "Inicio": inicio_real,
                "Fin": fin_real,
                "Camino Crítico": "Sí" if ls[nodo] - es[nodo] == 0 else "No"
            })
            
        df_plot = pd.DataFrame(df_gantt)
        fig_gantt = px.timeline(df_plot, x_start="Inicio", x_end="Fin", y="Tarea", 
                                color="Camino Crítico",
                                color_discrete_map={"Sí": "#e74c3c", "No": "#3498db"},
                                title="Diagrama de Gantt (Días laborables)")
        fig_gantt.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_gantt, use_container_width=True)

    except nx.NetworkXUnfeasible:
        st.error("Error: Se ha detectado un bucle o dependencia circular en las tareas.")