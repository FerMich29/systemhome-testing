<?php
$host = "localhost";
$db   = "ventas"; // El nombre que le pusiste a tu DB
$user = "root";   // Usuario por defecto de XAMPP
$pass = "";       // Contraseña por defecto (vacía)

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Error de conexión: " . $e->getMessage());
}
?>