<?php
// Configuración de errores y formato de respuesta JSON
error_reporting(0);
ini_set('display_errors', 0);
header("Content-Type: application/json; charset=utf-8");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

// Credenciales de la base de datos
$db_host = '127.0.0.1';
$db_name = 'ventas'; 
$db_user = 'root';
$db_pass = '';

// Conexión segura a MySQL usando la interfaz PDO
try {
    $pdo = new PDO("mysql:host=$db_host;dbname=$db_name;charset=utf8mb4", $db_user, $db_pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    ]);
} catch (Exception $e) {
    echo json_encode(["status" => "error", "msg" => "Error de conexión"]);
    exit;
}

// Captura del método de petición y decodificación de datos JSON entrantes
$metodo = $_SERVER['REQUEST_METHOD'];
$data = json_decode(file_get_contents('php://input'), true);

// --- BLOQUE DE CONSULTAS (LECTURA) ---
if ($metodo == 'GET') {
    $action = $_GET['action'] ?? '';

    // Obtener lista general de ventas
    if ($action == 'get_ventas') {
        $stmt = $pdo->query("SELECT id, total, created_at, estatus FROM venta ORDER BY id DESC");
        echo json_encode($stmt->fetchAll());
    } 
    // Obtener productos específicos de una venta mediante JOIN
    elseif ($action == 'detalle_venta') {
        $stmt = $pdo->prepare("SELECT dv.*, p.nombre FROM detalle_ventas dv JOIN productos p ON dv.id_producto = p.id WHERE dv.id_venta = ?");
        $stmt->execute([$_GET['id']]);
        echo json_encode($stmt->fetchAll());
    }
    // Calcular estadísticas: total diario, inventario y alertas de stock bajo
    elseif ($action == 'metricas') {
        $stmt1 = $pdo->query("SELECT SUM(total) as diario FROM venta WHERE estatus = 'PAGADA'");
        $vTotal = $stmt1->fetchColumn() ?: 0;
        $stmt2 = $pdo->query("SELECT COUNT(*) FROM productos");
        $tProds = $stmt2->fetchColumn() ?: 0;
        $stmt3 = $pdo->query("SELECT COUNT(*) FROM productos WHERE stock < 5");
        $sBajo = $stmt3->fetchColumn() ?: 0;
        echo json_encode(["ventas_hoy" => $vTotal, "total_productos" => $tProds, "alertas_stock" => $sBajo]);
    }
    // Consultar facturas registradas con sus montos originales
    elseif ($action == 'get_facturas') {
        $stmt = $pdo->query("SELECT f.*, v.total as monto_venta FROM facturas f JOIN venta v ON f.id_venta = v.id ORDER BY f.id DESC");
        echo json_encode($stmt->fetchAll());
    }
    // Carga inicial: catálogo de productos y categorías disponibles
    else {
        $prods = $pdo->query("SELECT * FROM productos ORDER BY categoria, nombre")->fetchAll();
        $cats = $pdo->query("SELECT DISTINCT categoria FROM productos WHERE categoria != ''")->fetchAll(PDO::FETCH_COLUMN);
        echo json_encode(["productos" => $prods, "categorias" => $cats]);
    }
    exit;
}

// --- BLOQUE DE ACCIONES ---
if ($metodo == 'POST') {
    $accion = $data['accion'] ?? '';

    // Validación de credenciales de usuario
    if ($accion == 'login') {
        $stmt = $pdo->prepare("SELECT id, usuario, rol FROM usuarios WHERE usuario = ? AND password = ?");
        $stmt->execute([$data['user'], $data['pass']]);
        $u = $stmt->fetch();
        echo json_encode($u ? ["status" => "ok", "user" => $u] : ["status" => "error"]);
    }
    // Cancelación delegada al Procedimiento Almacenado de la DB
    elseif ($accion == 'cancelar_venta') {
        try {
            $stmt = $pdo->prepare("CALL sp_cancelar_venta(?)");
            $stmt->execute([$data['id_venta']]);
            echo json_encode(["status" => "ok", "info" => "Procesado por SP"]);
        } catch (Exception $e) { 
            echo json_encode(["status" => "error", "msg" => $e->getMessage()]); 
        }
    }
    // Registro de datos fiscales para facturación
    elseif ($accion == 'generar_factura') {
        $stmt = $pdo->prepare("INSERT INTO facturas (id_venta, rfc, razon_social, uso_cfdi, email) VALUES (?, ?, ?, ?, ?)");
        $stmt->execute([$data['id_venta'], strtoupper($data['rfc']), strtoupper($data['razon_social']), $data['uso_cfdi'], $data['email']]);
        echo json_encode(["status" => "ok"]);
    }
    // Procesamiento de nueva venta con transacciones atómicas
    else {
        $pdo->beginTransaction(); // Asegura que se guarde todo o nada
        try {
            // 1. Insertar cabecera de la venta
            $stmt = $pdo->prepare("INSERT INTO venta (usuario_id, total, estatus, created_at) VALUES (1, ?, 'PAGADA', NOW())");
            $stmt->execute([$data['total']]);
            $id_v = $pdo->lastInsertId(); // Obtener el ID generado para el detalle

            // 2. Registrar cada producto y descontar stock simultáneamente
            foreach ($data['productos'] as $p) {
                $det = $pdo->prepare("INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario) VALUES (?, ?, 1, ?)");
                $det->execute([$id_v, $p['id'], $p['p']]); 

                $upd = $pdo->prepare("UPDATE productos SET stock = stock - 1 WHERE id = ?");
                $upd->execute([$p['id']]);
            }

            $pdo->commit(); // Confirmar cambios en la DB
            echo json_encode(["status" => "ok", "id_venta" => $id_v, "fecha" => date("Y-m-d H:i:s")]);
        } catch (Exception $e) {
            $pdo->rollBack(); // Revertir cambios en caso de error
            echo json_encode(["status" => "error", "msg" => $e->getMessage()]);
        }
    }
    exit;
}
?>