# SEMPIA AI Worker (Node 3)

Servicio de Inteligencia Artificial Educativa.

## Componentes

*   **API FastAPI**: Endpoints para tutoría y estimación de conocimiento.
*   **Deep Knowledge Tracing (DKT)**: PyTorch LSTM para inferencia cognitiva.
*   **Tutoría Integrada**: Generación de pistas adaptativas con Gemini.

## Despliegue

```bash
cp .env.example .env
docker-compose up -d --build
```

## Limitaciones y Seguridad
*   El modelo DKT actual inicia con estimaciones en frío (0.5) y una incertidumbre alta en ausencia de pesos entrenados.
*   La interacción con Gemini está restringida para evitar inyección de prompts, y solo retorna el número limitado de pistas. No se comparten llaves ni info secreta.
