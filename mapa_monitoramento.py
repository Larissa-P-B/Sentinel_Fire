import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap, Fullscreen
import random
import time
import os
import threading
from typing import Tuple, Dict


class MapaMonitoramento:
    def __init__(self, sistema):
        self.sistema = sistema
        self.regioes_geometrias = self._definir_regioes()
        self.mapa = self._inicializar_mapa()
        self.markers = []
        self.iniciar_simulacao()

    def _definir_regioes(self) -> Dict[str, Dict]:
        return {
            "Amazônia": {'centro': (-3.4653, -62.2159), 'bounds': [(-10, -74), (5, -50)]},
            "Pantanal": {'centro': (-17.6797, -57.4518), 'bounds': [(-20, -60), (-15, -55)]},
            "Cerrado": {'centro': (-15.8271, -47.2422), 'bounds': [(-20, -55), (-10, -40)]},
            "Mata Atlântica": {'centro': (-22.9519, -43.2105), 'bounds': [(-25, -48), (-15, -38)]}
        }

    def _inicializar_mapa(self) -> folium.Map:
        mapa = folium.Map(
            location=[-14.2350, -51.9253],
            zoom_start=4,
            tiles='https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
            attr='OpenStreetMap'
        )

        self.heatmap = HeatMap(data=[], name='Intensidade de Fogo', min_opacity=0.6,
                               radius=25, blur=15, gradient={
                                   0.4: 'blue', 0.6: 'lime',
                                   0.7: 'yellow', 0.8: 'orange', 1.0: 'red'
                               }).add_to(mapa)

        self.marker_cluster = MarkerCluster(name="Focos de Incêndio").add_to(mapa)

        self._adicionar_regioes(mapa)

        Fullscreen(position='topright').add_to(mapa)
        MiniMap(position='bottomleft').add_to(mapa)
        folium.LayerControl().add_to(mapa)

        return mapa

    def _adicionar_regioes(self, mapa):
        for regiao, info in self.regioes_geometrias.items():
            folium.Rectangle(
                bounds=info['bounds'],
                color='#3186cc',
                fill=True,
                fill_color='#3186cc',
                fill_opacity=0.1,
                popup=f"<b>Região {regiao}</b>",
                tooltip=regiao
            ).add_to(mapa)

    def _gerar_posicao_realista(self, regiao: str) -> Tuple[float, float]:
        bounds = self.regioes_geometrias.get(regiao, {}).get('bounds', [])
        if bounds:
            return (
                random.uniform(bounds[0][0], bounds[1][0]),
                random.uniform(bounds[0][1], bounds[1][1])
            )
        return self.regioes_geometrias[regiao]['centro']

    def _criar_marcador_fogo(self, ocorrencia):
        lat, lng = self._gerar_posicao_realista(ocorrencia.regiao)
        cor = 'orange' if ocorrencia.severidade <= 2 else 'red' if ocorrencia.severidade <= 4 else 'black'

        popup_html = f"""
        <div style="width: 250px;">
            <h4 style="color: {cor}; margin: 5px 0;">Fogo #{ocorrencia.id}</h4>
            <p><b>Local:</b> {ocorrencia.local}</p>
            <p><b>Região:</b> {ocorrencia.regiao}</p>
            <p><b>Severidade:</b> <span style="color: {cor}">{ocorrencia.severidade}/5</span></p>
            <p><b>Status:</b> {ocorrencia.status}</p>
        </div>
        """
        return folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=cor, icon='fire', prefix='fa'),
            tooltip=f"Fogo {ocorrencia.id} - {ocorrencia.regiao}"
        )

    def limpar_marcadores(self):
        self.marker_cluster._children.clear()
        self.markers.clear()

    def atualizar_simulacao(self):
        self.limpar_marcadores()
        heatmap_data = []

        for ocorrencia in self.sistema.fila_prioritaria:
            if ocorrencia.status == "Fogo ativo":
                marker = self._criar_marcador_fogo(ocorrencia)
                marker.add_to(self.marker_cluster)
                self.markers.append(marker)
                lat, lng = marker.location
                heatmap_data.append([lat, lng, ocorrencia.severidade * 2])

        self.heatmap.data = heatmap_data

    def adicionar_marcador(self, lat, lon, cor='red', popup=''):
        icone = {
            'red': ('fire', 'red'),
            'green': ('check', 'green'),
            'blue': ('truck', 'blue')
        }.get(cor, ('info-sign', 'gray'))

        folium.Marker(
            [lat, lon],
            popup=popup,
            icon=folium.Icon(color=icone[1], icon=icone[0], prefix='fa')
        ).add_to(self.mapa)

    def iniciar_simulacao(self):
        def simular():
            while True:
                try:
                    self.atualizar_simulacao()
                except Exception as e:
                    print(f"Erro ao atualizar mapa: {e}")
                time.sleep(3)

        threading.Thread(target=simular, daemon=True).start()

    def salvar_mapa(self, arquivo='templates/monitoramento.html'):
        os.makedirs(os.path.dirname(arquivo), exist_ok=True)
        self.mapa.save(arquivo)
        return arquivo

