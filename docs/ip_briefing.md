# Lung Cancer AI Platform
## Resumen ejecutivo para IP

**Autor:** Lucas Chabrera Querol

### 1) Proposito
Esta plataforma muestra, de forma reproducible, como transformar datos reales de cancer de pulmon en hipotesis priorizadas para investigacion.

No sustituye la validacion experimental del laboratorio. Su valor es reducir tiempo de exploracion inicial y enfocar recursos en candidatos con mayor señal.

---

### 2) Que hace la web
La web organiza el flujo en cuatro areas:

1. **Visor de pipeline**
   - Muestra estado de ejecucion y artefactos generados.
2. **Trazabilidad de datos**
   - Indica fuentes configuradas y manifiesto de descargas (URL, ruta local, hash).
3. **Priorizacion de dianas**
   - Presenta ranking generado por modelos de IA baseline.
4. **Carga de datos (demo)**
   - Permite subir un CSV/TSV real para obtener un ranking exploratorio inmediato.

---

### 3) Tecnologias y enfoque
- Python + Streamlit.
- IA baseline: RandomForest + ElasticNet.
- Datos publicos reales y trazables.
- Ejecucion local o en infraestructura del laboratorio.

---

### 4) Datos utilizados en la demo actual
- TCGA LUAD/LUSC (UCSC Xena, descarga publica).
- No se usan datos inventados ni mockups.

---

### 5) Nivel de evidencia (clave para interpretacion)
La plataforma diferencia tres niveles:

1. **Exploratorio**
   - Hallazgo inicial en un dataset.
2. **Reproducido computacionalmente**
   - Resultado consistente en corridas reproducibles.
3. **Validado experimentalmente**
   - Confirmacion por el laboratorio en modelos preclinicos.

La demo actual muestra resultados en niveles 1 y 2. El nivel 3 depende del laboratorio.

---

### 6) Valor para el grupo de Innovacion Terapeutica
La herramienta se alinea con los objetivos del grupo en:
- Priorizacion de nuevas dianas.
- Exploracion de mecanismos de resistencia.
- Preparacion de hipotesis para combinaciones terapeuticas.

Ventaja operativa:
- Menos tiempo en cribado inicial.
- Mayor trazabilidad y reproducibilidad.
- Mejor base para decidir que validar primero.

---

### 7) Privacidad y adopcion
La plataforma puede ejecutarse:
- En local.
- En servidor interno del centro.

No requiere exponer datos sensibles a servicios externos para su uso real.

---

### 8) Estado actual del proyecto
**Estado:** MVP funcional y demostrable.

Incluye:
- Flujo de descarga, preprocesado e integracion.
- Dashboard navegable.
- Ranking de candidatos.
- Trazabilidad de fuentes y artefactos.

---

### 9) Siguiente paso propuesto con el laboratorio
Adaptar el pipeline a endpoints propios del grupo (respuesta a tratamiento, resistencia basal/adquirida, datos internos) para convertir priorizacion computacional en shortlist experimental de alto valor.

---

### 10) Mensaje final para IP
Este proyecto ya demuestra utilidad potencial real como capa de priorizacion computacional reproducible. El impacto final depende de la integracion con datos y validaciones del propio laboratorio.
