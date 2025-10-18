# Windundis - Financial Assistant

Una aplicación web inteligente que combina análisis financiero con IA para ayudar a los usuarios a gestionar sus finanzas personales de manera más efectiva.

## Características Principales

### Análisis Financiero Inteligente
- **Análisis automático de transacciones bancarias** con clasificación inteligente
- **Perfil financiero personalizado** basado en patrones de gasto
- **Gráficos interactivos** para visualizar tendencias financieras
- **Recomendaciones personalizadas** de ahorro e inversión

### Asistente de IA
- **Chat financiero** con modelos de IA especializados (ALIA-40b, Salamandra)
- **Análisis de hábitos financieros** con insights personalizados
- **Creación de planes de ahorro** adaptados a cada usuario
- **Mensajes motivacionales** para mantener el progreso hacia metas

### Integración Bancaria
- **API de Redsys** para acceso seguro a datos bancarios
- **Autenticación OAuth2** con BancSabadell
- **Gestión de pagos** y transferencias
- **Consulta de estados** de transacciones en tiempo real

### Visualización de Datos
- **Gráficos interactivos** con Plotly
- **Dashboard personalizado** con métricas clave
- **Análisis de presupuesto 50-30-20**
- **Tendencias de ahorro** y proyecciones

## Tecnologías Utilizadas

### Backend
- **Python 3.14** - Lenguaje principal
- **Flask** - Framework web
- **Flask-CORS** - Manejo de CORS
- **Requests** - Cliente HTTP para APIs

### Análisis y Visualización
- **Matplotlib** - Gráficos estáticos
- **Seaborn** - Visualizaciones estadísticas
- **Plotly** - Gráficos interactivos
- **Pandas** - Manipulación de datos
- **NumPy** - Cálculos numéricos

### IA y Machine Learning
- **ALIA-40b** - Modelo de IA para análisis financiero
- **Salamandra-7b** - Modelo para simplificación y chat
- **PublicAI API** - Servicio de IA en la nube

### Frontend
- **HTML5/CSS3** - Estructura y estilos
- **JavaScript** - Interactividad
- **Font Awesome** - Iconografía

### DevOps
- **Docker** - Containerización
- **Python-dotenv** - Gestión de variables de entorno

## Requisitos del Sistema

- Python 3.14+
- Docker (opcional)
- Navegador web moderno
- Acceso a internet para APIs de IA

## Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd Windundis
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno
Crear el archivo `redsys.env` con las siguientes variables:

```env
# Configuración de Redsys/BancSabadell
CLIENT_ID=tu_client_id
SECOND_CLIENT_ID=tu_second_client_id
SCOPE=psd2
STATE=random_state
REDIRECT_URI=http://localhost:8080
CODE_CHALLENGE=tu_code_challenge
CODE_CHALLENGE_METHOD=S256
CODE_VERIFIER=tu_code_verifier
RESPONSE_TYPE=code
```

### 4. Ejecutar la Aplicación

#### Opción A: Ejecución Directa
```bash
python app.py
```

#### Opción B: Con Docker
```bash
# Construir la imagen
docker build -t windundis .

# Ejecutar el contenedor
docker run -p 8080:8080 windundis
```

### 5. Acceder a la Aplicación
Abrir el navegador y navegar a: `http://localhost:8080`

## Estructura del Proyecto

```
Windundis/
├── app.py                 # Aplicación principal Flask
├── ai_service.py          # Servicio de IA para análisis financiero
├── charts.py              # Generador de gráficos financieros
├── RedsysClient.py        # Cliente para API de Redsys
├── requirements.txt       # Dependencias de Python
├── Dockerfile            # Configuración de Docker
├── redsys.env            # Variables de entorno (crear)
├── data.json             # Datos de ejemplo
├── model/
│   ├── ALIA40b.py        # Modelo de IA para análisis
│   └── dividir_en_tareas_pequnia.py
├── static/
│   ├── script.js         # JavaScript del frontend
│   └── style.css         # Estilos CSS
├── templates/
│   └── index.html        # Plantilla HTML principal
└── README.md             # Este archivo
```

## API Endpoints

### Autenticación Bancaria
- `POST /api/login` - Obtener URL de autorización
- `POST /api/token` - Intercambiar código por token de acceso

### Gestión de Pagos
- `POST /api/payment/create` - Crear solicitud de pago
- `POST /api/payment/status` - Consultar estado de pago

### Análisis Financiero
- `POST /api/analyze` - Analizar datos bancarios y generar reportes

### Servicios de IA
- `POST /api/ai/chat` - Chat con asistente financiero
- `POST /api/ai/analyze-habits` - Análisis de hábitos financieros
- `POST /api/ai/savings-plan` - Crear plan de ahorro personalizado
- `POST /api/ai/motivation` - Obtener mensaje motivacional
- `POST /api/ai/subtasks` - Dividir metas en subtareas
- `POST /api/ai/suggest-tasks` - Sugerir tareas financieras
- `POST /api/ai/create-smart-goal` - Crear metas SMART

## Funcionalidades Detalladas

### Análisis de Transacciones
- **Clasificación automática** de gastos por categorías
- **Detección de patrones** de gasto y ahorro
- **Análisis de volatilidad** financiera
- **Identificación de oportunidades** de optimización

### Perfil Financiero
- **Clasificación de usuario** (Ahorrador, Equilibrado, etc.)
- **Análisis de presupuesto 50-30-20**
- **Métricas de salud financiera**
- **Recomendaciones personalizadas**

### Visualizaciones
- **Gráfico circular** de distribución de gastos
- **Gráfico de barras** ingresos vs gastos
- **Tendencias de ahorro** con proyecciones
- **Gráfico radar** del perfil financiero
- **Recomendaciones de ahorro** visuales

## Seguridad

- **Autenticación OAuth2** con bancos
- **Tokens de acceso** seguros
- **Validación de datos** en todas las entradas
- **Manejo seguro** de información financiera
- **CORS configurado** para desarrollo

## Datos de Prueba

El proyecto incluye un archivo `data.json` con datos de ejemplo para testing y desarrollo.

## Docker

### Construir Imagen
```bash
docker build -t windundis .
```

### Ejecutar Contenedor
```bash
docker run -p 8080:8080 windundis
```

### Variables de Entorno en Docker
```bash
docker run -p 8080:8080 --env-file redsys.env windundis
```

## Configuración de Desarrollo

### Variables de Entorno Requeridas
- `CLIENT_ID` - ID del cliente de Redsys
- `SECOND_CLIENT_ID` - Segundo ID de cliente
- `SCOPE` - Alcance de permisos (psd2)
- `REDIRECT_URI` - URI de redirección
- `CODE_CHALLENGE` - Challenge para PKCE
- `CODE_VERIFIER` - Verificador para PKCE

### Configuración de IA
- API Key de PublicAI configurada en `ai_service.py`
- Modelos: ALIA-40b, Salamandra-7b
- Endpoint: https://api.publicai.co/v1/chat/completions

## Métricas y Monitoreo

La aplicación genera automáticamente:
- **Logs de transacciones** y análisis
- **Métricas de rendimiento** de IA
- **Estadísticas de uso** de la API
- **Reportes de errores** detallados

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte técnico o preguntas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar la documentación de la API

## Roadmap

### Próximas Características
- [ ] Integración con más bancos
- [ ] Análisis predictivo con ML
- [ ] App móvil nativa
- [ ] Notificaciones inteligentes
- [ ] Integración con servicios de inversión
- [ ] Análisis de mercado en tiempo real

### Mejoras Técnicas
- [ ] Cache de respuestas de IA
- [ ] Optimización de consultas
- [ ] Tests automatizados
- [ ] CI/CD pipeline
- [ ] Monitoreo avanzado

---

**Desarrollado con cariño para mejorar la salud financiera de los usuarios**
