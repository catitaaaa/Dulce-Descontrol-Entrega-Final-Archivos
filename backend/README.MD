# Arquitectura Backend - Dulce Descontrol

Para este proyecto se optó por una arquitectura de datos moderna y eficiente, prescindiendo de un servidor intermediario tradicional (como Node.js, PHP o Python).

La lógica de la aplicación se maneja de dos formas según la versión:

1. **Versión Local (Rúbrica Principal):** Utiliza el almacenamiento nativo del navegador (`localStorage`) para gestionar y persistir el estado de los pedidos, actuando como una base de datos local para la demostración del prototipo.
2. **Versión Avanzada Cloud:** Emplea una arquitectura **Serverless (Sin Servidor)** utilizando **Google Cloud Firestore (Firebase)**. Toda la lógica de backend, almacenamiento y reglas de datos se gestionan directamente a través de los SDK integrados en el Front-end.

Esta decisión arquitectónica permite:
- Menor latencia y respuestas inmediatas en la interfaz.
- Sincronización de pedidos en tiempo real.
- Reducción total de costos operativos de infraestructura en etapas tempranas.