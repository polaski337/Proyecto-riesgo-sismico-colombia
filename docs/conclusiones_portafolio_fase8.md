Analisis de resultados y conclusiones para portafolio

Fecha: 2026-08-24

## Analisis espacial del riesgo y la exposicion sismica en Colombia


## Resumen ejecutivo

Este proyecto integra datos oficiales del Servicio Geologico Colombiano, DANE, SISPRO/MinSalud e INVIAS para construir una lectura geoespacial de la amenaza sismica, la sismicidad historica y la infraestructura potencialmente expuesta en Colombia. El flujo de trabajo fue desarrollado con ArcGIS Pro, ArcPy, procesamiento geoespacial reproducible y un dashboard interactivo en Streamlit.

El analisis no constituye un modelo oficial de riesgo sismico, porque no incorpora informacion suficiente y homogenea de vulnerabilidad estructural ni estimaciones probabilistas de perdida. Por tanto, los resultados deben interpretarse como una aproximacion espacial de amenaza y exposicion potencial, util para priorizar territorios, comunicar patrones y orientar analisis posteriores mas detallados.

## Diferenciacion conceptual

- **Amenaza sismica:** condicion fisica asociada a la posible ocurrencia e intensidad del movimiento sismico. En este proyecto se representa con la clasificacion oficial del SGC y valores PGA por municipio.
- **Exposicion:** poblacion, infraestructura o activos localizados en zonas con determinado nivel de amenaza. En este proyecto se estima para IPS, sedes educativas y red vial.
- **Vulnerabilidad:** susceptibilidad de los elementos expuestos a sufrir dano. No se estima en este proyecto por falta de informacion estructural completa y comparable a escala nacional.
- **Riesgo sismico:** combinacion de amenaza, exposicion y vulnerabilidad. El proyecto usa el termino riesgo en sentido analitico y comunicativo, pero las capas derivadas propias se denominan amenaza, exposicion o priorizacion.

## Principales hallazgos

### 1. Departamentos con mayor numero de eventos sismicos

El conteo departamental se realizo mediante interseccion espacial entre eventos sismicos y limites departamentales DANE MGN 2025. Los eventos fuera de limites departamentales se conservaron en una capa separada y no se reasignaron manualmente.

| Departamento | Eventos asignados | Magnitud maxima |
|---|---:|---:|
| Santander | 4.705 | 6,77 |
| Choco | 487 | 7,10 |
| Antioquia | 407 | 6,63 |
| Valle del Cauca | 210 | 7,20 |
| Meta | 196 | 7,10 |
| Boyaca | 134 | 6,64 |
| Norte de Santander | 131 | 6,50 |
| Cundinamarca | 105 | 6,50 |
| Cesar | 88 | 5,14 |
| Huila | 81 | 7,24 |

**Interpretacion:** Santander concentra ampliamente el mayor numero de eventos asignados espacialmente, lo cual es consistente con la actividad sismica recurrente asociada al sector del nido sismico de Bucaramanga. Sin embargo, un mayor numero de eventos no implica automaticamente mayor riesgo, porque el riesgo tambien depende de exposicion, vulnerabilidad y posibles intensidades locales.

### 2. Distribucion por magnitud

| Clase de magnitud | Eventos |
|---|---:|
| 3,0 - 3,9 | 5.629 |
| 4,0 - 4,9 | 8.455 |
| 5,0 - 5,9 | 1.856 |
| 6,0 - 6,9 | 302 |
| >= 7,0 | 48 |

**Interpretacion:** La mayor parte de los eventos del catalogo se concentra entre magnitudes 3,0 y 4,9. Los eventos de magnitud igual o superior a 6,0 son menos frecuentes, pero son cartograficamente relevantes para resaltar zonas donde han ocurrido sismos de mayor energia.

### 3. Amenaza sismica municipal

| Nivel de amenaza | Municipios |
|---|---:|
| Alta | 543 |
| Intermedia | 434 |
| Baja | 136 |
| Sin dato | 9 |

**Interpretacion:** La clasificacion de amenaza muestra una alta presencia territorial de municipios en amenaza alta e intermedia. Esto justifica que el dashboard priorice la amenaza municipal como capa base, pero debe recordarse que esta capa representa peligro/amenaza, no danos esperados.

### 4. Infraestructura de salud potencialmente expuesta

Departamentos con mayor numero de IPS ubicadas en municipios de amenaza alta:

| Departamento | IPS expuestas |
|---|---:|
| Valle del Cauca | 1.934 |
| Santander | 864 |
| Narino | 803 |
| Cauca | 498 |
| Norte de Santander | 450 |
| Meta | 430 |
| Huila | 378 |
| Risaralda | 369 |

**Interpretacion:** Valle del Cauca destaca por la concentracion de IPS en municipios clasificados con amenaza alta. Este resultado debe leerse como exposicion espacial de infraestructura de salud, no como vulnerabilidad hospitalaria ni estimacion de afectacion.

### 5. Sedes educativas potencialmente expuestas

Departamentos con mayor numero de sedes educativas ubicadas en municipios de amenaza alta:

| Departamento | Sedes educativas |
|---|---:|
| Valle del Cauca | 3.440 |
| Narino | 3.044 |
| Cauca | 2.803 |
| Huila | 2.001 |
| Antioquia | 1.760 |
| Norte de Santander | 1.720 |
| Santander | 1.707 |
| Boyaca | 1.476 |

**Interpretacion:** La exposicion educativa en amenaza alta es especialmente relevante en Valle del Cauca, Narino, Cauca y Huila. Estos departamentos deberian priorizarse para analisis posteriores que incorporen caracteristicas constructivas, estado de edificaciones, ocupacion y capacidad de respuesta.

### 6. Red vial potencialmente expuesta

Departamentos con mayor longitud de red vial intersectada con municipios de amenaza alta:

| Departamento | Longitud aproximada |
|---|---:|
| Cauca | 1.499,47 km |
| Valle del Cauca | 1.105,63 km |
| Huila | 1.017,38 km |
| Santander | 979,62 km |
| Norte de Santander | 907,96 km |
| Narino | 776,04 km |
| Boyaca | 757,36 km |
| Antioquia | 726,16 km |

**Interpretacion:** Cauca presenta la mayor longitud de red vial analizada en municipios de amenaza alta. En terminos de gestion del riesgo, esta lectura puede orientar revisiones sobre conectividad, rutas de evacuacion, redundancia vial y continuidad operativa, pero no permite inferir dano fisico sobre la infraestructura.

### 7. Relacion espacial entre sismos y fallas geologicas

Se calculo la distancia geometrica desde cada evento sismico a la falla geologica cartografiada mas cercana. Los resultados permiten explorar proximidad espacial, pero no atribuyen eventos a fallas especificas.

**Interpretacion:** La proximidad espacial a fallas geologicas debe interpretarse con cautela. La cartografia de fallas representa estructuras geologicas en superficie o interpretadas, mientras que los eventos sismicos pueden originarse a diferentes profundidades y mecanismos. Para establecer relaciones causales se requeriria un analisis sismotectonico especializado.

## Zonas de priorizacion territorial

Con base en la combinacion de frecuencia sismica, amenaza alta e infraestructura expuesta, los departamentos que aparecen reiteradamente en los resultados son:

- **Santander:** mayor numero de eventos asignados y alta exposicion de IPS/sedes en amenaza alta.
- **Valle del Cauca:** alta exposicion de IPS y sedes educativas, y presencia de eventos de magnitud relevante.
- **Narino:** alta exposicion educativa y de salud en amenaza alta.
- **Cauca:** alta exposicion educativa y mayor longitud de red vial en amenaza alta.
- **Huila:** presencia de eventos de magnitud alta y exposicion significativa de infraestructura.
- **Norte de Santander y Boyaca:** combinan municipios en amenaza alta con infraestructura expuesta relevante.

Esta priorizacion es exploratoria y no debe presentarse como ranking oficial de riesgo.

## Limitaciones principales

- El catalogo de sismos descargado desde el servicio utilizado llega hasta 2020.
- Una parte importante de los eventos queda fuera de limites departamentales DANE y se conserva como no asignada.
- La amenaza SGC utilizada fue incorporada a escala municipal; no se modelo una superficie continua.
- No se integro poblacion expuesta en esta version final, aunque el flujo queda preparado para incorporarla.
- No se dispone de informacion nacional completa de vulnerabilidad estructural para IPS, colegios o red vial.
- Exposicion no equivale a afectacion, dano o perdida economica.
- La proximidad a fallas no prueba causalidad sismotectonica.

## Resumen informativo

Proyecto geoespacial desarrollado en ArcGIS Pro, ArcPy y Streamlit para analizar la amenaza sismica, la sismicidad historica y la infraestructura potencialmente expuesta en Colombia. El flujo integra datos oficiales del SGC, DANE, SISPRO/MinSalud e INVIAS, construye una geodatabase reproducible, ejecuta analisis espaciales por departamento y municipio, y publica resultados en un dashboard interactivo. El producto diferencia tecnicamente amenaza, exposicion, vulnerabilidad y riesgo, evitando presentar indicadores exploratorios como riesgo oficial.

## Metodología

El proyecto siguio un flujo reproducible en ocho fases: busqueda y verificacion de fuentes oficiales, descarga de datos, construccion de geodatabase, normalizacion de capas, analisis espacial, diseno cartografico, preparacion para publicacion web y desarrollo de dashboard. Las operaciones principales incluyeron `Spatial Join`, `Statistics`, `Intersect`, `Near`, conversion de geometria, simplificacion para publicacion web y diseno de indicadores. El dashboard permite filtrar por año, departamento, magnitud y nivel de amenaza.

## Conclusiones finales

1. La distribucion espacial de eventos muestra una concentracion marcada en Santander, pero la frecuencia de eventos no debe confundirse con riesgo.
2. La amenaza sismica alta cubre una porcion importante del territorio municipal colombiano, con 543 municipios clasificados en esta categoria.
3. Valle del Cauca, Narino, Cauca, Huila y Santander destacan por infraestructura potencialmente expuesta en amenaza alta.
4. Los resultados permiten priorizar territorios para estudios posteriores de vulnerabilidad, pero no estiman danos, perdidas ni afectacion esperada.
5. El dashboard Streamlit ofrece una herramienta clara para comunicar los hallazgos y demostrar competencias en SIG, analisis espacial, ciencia de datos geoespaciales y visualizacion profesional.
