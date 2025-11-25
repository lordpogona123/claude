# ✅ Lista de Verificación para Probar el Workflow

## Antes de Importar

### 1. Crear Cuentas y Obtener API Keys

- [ ] **NewsAPI**
  - Registrarse en https://newsapi.org/register
  - Copiar tu API Key del dashboard
  - Verificar límite: 100 requests/día (plan gratuito)

- [ ] **OpenAI**
  - Crear cuenta en https://platform.openai.com/signup
  - Añadir créditos ($5 mínimo) en Billing
  - Crear API Key en https://platform.openai.com/api-keys
  - Verificar que tienes acceso a GPT-4o y DALL-E 3

- [ ] **LinkedIn**
  - Tener perfil de LinkedIn activo
  - Preparar credenciales OAuth2 (se configuran en n8n)

## Importación en n8n

### 2. Importar el Workflow

- [ ] Ir a n8n Cloud (o tu instancia self-hosted)
- [ ] Workflows → "Add Workflow" → "Import from File"
- [ ] Seleccionar `linkedin-ai-trends-automation.json`
- [ ] Verificar que todos los nodos se importen correctamente

### 3. Posibles Problemas al Importar

Si encuentras errores al importar:

#### Error: "Unknown node type"
```
Solución: Actualiza n8n o instala el paquete del nodo faltante
```

#### Error: "Invalid JSON"
```
Solución: Verifica que el archivo no esté corrupto, descárgalo de nuevo
```

#### Advertencias de versión
```
Solución: Acepta actualizar a las versiones más recientes de los nodos
```

## Configuración de Credenciales

### 4. Configurar NewsAPI

- [ ] En n8n: Settings → Credentials → New
- [ ] Tipo: "HTTP Query Auth"
- [ ] Nombre: "NewsAPI Credentials" (o el que prefieras)
- [ ] Configuración:
  ```
  Name: apiKey
  Value: [TU_NEWSAPI_KEY]
  ```
- [ ] Save

### 5. Configurar OpenAI

- [ ] Settings → Credentials → New
- [ ] Tipo: "OpenAI"
- [ ] Nombre: "OpenAI API" (o el que prefieras)
- [ ] API Key: [TU_OPENAI_API_KEY]
- [ ] Save

### 6. Configurar LinkedIn OAuth2

- [ ] Settings → Credentials → New
- [ ] Tipo: "LinkedIn OAuth2 API"
- [ ] Seguir el proceso de autenticación OAuth2
- [ ] Autorizar permisos: `w_member_social`, `r_basicprofile`
- [ ] Save

### 7. Conectar Credenciales a los Nodos

Abre el workflow y para cada nodo:

- [ ] **Nodo "Fetch AI News - NewsAPI"**
  - Click en el nodo
  - En "Credential for HTTP Query Auth" → Seleccionar "NewsAPI Credentials"

- [ ] **Nodo "OpenAI - Generate Post Content"**
  - En "Credential for OpenAI" → Seleccionar "OpenAI API"

- [ ] **Nodo "DALL-E 3 - Generate Image"**
  - En "Credential for OpenAI" → Seleccionar "OpenAI API"

- [ ] **Nodo "LinkedIn - Upload Image"**
  - En "Credential for LinkedIn OAuth2" → Seleccionar tu credencial de LinkedIn

- [ ] **Nodo "LinkedIn - Create Post"**
  - En "Credential for LinkedIn OAuth2" → Seleccionar tu credencial de LinkedIn

## Ajustes Potenciales

### 8. Verificar Configuración de Nodos

#### Nodo OpenAI - Generate Post Content

Si tu versión de n8n es diferente, el nodo puede llamarse:
- "OpenAI Chat Model" en lugar de "OpenAI"
- O usar el nodo de texto "Chat"

Ajustar según tu versión:
```javascript
// Verificar que esté configurado:
Resource: Text / Chat
Operation: Message / Complete
Model: gpt-4o (o el más reciente disponible)
```

#### Nodo DALL-E 3

```javascript
// Verificar configuración:
Resource: Image
Operation: Create / Generate
Model: dall-e-3
Size: 1024x1024
Quality: hd
```

#### Nodo LinkedIn

```javascript
// Verificar operaciones:
Nodo Upload: operation = "upload"
Nodo Create Post: operation = "create"
```

## Prueba Manual

### 9. Primera Ejecución de Prueba

- [ ] **NO activar el workflow todavía**
- [ ] Click en "Execute Workflow" (botón arriba a la derecha)
- [ ] Observar la ejecución paso a paso

### 10. Verificar Cada Nodo

Revisa el output de cada nodo:

- [ ] **Schedule Trigger**: Se ejecuta (al hacer Execute, se salta este)
- [ ] **Fetch AI News**: Devuelve artículos
  ```
  Esperado: JSON con array "articles"
  ```

- [ ] **Process News Data**: Formatea correctamente
  ```
  Esperado: Campo "articles_summary" con texto
  ```

- [ ] **OpenAI Generate**: Devuelve JSON con post
  ```
  Esperado: JSON con "post_text", "image_prompt", "main_topic"
  ```

- [ ] **Parse Response**: Extrae los campos
  ```
  Esperado: Campos separados y limpios
  ```

- [ ] **DALL-E 3**: Genera URL de imagen
  ```
  Esperado: URL de imagen generada
  ```

- [ ] **Download Image**: Descarga la imagen
  ```
  Esperado: Binary data de la imagen
  ```

- [ ] **LinkedIn Upload**: Sube imagen correctamente
  ```
  Esperado: ID de la imagen subida
  ```

- [ ] **LinkedIn Create Post**: Crea el post
  ```
  Esperado: ID del post y URL
  ```

## Solución de Problemas Comunes

### Error en NewsAPI

```
Error: "apiKey parameter is missing"
```
**Solución**: La credencial no está conectada o el formato es incorrecto
- Verificar que el parámetro query se llama "apiKey" (no "api_key")

```
Error: "You have made too many requests recently"
```
**Solución**: Límite de API alcanzado
- Espera 24 horas o usa otra API key

### Error en OpenAI

```
Error: "Incorrect API key provided"
```
**Solución**: API key inválida
- Verifica que copiaste la key completa (empieza con "sk-")

```
Error: "You exceeded your current quota"
```
**Solución**: Sin créditos
- Añade créditos en https://platform.openai.com/account/billing

```
Error: "Model not found: gpt-4o"
```
**Solución**: No tienes acceso al modelo
- Cambia a "gpt-4-turbo" o "gpt-3.5-turbo"
- O solicita acceso a GPT-4o

### Error en LinkedIn

```
Error: "Invalid access token"
```
**Solución**: OAuth2 expirado
- Reautoriza la conexión en Credentials

```
Error: "Insufficient permissions"
```
**Solución**: Faltan permisos
- Verificar que la app de LinkedIn tenga `w_member_social`

### Error en DALL-E 3

```
Error: "Your request was rejected as a result of our safety system"
```
**Solución**: El prompt fue rechazado por filtros de seguridad
- Modificar el prompt para ser más genérico
- Evitar términos que puedan ser sensibles

## Ajustes Finales

### 11. Optimización

Si todo funciona en la prueba manual:

- [ ] Ajustar el horario en Schedule Trigger si es necesario
- [ ] Modificar el prompt del sistema para tu estilo preferido
- [ ] Personalizar hashtags
- [ ] Cambiar idioma si es necesario

### 12. Activación

- [ ] Revisar que todos los nodos funcionaron correctamente
- [ ] Click en el toggle "Active" en la esquina superior derecha
- [ ] Verificar que el workflow aparece como "Active" en la lista

### 13. Monitoreo

- [ ] Ir a "Executions" para ver el historial
- [ ] Verificar la primera ejecución automática
- [ ] Revisar que el post se publicó en LinkedIn
- [ ] Monitorear los siguientes días

## Notas Importantes

### Limitaciones de Plan Gratuito

**NewsAPI Free:**
- 100 requests/día
- Noticias con 24h de delay (para noticias en tiempo real necesitas plan de pago)

**n8n Cloud Starter ($20/mes):**
- 5,000 workflow executions/mes
- Con 1 ejecución diaria = 30/mes = OK ✅

**OpenAI:**
- GPT-4o: ~$0.015 por ejecución
- DALL-E 3 HD: ~$0.08 por imagen
- Total: ~$0.095/día = $2.85/mes

### Recomendaciones

1. **Prueba manual primero**: No actives el workflow sin probar manualmente
2. **Revisa los primeros posts**: Los primeros días verifica que el contenido sea apropiado
3. **Ajusta temperatura**: Si el contenido es muy repetitivo, sube el parámetro temperature
4. **Monitorea costos**: Revisa tu uso de OpenAI API regularmente
5. **Backup del workflow**: Exporta el JSON después de configurarlo

## ✅ Checklist Final

Antes de dar por terminado:

- [ ] Workflow importado sin errores
- [ ] Todas las credenciales configuradas y conectadas
- [ ] Prueba manual exitosa
- [ ] Post de prueba publicado en LinkedIn correctamente
- [ ] Imagen generada y adjuntada correctamente
- [ ] Horario configurado a tu preferencia
- [ ] Workflow activado
- [ ] Primera ejecución automática verificada

## 🎉 ¡Listo!

Si completaste todos los pasos, tu automatización debería estar funcionando correctamente.

## 🆘 Si Algo No Funciona

1. Revisa los logs en "Executions"
2. Identifica en qué nodo falla
3. Verifica la configuración específica de ese nodo
4. Consulta la documentación de n8n para ese nodo específico
5. Revisa el SETUP-GUIDE.md para más detalles

## 📊 Métricas de Éxito

Después de una semana, deberías ver:
- 7 posts publicados en LinkedIn
- Engagement en tus posts (likes, comentarios, shares)
- Costo de OpenAI: ~$0.67
- 0 errores en las ejecuciones

¡Buena suerte! 🚀
