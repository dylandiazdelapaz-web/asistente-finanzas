# Asistente de Finanzas por WhatsApp

Prototipo local en español para registrar gastos y consultar resúmenes por usuario. Usa SQLite persistente y está pensado para crecer hacia WhatsApp Business Cloud API y Google Sheets, pero todavía no usa credenciales externas.

Incluye un cuestionario financiero de ocho preguntas. Compartir el resultado es opcional; el panel privado requiere configurar `ADMIN_PASSWORD` como variable de entorno. En Render Free, SQLite puede reiniciarse al reiniciar o volver a desplegar el servicio, así que configura una base de datos o disco persistente antes de depender de estos resultados.

## Requisitos

- Python 3.11 o superior
- VS Code

## Ejecutar en PowerShell

```powershell
cd C:\Users\dylan\finanzas-whatsapp
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m uvicorn app:app --reload
```

Abre `http://127.0.0.1:8000/docs` para probar la API desde Swagger.

## Ejemplos

Registrar un gasto:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/expenses -ContentType 'application/json' -Body '{"user_id":"user-a","amount":"4500","category":"transporte","description":"Metro","spent_on":"2026-09-30"}'
```

Consultar el informe mensual:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/users/user-a/summary?year=2026^&month=9
```

Probar un mensaje de WhatsApp en modo local:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/webhooks/whatsapp -ContentType 'application/json' -Body '{"user_id":"+56900000000","message":"Gasté 3.500 en transporte"}'
```

Ejecutar pruebas:

```powershell
py -m pytest
```

Para habilitar el panel privado localmente, define `ADMIN_PASSWORD` antes de iniciar Uvicorn. En Render, agrégala en la sección Environment del servicio y elige una contraseña larga y única.

## Siguiente etapa

1. Validar identidad del usuario mediante el número de WhatsApp, sin mezclar registros.
2. Conectar Meta WhatsApp Cloud API usando variables de entorno.
3. Exportar a Google Sheets con OAuth o una cuenta de servicio protegida.
4. Añadir autenticación, copias de seguridad, eliminación de datos y consentimiento antes de usar datos financieros reales.
