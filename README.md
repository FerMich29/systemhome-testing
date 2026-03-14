# SYSTEMHOME - Automated E2E Testing Suite 

This repository contains the End-to-End (E2E) testing framework for the **SYSTEMHOME** sales and inventory management system. 

## Project Overview
The main objective of this project is to verify the stability of critical business workflows using **Playwright**. This suite covers security, transaction integrity, and UI state management.

## Test Cases
1. **TC-01:** Login Exitoso (Control de Acceso).
2. **TC-02:** Login Fallido - Clave Incorrecta.
3. **TC-03:** Intento de Login con Campos Vacíos.
4. **TC-04:** Registro de Venta y Generación de Ticket (Flujo Positivo completo).
5. **TC-05:** Pago Insuficiente (Validación de lógica de negocio).
6. **TC-06:** Intento de Venta de Producto sin Stock.
7. **TC-07:** Consulta y Visualización de Historial de Ventas.
8. **TC-08:** Verificación de Estructura de Tablas (Seguridad de datos).
9. **TC-09:** Navegación entre secciones (SPA Toggle).
   
## Tech Stack
- **Framework:** [Playwright](https://playwright.dev/)
- **Language:** JavaScript
- **Reporting:** Playwright HTML Reporter

## How to Run the Tests
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/MichelAguayo/home-sale-testing.git](https://github.com/MichelAguayo/home-sale-testing.git)

2. **Playwright instalation:**
   npx playwright install

3. **Execution:**
   npx playwright test
