import numpy as np
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
import time

class SimuladorAlmacen:
    def __init__(self, params):
        # Variables de simulación, incluyendo etiquetas para estados del servidor o de la tienda
        self.QLIMIT = params['num_delays_required']
        self.BUSY = 1
        self.IDLE = 0
        self.OPEN = 1
        self.CLOSED = 0
        self.SERVICE_A = 1
        self.SERVICE_B = 2
        self.NO_SERVICE = 3
        self.next_event_type = 0
        self.num_custs_delayed = 0
        self.num_delays_required = params['num_delays_required']
        self.num_events = 0
        self.num_in_q = 0
        self.server_status = []
        # Número de servidores del simulador
        self.num_servers = params.get('num_servers', 1) 
        self.store_status = 0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        #Cálculo de ingresos diarios
        self.area_total_income = 0.0
        self.mean_interarrival = params['mean_interarrival']
        self.mean_service_A_sup = params['mean_service_A_sup']
        self.mean_service_A_inf = params['mean_service_A_inf']
        self.mean_service_B = params['mean_service_B']
        self.mean_no_service = params['mean_no_service_']
        self.prob_service_A = params['prob_service_A']
        self.prob_service_B = params['prob_service_B']
        self.sales_A = params['sales_A']
        self.sales_B = params['sales_B']
        self.sales_no_service = params['sales_no_service']
        self.service_type = 0
        self.num_service_types = 3
        self.prob_no_service_ = 1 - (self.prob_service_A + self.prob_service_B)
        self.time_limit = params['time_limit']
        self.sim_time = 0.0
        self.time_arrival = np.zeros(self.QLIMIT + 1)
        self.time_last_event = 0.0
        self.time_next_event = []
        self.total_of_delays = 0.0
        self.service_counts = np.zeros(self.num_service_types + 1)
        self.service_times = np.zeros(self.num_service_types + 1)
        self.queue_times = np.zeros(self.num_service_types + 1)
        self.sales_by_service = np.zeros(self.num_service_types + 1)
        self.service_type_arrival = np.zeros(self.QLIMIT + 1)
        self.results = {}
    
    @staticmethod
    def exponential(beta):
        'Genera un número aleatorio exponencial con parámetro beta.'
        u = np.random.rand()
        return -beta * np.log(u)

    def select_service(self):
        'Selecciona el tipo de servicio basado en las probabilidades definidas.'
        u = np.random.rand()
        if u < self.prob_service_A:
            return self.SERVICE_A
        elif u < self.prob_service_A + self.prob_service_B:
            return self.SERVICE_B
        else:
            return self.NO_SERVICE
        
    def service_time(self, service_type):
        'Calcula el tiempo de servicio basado en el tipo de servicio proporcionado.'
        if service_type == self.SERVICE_A:
            v = np.random.rand()
            return v * (self.mean_service_A_sup - self.mean_service_A_inf) + self.mean_service_A_inf
        elif service_type == self.SERVICE_B:
            return self.exponential(self.mean_service_B)
        elif service_type == self.NO_SERVICE:
            return self.mean_no_service
        else:
            print("Error: Tipo de servicio inválido", service_type)
            return 0.0
        
    def sales(self, service_type):
        'Calcula las ventas basadas en el tipo de servicio proporcionado.'
        if service_type == self.SERVICE_A:
            return self.sales_A
        elif service_type == self.SERVICE_B:
            return self.sales_B
        elif service_type == self.NO_SERVICE:
            return self.sales_no_service
        else:
            print("Error: Tipo de servicio inválido", service_type)
            return 0.0
        
    def initialize(self):
        'Inicializa las variables de la simulación.'
        self.sim_time = 0.0
        self.server_status = [self.IDLE] * self.num_servers #1 por cada servidor
        self.store_status = self.OPEN
        self.num_in_q = 0
        self.time_last_event = 0.0
        self.num_custs_delayed = 0
        self.total_of_delays = 0.0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.area_total_income = 0.0
        self.num_events = 1 + self.num_servers  # Eventos: 1 llegada + num_servers salidas
        self.time_next_event = [0.0] * (self.num_events + 1)
        self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)
        for i in range(2, self.num_events + 1):
            self.time_next_event[i] = float('inf') #Tiempo de salida por defecto
        self.service_counts = np.zeros(self.num_service_types + 1)
        self.service_times = np.zeros(self.num_service_types + 1)
        self.queue_times = np.zeros(self.num_service_types + 1)
        self.sales_by_service = np.zeros(self.num_service_types + 1)
        self.service_type_arrival = np.zeros(self.QLIMIT + 1)
        
    def timing(self):
        'Determina el próximo evento a procesar.'
        min_time_next_event = float('inf')
        self.next_event_type = 0
        for i in range(1, self.num_events + 1): #Encuentra el próximo evento
            if self.time_next_event[i] < min_time_next_event:
                min_time_next_event = self.time_next_event[i]
                self.next_event_type = i
        if self.next_event_type == 0:
            print("Lista de eventos vacía en tiempo", self.sim_time)
            return
        if min_time_next_event > self.time_limit: #Detecta cuando se cierra la tienda, evitando nuevas llegadas
            self.store_status = self.CLOSED
        # Permite que los clientes que estaban haciendo fila en el cierre sean atendidos
        self.sim_time = min_time_next_event

    def arrive(self):
        'Manejo de evento de llegada del cliente'
        if self.store_status == self.OPEN: #Solo agenda proxima llegada si la tienda está abierta
            self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)
        else:
            self.time_next_event[1] = float('inf')
        #Decide tipo de cliente
        service_type = self.select_service()
        #Encuentra servidores libres
        available_server = next((i for i, status in enumerate(self.server_status) if status == self.IDLE), None)
        
        if available_server is not None: #Inicio de servicio
            delay = 0.0
            self.total_of_delays += delay
            self.num_custs_delayed += 1
            self.server_status[available_server] = self.BUSY #Ocupa el servidor que aceptó al cliente
            service_time = self.service_time(service_type)
            departure_event = 2 + available_server #Manejo interno de arreglo de eventos
            self.time_next_event[departure_event] = self.sim_time + service_time
            self.service_counts[service_type] += 1
            self.service_times[service_type] += service_time
            sale_amount = self.sales(service_type)
            self.sales_by_service[service_type] += sale_amount
            self.area_total_income += sale_amount
        else:
            self.num_in_q += 1
            if self.num_in_q > self.QLIMIT: #Condicional incluido para evitar atascos indefinidos
                print("Overflow de la cola en tiempo", self.sim_time)
            else:
                self.time_arrival[self.num_in_q] = self.sim_time
                self.service_type_arrival[self.num_in_q] = service_type

    def depart(self):
        'Manejo de los eventos de salida'
        server_index = self.next_event_type - 2 #Indica servidor que termina servicio
        if self.num_in_q > 0:
            service_type = int(self.service_type_arrival[1])
            delay = self.sim_time - self.time_arrival[1]
            self.total_of_delays += delay
            self.num_custs_delayed += 1
            service_time = self.service_time(service_type)
            self.time_next_event[self.next_event_type] = self.sim_time + service_time
            self.service_counts[service_type] += 1
            self.service_times[service_type] += service_time
            self.queue_times[service_type] += delay
            sale_amount = self.sales(service_type)
            self.sales_by_service[service_type] += sale_amount #Se calculan los ingresos al terminar el servicio
            self.area_total_income += sale_amount
            self.num_in_q -= 1
            for i in range(1, self.num_in_q + 1):
                self.time_arrival[i] = self.time_arrival[i + 1]
                self.service_type_arrival[i] = self.service_type_arrival[i + 1]
        else:
            self.server_status[server_index] = self.IDLE
            self.time_next_event[self.next_event_type] = float('inf')

    def update_time_avg_stats(self):
        'Actualización de estadísticas por cada evento'
        time_since_last_event = self.sim_time - self.time_last_event
        self.time_last_event = self.sim_time
        self.area_num_in_q += self.num_in_q * time_since_last_event
        busy_servers = sum(status == self.BUSY for status in self.server_status)
        self.area_server_status += busy_servers * time_since_last_event

    def report(self):
        """Genera un diccionario con los resultados en lugar de imprimirlos."""
        results = {
            "general_stats": {
                "avg_delay": self.total_of_delays / self.num_custs_delayed,
                "avg_num_in_queue": self.area_num_in_q / self.sim_time,
                "server_utilization": self.area_server_status / (self.num_servers * self.sim_time),
                "total_sim_time": self.sim_time,
                "time_after_close": max(0, self.sim_time - self.time_limit),
                "total_income": self.area_total_income,
                "avg_sale_per_client": self.area_total_income / self.num_custs_delayed
            },
            "service_stats": {}
        }

        service_names = {
            self.SERVICE_A: "Servicio A (Uniforme)",
            self.SERVICE_B: "Servicio B (Exponencial)",
            self.NO_SERVICE: "Sin Servicio"
        }

        for service_type in [self.SERVICE_A, self.SERVICE_B, self.NO_SERVICE]:
            count = self.service_counts[service_type]
            if count > 0:
                results["service_stats"][service_names[service_type]] = {
                    "clients_served": int(count),
                    "total_service_time": float(self.service_times[service_type]),
                    "avg_service_time": float(self.service_times[service_type]/count),
                    "total_queue_time": float(self.queue_times[service_type]),
                    "avg_queue_time": float(self.queue_times[service_type]/count),
                    "client_proportion": float(count/self.num_custs_delayed),
                    "total_sales": float(self.sales_by_service[service_type])
                }
            else:
                results["service_stats"][service_names[service_type]] = {
                    "clients_served": 0,
                    "message": "Sin clientes"
                }

        self.results = results  # Almacenamos los resultados
        return results

    def main(self):
        self.initialize()
        while self.sim_time < self.time_limit or self.num_in_q > 0 or any(status == self.BUSY for status in self.server_status):
            self.timing()
            if self.sim_time > self.time_limit:
                self.store_status = self.CLOSED
                self.time_next_event[1] = float('inf')
            self.update_time_avg_stats()
            if self.next_event_type == 1:
                self.arrive()
            elif 2 <= self.next_event_type <= self.num_events:
                self.depart()
        return self.report()

def run_simulation_batch_d(n, mean_interarrival):
    """Versión modificada de run_simulation_batch para el reporte d"""
    results = np.zeros((n, 28), dtype=np.float64)
    
    params = {
        'num_servers': 1,  # Número fijo de servidores para este reporte
        'mean_interarrival': mean_interarrival,  # Este parámetro varía
        'mean_service_A_inf': 3.1,
        'mean_service_A_sup': 3.8,
        'mean_service_B': 7.0,
        'mean_no_service_': 1.5,
        'prob_service_A': 0.5,
        'prob_service_B': 0.3,
        'num_delays_required': 1000,
        'time_limit': 480.0,
        'sales_A': 2500,
        'sales_B': 4000,
        'sales_no_service': 0
    }
    
    for i in range(n):
        simulator = SimuladorAlmacen(params)
        sim_results = simulator.main()
        
        # Estadísticas generales (7 valores)
        general = sim_results["general_stats"]
        results[i, 0] = general["avg_delay"]
        results[i, 1] = general["avg_num_in_queue"]
        results[i, 2] = general["server_utilization"]
        results[i, 3] = general["total_sim_time"]
        results[i, 4] = general["time_after_close"]
        results[i, 5] = general["total_income"]
        results[i, 6] = general["avg_sale_per_client"]
        
        # Estadísticas por servicio (7 valores × 3 servicios = 21 valores)
        service_stats = sim_results["service_stats"]
        for j, service_type in enumerate([1, 2, 3]):
            service_name = {
                1: "Servicio A (Uniforme)",
                2: "Servicio B (Exponencial)",
                3: "Sin Servicio"
            }[service_type]
            
            stats = service_stats[service_name]
            offset = 7 + j*7
            results[i, offset] = stats["clients_served"]
            results[i, offset+1] = stats["total_service_time"]
            results[i, offset+2] = stats["avg_service_time"]
            results[i, offset+3] = stats["total_queue_time"]
            results[i, offset+4] = stats["avg_queue_time"]
            results[i, offset+5] = stats["client_proportion"]
            results[i, offset+6] = stats["total_sales"]
    
    return results

def multiple_simulation_parallel_d(nSimulations, mean_interarrival):
    """Versión modificada para el reporte d"""
    n_cpus = multiprocessing.cpu_count()
    batch_sizes = [nSimulations // n_cpus] * n_cpus
    for i in range(nSimulations % n_cpus):
        batch_sizes[i] += 1

    with ProcessPoolExecutor(max_workers=n_cpus) as executor:
        futures = [executor.submit(run_simulation_batch_d, batch_size, mean_interarrival) 
                  for batch_size in batch_sizes]
        results = np.vstack([f.result() for f in futures])

    return results.mean(axis=0), results.std(axis=0)

def generate_plots_d(interarrivals, data):
    """Genera gráficas para el reporte d (diferentes tasas de llegada)"""
    # Desempaquetar datos
    avg_delays, avg_delays_std, total_incomes, total_incomes_std, time_after_closes, time_after_closes_std, server_utils, server_utils_std, service_proportions = data
    
    # Gráfica 1: Métricas principales
    plt.figure(figsize=(14, 10))
    
    plt.subplot(2, 2, 1)
    plt.errorbar(interarrivals, avg_delays, yerr=avg_delays_std, fmt='-o', capsize=5, color='tab:blue')
    plt.title('Retraso promedio en cola')
    plt.xlabel('Tiempo entre llegadas (min)')
    plt.ylabel('Minutos')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.subplot(2, 2, 2)
    plt.errorbar(interarrivals, total_incomes, yerr=total_incomes_std, fmt='-o', capsize=5, color='tab:green')
    plt.title('Ingresos totales')
    plt.xlabel('Tiempo entre llegadas (min)')
    plt.ylabel('Dólares ($)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.subplot(2, 2, 3)
    plt.errorbar(interarrivals, time_after_closes, yerr=time_after_closes_std, fmt='-o', capsize=5, color='tab:red')
    plt.title('Tiempo operando después de cierre')
    plt.xlabel('Tiempo entre llegadas (min)')
    plt.ylabel('Minutos')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.subplot(2, 2, 4)
    plt.errorbar(interarrivals, server_utils, yerr=server_utils_std, fmt='-o', capsize=5, color='tab:purple')
    plt.title('Utilización del servidor')
    plt.xlabel('Tiempo entre llegadas (min)')
    plt.ylabel('Proporción')
    plt.ylim(0, 1)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('report_d_main_metrics.png')
    plt.close()
    
    # Gráfica 2: Proporción de servicios
    plt.figure(figsize=(10, 6))
    width = 0.25
    x = np.arange(len(interarrivals))
    
    for i, (service, color) in enumerate(zip(['A', 'B', 'Sin'], ['#2ecc71', '#3498db', '#e74c3c'])):
        plt.bar(x + i*width, service_proportions[:,i], width, label=f'Servicio {service}', 
                color=color, alpha=0.8, edgecolor='black')
    
    plt.title('Proporción de clientes por tipo de servicio')
    plt.xlabel('Tiempo entre llegadas (min)')
    plt.ylabel('Proporción')
    plt.xticks(x + width, interarrivals)
    plt.legend()
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('report_d_service_proportions.png')
    plt.close()

def generate_report_d(interarrival_times, num_simulations):
    """Genera un reporte comparativo para diferentes tasas de llegada"""
    all_means, all_stds = [], []
    interarrivals = []
    with open('simulation_11d_report.txt', 'w') as f:
        f.write("ANÁLISIS COMPARATIVO DE SIMULACIÓN - TIENDA DE ROPA (TASAS DE LLEGADA)\n")
        f.write("="*80 + "\n\n")
        f.write(f"Configuración: {num_simulations} simulaciones por tasa de llegada\n")
        f.write("Parámetros fijos:\n")
        f.write(f"- Número de servidores: 1\n- Tiempo límite: 480 min\n")
        f.write(f"- Prob Servicio A: 0.5\n- Prob Servicio B: 0.3\n")
        f.write(f"- Ventas Servicio A: $2500\n- Ventas Servicio B: $4000\n- Sin servicio: $0\n\n")
        
        for interarrival in interarrival_times:
            # Ejecutar simulaciones para esta tasa de llegada
            time_start = time.time()
            mean_results, std_results = multiple_simulation_parallel_d(num_simulations, interarrival)
            time_end = time.time()
            
            f.write(f"\nRESULTADOS PARA TIEMPO ENTRE LLEGADAS DE {interarrival} MINUTOS\n")
            f.write("-"*80 + "\n")
            
            # Escribir estadísticas generales
            f.write("\nESTADÍSTICAS GENERALES:\n")
            f.write(f"• Retraso promedio: {mean_results[0]:.2f} ± {std_results[0]:.2f} min\n")
            f.write(f"• Clientes en cola (promedio): {mean_results[1]:.2f} ± {std_results[1]:.2f}\n")
            f.write(f"• Utilización de servidores: {mean_results[2]*100:.1f}% ± {std_results[2]*100:.1f}%\n")
            f.write(f"• Tiempo total de simulación: {mean_results[3]:.1f} ± {std_results[3]:.1f} min\n")
            f.write(f"• Tiempo después del cierre: {mean_results[4]:.1f} ± {std_results[4]:.1f} min\n")
            f.write(f"• Ingresos totales: ${mean_results[5]:,.2f} ± ${std_results[5]:,.2f}\n")
            f.write(f"• Venta promedio por cliente: ${mean_results[6]:.2f} ± ${std_results[6]:.2f}\n")
            
            # Escribir estadísticas por servicio
            f.write("\nESTADÍSTICAS POR TIPO DE SERVICIO:\n")
            services = {
                1: "Servicio A (Uniforme)",
                2: "Servicio B (Exponencial)",
                3: "Sin Servicio"
            }
            
            offset = 7  # Posición donde empiezan los datos de servicios
            for serv_type in [1, 2, 3]:
                idx = offset + (serv_type-1)*7
                f.write(f"\n{services[serv_type]}:\n")
                f.write(f"  • Clientes atendidos: {mean_results[idx]:.0f} ± {std_results[idx]:.0f}\n")
                f.write(f"  • Tiempo servicio total: {mean_results[idx+1]:.1f} ± {std_results[idx+1]:.1f} min\n")
                f.write(f"  • Tiempo servicio promedio: {mean_results[idx+2]:.2f} ± {std_results[idx+2]:.2f} min\n")
                f.write(f"  • Tiempo en cola total: {mean_results[idx+3]:.1f} ± {std_results[idx+3]:.1f} min\n")
                f.write(f"  • Tiempo en cola promedio: {mean_results[idx+4]:.2f} ± {std_results[idx+4]:.2f} min\n")
                f.write(f"  • Proporción de clientes: {mean_results[idx+5]*100:.1f}% ± {std_results[idx+5]*100:.1f}%\n")
                f.write(f"  • Ventas generadas: ${mean_results[idx+6]:,.2f} ± ${std_results[idx+6]:,.2f}\n")
            
            f.write(f"\nTiempo de simulación: {time_end-time_start:.2f} segundos\n")
            f.write("-"*80 + "\n")
            interarrivals.append(interarrival)
            all_means.append(mean_results)
            all_stds.append(std_results)
    avg_delays = [m[0] for m in all_means]
    avg_delays_std = [s[0] for s in all_stds]
    total_incomes = [m[5] for m in all_means]
    total_incomes_std = [s[5] for s in all_stds]
    time_after_closes = [m[4] for m in all_means]
    time_after_closes_std = [s[4] for s in all_stds]
    server_utils = [m[2] for m in all_means]
    server_utils_std = [s[2] for s in all_stds]
    
    # Proporciones de servicios
    service_proportions = np.zeros((len(interarrivals), 3))
    for i, m in enumerate(all_means):
        total = sum(m[7 + j*7] for j in range(3))  # Suma de clientes de todos los servicios
        for j in range(3):
            service_proportions[i,j] = m[7 + j*7] / total if total > 0 else 0
    
    # Generar gráficas
    data = (avg_delays, avg_delays_std, total_incomes, total_incomes_std, 
            time_after_closes, time_after_closes_std, server_utils, server_utils_std,
            service_proportions)
    generate_plots_d(interarrivals, data)

def run_simulation_batch_e(n, servers):
    results = np.zeros((n, 28), dtype=np.float64)
    
    params = {
        'num_servers': servers,
        'mean_interarrival': 3.0,
        'mean_service_A_inf': 3.1,
        'mean_service_A_sup': 3.8,
        'mean_service_B': 7.0,
        'mean_no_service_': 1.5,
        'prob_service_A': 0.5,
        'prob_service_B': 0.3,
        'num_delays_required': 1000,
        'time_limit': 480.0,
        'sales_A': 2500,
        'sales_B': 4000,
        'sales_no_service': 0
    }
    
    for i in range(n):
        simulator = SimuladorAlmacen(params)
        sim_results = simulator.main()
        
        # Estadísticas generales (7 valores)
        general = sim_results["general_stats"]
        results[i, 0] = general["avg_delay"]
        results[i, 1] = general["avg_num_in_queue"]
        results[i, 2] = general["server_utilization"]
        results[i, 3] = general["total_sim_time"]
        results[i, 4] = general["time_after_close"]
        results[i, 5] = general["total_income"]
        results[i, 6] = general["avg_sale_per_client"]
        
        # Estadísticas por servicio (7 valores × 3 servicios = 21 valores)
        service_stats = sim_results["service_stats"]
        for j, service_type in enumerate([1, 2, 3]):
            service_name = {
                1: "Servicio A (Uniforme)",
                2: "Servicio B (Exponencial)",
                3: "Sin Servicio"
            }[service_type]
            
            stats = service_stats[service_name]
            offset = 7 + j*7
            results[i, offset] = stats["clients_served"]
            results[i, offset+1] = stats["total_service_time"]
            results[i, offset+2] = stats["avg_service_time"]
            results[i, offset+3] = stats["total_queue_time"]
            results[i, offset+4] = stats["avg_queue_time"]
            results[i, offset+5] = stats["client_proportion"]
            results[i, offset+6] = stats["total_sales"]
    
    return results

def multiple_simulation_parallel_e(nSimulations, num_servers):
    n_cpus = multiprocessing.cpu_count()
    batch_sizes = [nSimulations // n_cpus] * n_cpus
    for i in range(nSimulations % n_cpus):
        batch_sizes[i] += 1

    with ProcessPoolExecutor(max_workers=n_cpus) as executor:
        futures = [executor.submit(run_simulation_batch_e, batch_size, num_servers) 
                  for batch_size in batch_sizes]
        results = np.vstack([f.result() for f in futures])

    return results.mean(axis=0), results.std(axis=0)

def generate_plots_e(servers, data):
    """Genera gráficas para el reporte e (diferentes servidores)"""
    # Desempaquetar datos
    avg_delays, avg_delays_std, total_incomes, total_incomes_std, time_after_closes, time_after_closes_std, server_utils, server_utils_std, service_proportions = data
    
    # Gráfica 1: Métricas principales
    plt.figure(figsize=(14, 10))
    
    plt.subplot(2, 2, 1)
    plt.errorbar(servers, avg_delays, yerr=avg_delays_std, fmt='-o', capsize=5, color='tab:blue')
    plt.title('Retraso promedio en cola')
    plt.xlabel('Número de servidores')
    plt.ylabel('Minutos')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.subplot(2, 2, 2)
    plt.errorbar(servers, total_incomes, yerr=total_incomes_std, fmt='-o', capsize=5, color='tab:green')
    plt.title('Ingresos totales')
    plt.xlabel('Número de servidores')
    plt.ylabel('Dólares ($)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.subplot(2, 2, 3)
    plt.errorbar(servers, time_after_closes, yerr=time_after_closes_std, fmt='-o', capsize=5, color='tab:red')
    plt.title('Tiempo operando después de cierre')
    plt.xlabel('Número de servidores')
    plt.ylabel('Minutos')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.subplot(2, 2, 4)
    plt.errorbar(servers, server_utils, yerr=server_utils_std, fmt='-o', capsize=5, color='tab:purple')
    plt.title('Utilización promedio por servidor')
    plt.xlabel('Número de servidores')
    plt.ylabel('Proporción')
    plt.ylim(0, 1)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('report_e_main_metrics.png')
    plt.close()
    
    # Gráfica 2: Proporción de servicios
    plt.figure(figsize=(10, 6))
    width = 0.25
    x = np.arange(len(servers))
    
    for i, (service, color) in enumerate(zip(['A', 'B', 'Sin'], ['#2ecc71', '#3498db', '#e74c3c'])):
        plt.bar(x + i*width, service_proportions[:,i], width, label=f'Servicio {service}', 
                color=color, alpha=0.8, edgecolor='black')
    
    plt.title('Proporción de clientes por tipo de servicio')
    plt.xlabel('Número de servidores')
    plt.ylabel('Proporción')
    plt.xticks(x + width, servers)
    plt.legend()
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('report_e_service_proportions.png')
    plt.close()

def generate_report_e(servers_range, num_simulations):
    """Genera un reporte comparativo para diferentes números de servidores"""
    all_means, all_stds = [], []
    servers = []
    with open('simulation_11e_report.txt', 'w') as f:
        f.write("ANÁLISIS COMPARATIVO DE SIMULACIÓN - TIENDA DE ROPA\n")
        f.write("="*80 + "\n\n")
        f.write(f"Configuración: {num_simulations} simulaciones por número de servidores\n")
        f.write("Parámetros fijos:\n")
        f.write(f"- Tiempo límite: 480 min\n- Prob Servicio A: 0.5\n- Prob Servicio B: 0.3\n")
        f.write(f"- Ventas Servicio A: $2500\n- Ventas Servicio B: $4000\n- Sin servicio: $0\n\n")
        
        for num_servers in servers_range:
            # Ejecutar simulaciones para este número de servidores
            time_start = time.time()
            mean_results, std_results = multiple_simulation_parallel_e(num_simulations, num_servers)
            time_end = time.time()
            
            f.write(f"\nRESULTADOS PARA {num_servers} SERVIDOR(ES)\n")
            f.write("-"*80 + "\n")
            
            # Escribir estadísticas generales
            f.write("\nESTADÍSTICAS GENERALES:\n")
            f.write(f"• Retraso promedio: {mean_results[0]:.2f} ± {std_results[0]:.2f} min\n")
            f.write(f"• Clientes en cola (promedio): {mean_results[1]:.2f} ± {std_results[1]:.2f}\n")
            f.write(f"• Utilización de servidores: {mean_results[2]*100:.1f}% ± {std_results[2]*100:.1f}%\n")
            f.write(f"• Tiempo total de simulación: {mean_results[3]:.1f} ± {std_results[3]:.1f} min\n")
            f.write(f"• Tiempo después del cierre: {mean_results[4]:.1f} ± {std_results[4]:.1f} min\n")
            f.write(f"• Ingresos totales: ${mean_results[5]:,.2f} ± ${std_results[5]:,.2f}\n")
            f.write(f"• Venta promedio por cliente: ${mean_results[6]:.2f} ± ${std_results[6]:.2f}\n")
            
            # Escribir estadísticas por servicio
            f.write("\nESTADÍSTICAS POR TIPO DE SERVICIO:\n")
            services = {
                1: "Servicio A (Uniforme)",
                2: "Servicio B (Exponencial)",
                3: "Sin Servicio"
            }
            
            offset = 7  # Posición donde empiezan los datos de servicios
            for serv_type in [1, 2, 3]:
                idx = offset + (serv_type-1)*7
                f.write(f"\n{services[serv_type]}:\n")
                f.write(f"  • Clientes atendidos: {mean_results[idx]:.0f} ± {std_results[idx]:.0f}\n")
                f.write(f"  • Tiempo servicio total: {mean_results[idx+1]:.1f} ± {std_results[idx+1]:.1f} min\n")
                f.write(f"  • Tiempo servicio promedio: {mean_results[idx+2]:.2f} ± {std_results[idx+2]:.2f} min\n")
                f.write(f"  • Tiempo en cola total: {mean_results[idx+3]:.1f} ± {std_results[idx+3]:.1f} min\n")
                f.write(f"  • Tiempo en cola promedio: {mean_results[idx+4]:.2f} ± {std_results[idx+4]:.2f} min\n")
                f.write(f"  • Proporción de clientes: {mean_results[idx+5]*100:.1f}% ± {std_results[idx+5]*100:.1f}%\n")
                f.write(f"  • Ventas generadas: ${mean_results[idx+6]:,.2f} ± ${std_results[idx+6]:,.2f}\n")
            
            f.write(f"\nTiempo de simulación: {time_end-time_start:.2f} segundos\n")
            f.write("-"*80 + "\n")
            servers.append(num_servers)
            all_means.append(mean_results)
            all_stds.append(std_results)
    avg_delays = [m[0] for m in all_means]
    avg_delays_std = [s[0] for s in all_stds]
    total_incomes = [m[5] for m in all_means]
    total_incomes_std = [s[5] for s in all_stds]
    time_after_closes = [m[4] for m in all_means]
    time_after_closes_std = [s[4] for s in all_stds]
    server_utils = [m[2] for m in all_means]
    server_utils_std = [s[2] for s in all_stds]
    
    # Proporciones de servicios
    service_proportions = np.zeros((len(servers), 3))
    for i, m in enumerate(all_means):
        total = sum(m[7 + j*7] for j in range(3))
        for j in range(3):
            service_proportions[i,j] = m[7 + j*7] / total if total > 0 else 0
    
    # Generar gráficas
    data = (avg_delays, avg_delays_std, total_incomes, total_incomes_std, 
            time_after_closes, time_after_closes_std, server_utils, server_utils_std,
            service_proportions)
    generate_plots_e(servers, data)

if __name__ == "__main__":
    num_simulations = 1000  # Número de simulaciones por configuración
    interarrival_times = [1.5, 3.0] 
    max_servers = 5         # Número máximo de servidores a probar (1-5)
    generate_report_d(interarrival_times, num_simulations)
    generate_report_e(range(1, max_servers + 1), num_simulations)