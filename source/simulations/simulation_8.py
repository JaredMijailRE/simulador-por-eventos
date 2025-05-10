import random
import math

class SimuladorTaller:
    def __init__(self, tasa_llegadas_h, tiempo_servicio_med, num_reparadores, tiempo_sim_min=480, semilla=None):
        # Inicialización con posibilidad de semilla opcional
        if semilla is not None:
            random.seed(semilla)
        self.media_entre_llegadas = 60.0 / tasa_llegadas_h
        self.media_servicio = tiempo_servicio_med
        self.num_reparadores = num_reparadores
        self.tiempo_sim = tiempo_sim_min
        self.reloj = 0.0
        self.estado_servidores = [0]*num_reparadores
        self.cola = []
        self.num_eventos = 2 + num_reparadores
        self.tiempo_prox = [math.inf] * (self.num_eventos + 2)
        self.tiempo_prox[1] = 0.0                # primera llegada en t=0
        self.tiempo_prox[self.num_eventos+1] = tiempo_sim_min  # fin
        self.count_esperados = 0
        self.total_esperas = 0.0
        self.ingresos = 0.0
        self.costos = 0.0
        self.total_atendidos = 0

    def exponencial(self, beta):
        return -beta * math.log(random.random())

    def timing(self):
        # elegir próximo evento
        i = min(range(1, self.num_eventos+2), key=lambda k: self.tiempo_prox[k])
        self.reloj = self.tiempo_prox[i]
        return i

    def find_idle(self):
        # verifica si hay servidor libre
        for i, s in enumerate(self.estado_servidores):
            if s == 0:
                return i
        return None

    def arrive(self):
        # programar siguiente llegada
        self.tiempo_prox[1] = self.reloj + self.exponencial(self.media_entre_llegadas)
        # decidir si sigue dentro de tiempo
        if self.reloj <= self.tiempo_sim:
            r = self.find_idle()
            if r is not None:
                # servidor libre
                self.estado_servidores[r] = 1
                self.tiempo_prox[2+r] = self.reloj + self.exponencial(self.media_servicio)
                self.total_atendidos += 1
            else:
                # ocupados
                self.cola.append(self.reloj)

    def depart(self, idx):
        r = idx - 2
        espera = 0.0
        # verificar si hay clientes en cola
        if self.cola:
            # Atender próximo
            llegada = self.cola.pop(0)
            espera = self.reloj - llegada
            self.total_esperas += espera
            self.count_esperados += 1
            self.total_atendidos += 1
            self.tiempo_prox[idx] = self.reloj + self.exponencial(self.media_servicio)
        else:
            # No: liberar servidor
            self.estado_servidores[r] = 0
            self.tiempo_prox[idx] = math.inf
        # Umbral de espera
        if espera <= 60:
            # Cliente paga
            self.ingresos += 5
            self.costos += 3
        else:
            # Garantía
            self.costos += 3

    def run(self):
        while True:
            ev = self.timing()
            # tipo de evento
            if ev == 1:
                # llegada dentro de tiempo?
                if self.reloj <= self.tiempo_sim:
                    self.arrive()
                else:
                    break
            elif 2 <= ev < self.num_eventos+1:
                self.depart(ev)
            else:
                # fin de simulación
                break
        self.report()

    def report(self):
        demora_prom = (self.total_esperas / self.count_esperados) if self.count_esperados else 0
        neto = self.ingresos - self.costos
        print("Cola en taller electrodomésticos")
        print(f"Primera llegada: 0.000 min")
        print(f"Media entre llegadas: {self.media_entre_llegadas:.3f} ")
        print(f"Media servicio: {self.media_servicio:.3f} ")
        print(f"Fin simulacion: {self.tiempo_sim:.3f} ")
        print(f"Reparadores: {self.num_reparadores}")
        print(f"Clientes atendidos totales: {self.total_atendidos}")
        print(f"Clientes demorados: {self.count_esperados}")
        print(f"Demora promedio: {demora_prom:.3f}")
        print(f"Ingresos: $ {int(self.ingresos)}")
        print(f"Costos: $ {int(self.costos)}")
        print(f"Neto: $ {int(neto)}")

(f"{SimuladorTaller(8,5,1, semilla=1356).run()}")
print()
(f"{SimuladorTaller(16,5,1, semilla=1356).run()}")
print()
(f"{SimuladorTaller(16,5,2, semilla=1356).run()}")
print()
(f"{SimuladorTaller(8,6.48,1, semilla=1356).run()}")