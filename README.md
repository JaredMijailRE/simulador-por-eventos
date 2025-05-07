
# Proyecto de Modelos y Simulación – Python

Este repositorio contiene el desarrollo de un proyecto académico para la asignatura de **Modelos y Simulación**, enfocado en la generación de variables aleatorias y la implementación de modelos de simulación por eventos discretos. Todo el código está escrito en Python, con optimizaciones específicas mediante `numba` para mejorar el rendimiento computacional en procesos intensivos.

## Contenido del proyecto

El proyecto implementa distintos métodos para la generación de variables aleatorias a partir de funciones de densidad y distribución de probabilidad, incluyendo:

- 📈 **Transformada Inversa:** generación de variables a partir de su función de distribución acumulada (CDF).
- 🧩 **Método de Composición:** combinación de variables generadas a partir de subdistribuciones.
- ❌ **Método de Rechazo (Rejection Sampling):** generación eficiente para distribuciones complejas.
- 🔺 **Distribución Triangular:** generador personalizado a partir de su PDF definida.
- 📊 **Generador desde CDF definida en el intervalo [-3, 4].**
- ⏱️ **Simulación basada en eventos discretos:** construcción de modelos de eventos en el tiempo.

## Gestión de dependencias

Este proyecto utiliza [`uv`](https://github.com/astral-sh/uv), un gestor de paquetes rápido y moderno para Python. Para instalar las dependencias, simplemente ejecuta:

```bash
pip install uv
uv sync
````

## Optimización

Algunas funciones del proyecto hacen uso de `numba` para compilación Just-In-Time (JIT), lo cual acelera significativamente la ejecución en comparación con Python puro.

---

Proyecto desarrollado como parte del curso de Modelos y Simulación.
