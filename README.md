# Análisis interactivo de casos de COVID-19 en México (2020)

Aplicación web hecha con **Shiny para Python** que permite explorar qué factores (demográficos, de atención médica y comorbilidades) se asocian con el fallecimiento de pacientes con sospecha o diagnóstico de COVID-19 en México durante 2020.

Proyecto XS-0130 Programación para Estadística II, Escuela de Estadística, UCR.
Autores: Dariana Calderón Sáenz, Santiago Muñoz Córdoba & Celeste Salazar.

## Datos

- **Fuente:** información abierta de casos de COVID-19 publicada por la Secretaría de Salud de México, obtenida de Kaggle ([enlace al dataset](https://www.kaggle.com/datasets/marianarfranklin/mexico-covid19-clinical-data)).
- **Muestra:** 1000 registros y 20 variables sin valores nulos; cada fila es un paciente anónimo.
- **Procesamiento:** se eliminaron 28 909 filas con datos desconocidos y se tomó una muestra aleatoria estratificada por tipo de paciente y sexo de 1000 registros. Se creó la variable `FALLECIDO`.
- **Limitaciones:** El dataset original solo incluye personas que se hicieron la prueba o recibieron atención, por lo que la mortalidad de la muestra no representa la tasa real de mortalidad de COVID-19 en México. Además, las 122 filas repetidas no se eliminaron, ya que el dataset no tiene un identificador de paciente y casi todas las variables son 1/2, por lo que perfiles idénticos aparecen de forma natural.

### Variables
En las variables sí/no, 1 = Sí, 2 = No y 97 = No aplica.

| Variable | Descripción | Codificación y detalles de la muestra |
| :--- | :--- | :--- |
| `SEX` | Sexo del paciente. | `1` = Mujer (499 registros)<br>`2` = Hombre (501 registros) |
| `AGE` | Edad del paciente en años cumplidos. | Rango numérico de `0` a `100` años. |
| `PATIENT_TYPE` | Tipo de atención médica recibida. | `1` = Ambulatorio (regresó a casa)<br>`2` = Hospitalizado |
| `INTUBED` | Indica si el paciente requirió intubación. | Aplica solo a hospitalizados; en ambulatorios toma el valor `97`. |
| `ICU` | Indica si el paciente ingresó a cuidados intensivos. | Aplica solo a pacientes hospitalizados. |
| `PNEUMONIA` | Indica si el paciente presentó neumonía. | Variable indicadora de diagnóstico clínico. |
| `PREGNANT` | Indica si la paciente está embarazada. | En pacientes hombres toma el valor `97`. |
| `DIABETES` | Indica si el paciente tiene diabetes. | Variable indicadora de antecedente clínico. |
| `COPD` | Indica si tiene enfermedad pulmonar obstructiva crónica (EPOC). | Variable indicadora de antecedente clínico. |
| `ASTHMA` | Indica si el paciente tiene asma. | Variable indicadora de antecedente clínico. |
| `INMSUPR` | Indica si el paciente presenta inmunosupresión. | Variable indicadora de antecedente clínico. |
| `HIPERTENSION` | Indica si el paciente tiene hipertensión. | Variable indicadora de antecedente clínico. |
| `OTHER_DISEASE` | Indica si el paciente presenta otra enfermedad. | Variable indicadora de antecedente clínico. |
| `CARDIOVASCULAR` | Indica si tiene una enfermedad cardiovascular. | Variable indicadora de antecedente clínico. |
| `OBESITY` | Indica si el paciente tiene obesidad. | Variable indicadora de antecedente clínico. |
| `RENAL_CHRONIC` | Indica si tiene enfermedad renal crónica. | Variable indicadora de antecedente clínico. |
| `TOBACCO` | Indica si el paciente consume tabaco. | Variable indicadora de factor de riesgo. |
| `DATE_DIED` | Fecha de fallecimiento del paciente. | Formato `AAAA-MM-DD`, o `9999-99-99` si sobrevivió.<br>Contiene **69 fechas reales** (entre `26/03/2020` y `03/09/2020`). |
| `FALLECIDO` | Variable derivada de mortalidad. | `1` si `DATE_DIED` es una fecha real.<br>Muestra: **69 fallecidos** y **931 sobrevivientes**. |
| `COVID_POSITIVO` | Resultado de diagnóstico para COVID-19. | `1` = Caso positivo.<br>Muestra: **372 positivos** y **628 no positivos**. |

## Contenido de la app

* **1. Perfil de la muestra:** Panorama demográfico y clínico general de los 1,000 pacientes (edad, sexo, tipo de atención y prevalencia de comorbilidades).
* **2. Atención médica y desenlace:** Flujo de gravedad clínica (hospitalización, UCI e intubación) y comparación de mortalidad según atención, prueba y sexo.
* **3. Edad y comorbilidades:** Relación entre el envejecimiento, la acumulación de enfermedades preexistentes y el riesgo de fallecimiento.
* **4. Evolución temporal:** Distribución mensual y acumulada de las defunciones ocurridas entre marzo y septiembre de 2020.

## Cómo ejecutarla
1. Clona el repositorio: `git clone https://github.com/Santiago-MunozC/Proyecto-Programaci-n-II.git` e ingresa a la carpeta del proyecto.
2. Instala las dependencias: `pip install -r requirements.txt`
3. Ejecuta: `shiny run app.py` y abre el enlace local que aparece en la terminal (o usa el botón ▶ en Positron, por ejemplo).

## Estructura del proyecto
```text
Proyecto-Programaci-n-II/
├── app.py                   # Une las pestañas y arranca la aplicación
├── covid_muestra_1000.xlsx  # Conjunto de datos (1,000 registros)
├── requirements.txt         # Dependencias del proyecto
└── modulos/
    ├── datos.py             # Carga y preparación de datos
    ├── tab_perfil.py        # Pestaña 1: Perfil de la muestra
    ├── tab_atencion.py      # Pestaña 2: Atención y desenlace
    ├── tab_edad.py          # Pestaña 3: Edad y comorbilidades
    └── tab_temporal.py      # Pestaña 4: Evolución temporal
```
