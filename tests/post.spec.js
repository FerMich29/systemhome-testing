const { test, expect } = require('@playwright/test');

test.describe('SYSTEMHOME - E2E UX/UI Tests', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('./');
    });

    // --- FLUJO: CONTROL DE ACCESO ---
    test('TC-01: Login Exitoso (Positivo)', async ({ page }) => {
        await page.fill('#l-u', 'admin');
        await page.fill('#l-p', '123');

        await page.click('button:has-text("Entrar")');

        const userBadge = page.locator('#u-badge');
        await userBadge.waitFor({ state: 'visible' });

        await expect(page.locator('#login-screen')).toBeHidden();
        await expect(userBadge).toBeVisible();
    });

    test('TC-02: Login Fallido - Clave Incorrecta (Negativo)', async ({ page }) => {
        await page.fill('#l-u', 'admin');
        await page.fill('#l-p', '9999');
        await page.click('button:has-text("Entrar")');
        await expect(page.locator('#login-screen')).toBeVisible();
    });

    test('TC-03: Campos Vacíos (Edge Case)', async ({ page }) => {
        await page.click('button:has-text("Entrar")');

        await expect(page.locator('#login-screen')).toBeVisible();
    });

    // --- FLUJO: PROCESO DE VENTA ---
    test('TC-04: Registro de Venta y Ticket (Positivo)', async ({ page }) => {
        await page.fill('#l-u', 'admin');
        await page.fill('#l-p', '123');
        await page.click('button:has-text("Entrar")');

        await page.waitForSelector('#u-badge', { state: 'visible' });

        const btnAdd = page.locator('button:has-text("Añadir")').nth(1);
        await btnAdd.click();


        await page.click('#btn-pg');

        await page.fill('#efectivo', '1000');
        await page.click('button:has-text("Confirmar Pago")');

        await expect(page.locator('#m-t')).toBeVisible();
        await expect(page.locator('#tk-f')).toContainText('FOLIO');
    });

    test('TC-05: Pago Insuficiente (Negativo)', async ({ page }) => {
        await page.fill('#l-u', 'admin');
        await page.fill('#l-p', '123');
        await page.click('button:has-text("Entrar")');
        await page.waitForSelector('#u-badge', { state: 'visible' });

        const btnAdd = page.locator('button:has-text("Añadir")').nth(1);
        await btnAdd.click();

        page.on('dialog', async dialog => {
            expect(dialog.message()).toContain('Dinero insuficiente');
            await dialog.accept();
        });

        await page.click('#btn-pg');

        await page.fill('#efectivo', '1');
        await page.click('button:has-text("Confirmar Pago")');

        await expect(page.locator('#m-confirm')).toBeVisible();
    });

    test('TC-06: Venta sin Stock (Edge Case)', async ({ page }) => {
        await page.goto('./');

        await page.fill('#l-u', 'admin');
        await page.fill('#l-p', '123');
        await page.click('button:has-text("Entrar")');


        await page.waitForSelector('#u-badge');

        const btnAdd = page.locator('button:has-text("Añadir")').first();
        await expect(btnAdd).toBeVisible();
    });
    // --- FLUJO: HISTORIAL ---
    test('TC-07: Consulta de Historial (Positivo)', async ({ page }) => {
        await page.fill('#l-u', 'admin'); await page.fill('#l-p', '123');
        await page.click('button:has-text("Entrar")');

        await page.click('#n-h');
        await expect(page.locator('#sec-h')).toBeVisible();


        const row = page.locator('#t-hist tr').first();
        await expect(row).toBeVisible();
    });

    test('TC-08: Visualización Segura de Tablas (Negativo)', async ({ page }) => {
        await page.fill('#l-u', 'admin'); await page.fill('#l-p', '123');
        await page.click('button:has-text("Entrar")');

        await page.click('#n-h');

        await expect(page.locator('th:has-text("Folio")')).toBeVisible();
    });

    test('TC-09: SPA Navigation Toggle (Edge Case)', async ({ page }) => {
        await page.fill('#l-u', 'admin'); await page.fill('#l-p', '123');
        await page.click('button:has-text("Entrar")');


        await page.click('#n-h');
        await expect(page.locator('#sec-h')).toBeVisible();
        await expect(page.locator('#sec-v')).toBeHidden();

        await page.click('#n-v');
        await expect(page.locator('#sec-v')).toBeVisible();
        await expect(page.locator('#sec-h')).toBeHidden();
    });
});