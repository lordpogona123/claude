# 🚀 LinkedIn AI Trends Automation - Guía de Configuración

## 📋 Descripción

Este workflow de n8n automatiza la creación y publicación diaria de posts en LinkedIn sobre las últimas tendencias de Inteligencia Artificial. El sistema:

- ✅ Se ejecuta automáticamente todos los días a las 9:00 AM
- ✅ Busca las noticias más recientes sobre IA (últimas 24 horas)
- ✅ Analiza tendencias y crea contenido profesional optimizado
- ✅ Genera imágenes impactantes con DALL-E 3
- ✅ Publica automáticamente en tu perfil de LinkedIn

## 🔧 Requisitos Previos

### 1. APIs Necesarias

Necesitarás crear cuentas y obtener credenciales para:

#### **NewsAPI** (para buscar noticias)
- Regístrate en: https://newsapi.org/
- Plan gratuito: 100 requests/día
- Copia tu API Key

#### **OpenAI API** (para generar contenido e imágenes)
- Regístrate en: https://platform.openai.com/
- Añade créditos a tu cuenta (mínimo $5)
- Crea una API Key en: https://platform.openai.com/api-keys
- Modelos utilizados:
  - **GPT-4o**: Para generar el contenido del post
  - **DALL-E 3**: Para generar imágenes HD

#### **LinkedIn API** (para publicar)
- Necesitarás crear una LinkedIn App
- Sigue esta guía: https://docs.n8n.io/integrations/builtin/credentials/linkedin/
- Permisos necesarios: `w_member_social`, `r_basicprofile`

### 2. n8n Cloud
- Cuenta en n8n Cloud: https://n8n.io/cloud/
- O instalación self-hosted de n8n

## 📥 Instalación

### Paso 1: Importar el Workflow

1. Accede a tu instancia de n8n Cloud
2. Ve a **Workflows** > **Add Workflow** > **Import from File**
3. Selecciona el archivo `linkedin-ai-trends-automation.json`
4. El workflow se importará con todos los nodos configurados

### Paso 2: Configurar Credenciales

#### A. NewsAPI

1. En n8n, ve a **Settings** > **Credentials** > **New**
2. Busca **HTTP Query Auth**
3. Configura:
   - **Name**: `NewsAPI Credentials`
   - **Query Auth**:
     - Name: `apiKey`
     - Value: `TU_NEWSAPI_KEY`

#### B. OpenAI

1. Ve a **Settings** > **Credentials** > **New**
2. Busca **OpenAI**
3. Configura:
   - **Name**: `OpenAI API`
   - **API Key**: `TU_OPENAI_API_KEY`

#### C. LinkedIn OAuth2

1. Ve a **Settings** > **Credentials** > **New**
2. Busca **LinkedIn OAuth2 API**
3. Sigue el proceso de autenticación OAuth2
4. Autoriza los permisos necesarios

### Paso 3: Conectar Credenciales al Workflow

1. Abre el workflow importado
2. Para cada nodo que requiera credenciales:
   - **Fetch AI News - NewsAPI**: Selecciona `NewsAPI Credentials`
   - **OpenAI - Generate Post Content**: Selecciona `OpenAI API`
   - **DALL-E 3 - Generate Image**: Selecciona `OpenAI API`
   - **LinkedIn - Upload Image**: Selecciona `LinkedIn OAuth2`
   - **LinkedIn - Create Post**: Selecciona `LinkedIn OAuth2`

### Paso 4: Personalizar el Horario (Opcional)

Por defecto, el workflow se ejecuta a las **9:00 AM** todos los días.

Para cambiar el horario:

1. Haz clic en el nodo **Schedule Trigger - Daily 9AM**
2. Modifica la expresión cron:
   - `0 9 * * *` = 9:00 AM diario
   - `0 18 * * *` = 6:00 PM diario
   - `0 12 * * 1` = 12:00 PM solo los lunes

### Paso 5: Activar el Workflow

1. Haz clic en el botón **Active** en la esquina superior derecha
2. El workflow comenzará a ejecutarse automáticamente según el horario configurado

## 🎯 Flujo del Workflow

```
1. Schedule Trigger (Cron)
   ↓
2. Buscar Noticias de IA (NewsAPI)
   ↓
3. Procesar y Filtrar Noticias
   ↓
4. Generar Contenido del Post (GPT-4o)
   ↓
5. Parsear Respuesta JSON
   ↓
6. Generar Imagen (DALL-E 3)
   ↓
7. Descargar Imagen
   ↓
8. Subir Imagen a LinkedIn
   ↓
9. Crear Post en LinkedIn
   ↓
10. Verificar Éxito/Error
```

## 🔍 Descripción de Nodos

### 1. **Schedule Trigger - Daily 9AM**
- Tipo: Schedule Trigger
- Función: Ejecuta el workflow automáticamente
- Configuración: Cron expression `0 9 * * *`

### 2. **Fetch AI News - NewsAPI**
- Tipo: HTTP Request
- Función: Busca noticias recientes sobre IA
- Búsqueda: "artificial intelligence", "AI", "machine learning", etc.
- Filtro: Últimas 24 horas, en español, top 10 resultados

### 3. **Process News Data**
- Tipo: Set Node
- Función: Procesa y formatea las noticias
- Output: Resumen de 5 artículos principales

### 4. **OpenAI - Generate Post Content**
- Tipo: OpenAI (Chat)
- Modelo: GPT-4o
- Función: Analiza noticias y genera:
  - Texto del post (150-300 palabras)
  - Prompt para la imagen
  - Tema principal
- Temperatura: 0.8 (creatividad moderada-alta)

### 5. **Parse OpenAI Response**
- Tipo: Code (JavaScript)
- Función: Extrae y parsea la respuesta JSON de OpenAI
- Manejo robusto de errores

### 6. **DALL-E 3 - Generate Image**
- Tipo: OpenAI (Image)
- Modelo: DALL-E 3
- Configuración:
  - Calidad: HD
  - Tamaño: 1024x1024 (óptimo para LinkedIn)
  - Estilo: Vivid

### 7. **Download Generated Image**
- Tipo: HTTP Request
- Función: Descarga la imagen generada

### 8. **LinkedIn - Upload Image**
- Tipo: LinkedIn
- Función: Sube la imagen a LinkedIn

### 9. **LinkedIn - Create Post**
- Tipo: LinkedIn
- Función: Crea el post con texto e imagen
- Visibilidad: PUBLIC

### 10. **Check Post Success**
- Tipo: IF
- Función: Verifica si el post se creó correctamente

## 🎨 Personalización

### Modificar el Estilo del Contenido

Edita el prompt del sistema en el nodo **OpenAI - Generate Post Content**:

```javascript
// Ejemplo: Estilo más técnico
"Eres un experto técnico en IA. Crea posts detallados y técnicos sobre..."

// Ejemplo: Estilo más casual
"Eres un comunicador de tecnología accesible. Crea posts amigables que simplifiquen conceptos de IA..."
```

### Cambiar Idioma de los Posts

En el nodo **OpenAI - Generate Post Content**, modifica:
- Sistema: Cambia "En español" a "In English" o el idioma deseado
- NewsAPI: Cambia el parámetro `language` de `es` a `en`, `fr`, etc.

### Ajustar Frecuencia de Búsqueda de Noticias

En el nodo **Fetch AI News - NewsAPI**, modifica el parámetro `from`:
- Últimas 24 horas: `={{ $today.minus({ days: 1 }).toISO() }}`
- Última semana: `={{ $today.minus({ days: 7 }).toISO() }}`
- Últimos 3 días: `={{ $today.minus({ days: 3 }).toISO() }}`

### Modificar Hashtags

En el prompt del sistema, personaliza la lista de hashtags según tu audiencia.

## 🧪 Pruebas

### Ejecutar Manualmente

1. Abre el workflow
2. Haz clic en **Execute Workflow** en la esquina superior derecha
3. Observa la ejecución paso a paso
4. Verifica el output de cada nodo

### Revisar Logs

1. Ve a **Executions** en el menú lateral
2. Selecciona una ejecución
3. Revisa el estado de cada nodo
4. Verifica errores si los hay

## 💰 Costos Estimados

### OpenAI (por ejecución diaria)
- **GPT-4o**: ~1,500 tokens = $0.015
- **DALL-E 3 HD**: 1 imagen 1024x1024 = $0.080
- **Total por día**: ~$0.095
- **Total por mes**: ~$2.85

### NewsAPI
- Plan gratuito: 100 requests/día (suficiente)
- Plan Developer: $449/mes (si necesitas más)

### LinkedIn
- Gratis

### n8n Cloud
- Starter: $20/mes (5,000 executions)
- Pro: $50/mes (10,000 executions)

## 🛟 Solución de Problemas

### Error: "No articles found"
- Verifica que tu NewsAPI key sea válida
- Comprueba que tengas requests disponibles (límite: 100/día en plan gratuito)

### Error: "OpenAI authentication failed"
- Verifica que tu API key sea correcta
- Asegúrate de tener créditos en tu cuenta OpenAI

### Error: "LinkedIn upload failed"
- Reautentica las credenciales OAuth2 de LinkedIn
- Verifica que tu LinkedIn App tenga los permisos correctos

### Posts sin imagen
- Verifica que DALL-E 3 se esté ejecutando correctamente
- Revisa los logs del nodo de descarga de imagen

### Contenido repetitivo
- Aumenta el parámetro `temperature` en OpenAI (prueba 0.9)
- Modifica el prompt del sistema para más variedad

## 📊 Mejoras Futuras

Posibles extensiones del workflow:

1. **Análisis de Engagement**
   - Añadir nodo para trackear likes, comments, shares
   - Almacenar métricas en Google Sheets o base de datos

2. **A/B Testing**
   - Generar múltiples versiones del post
   - Publicar en diferentes horarios

3. **Notificaciones**
   - Enviar email/Slack cuando el post se publique
   - Alertas si hay errores

4. **Multi-idioma**
   - Publicar el mismo contenido en varios idiomas
   - Usar diferentes cuentas de LinkedIn

5. **Videos en lugar de imágenes**
   - Integrar APIs de generación de video
   - Usar Runway, Pika, o similares

## 📝 Notas Importantes

- El workflow está configurado para **español** por defecto
- Se recomienda revisar manualmente los posts iniciales
- DALL-E 3 puede generar imágenes con texto, pero no siempre es preciso
- LinkedIn tiene límites de API, evita ejecutar muy frecuentemente

## 🤝 Soporte

Para problemas o preguntas:
- Documentación n8n: https://docs.n8n.io/
- Community n8n: https://community.n8n.io/
- OpenAI Docs: https://platform.openai.com/docs/

## 📄 Licencia

Este workflow es de código abierto y puede ser modificado libremente.
