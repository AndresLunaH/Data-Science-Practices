#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os, sys
from datetime import datetime

DB = "minicafe.db"

def cls():
    # Limpia consola en Windows/Linux/macOS
    os.system('cls' if os.name == 'nt' else 'clear')  # [web:27][web:30][web:33]

def conn_db():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON;")  # activar FK por conexión [web:28][web:34][web:40]
    return conn

def bootstrap():
    conn = conn_db()
    cur = conn.cursor()
    # Tablas
    cur.execute("""
    CREATE TABLE IF NOT EXISTS paquetes(
        id_paquete INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        desc TEXT,
        precio REAL NOT NULL
    )
    """)  # [web:24][web:22]
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ventas(
        id_venta INTEGER PRIMARY KEY,
        fecha TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
        id_paquete INTEGER NOT NULL,
        FOREIGN KEY(id_paquete) REFERENCES paquetes(id_paquete)
    )
    """)  # fecha ISO8601 por DEFAULT [web:24][web:26]
    # Semilla catálogo
    cur.execute("SELECT COUNT(1) FROM paquetes")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO paquetes(id_paquete,nombre,desc,precio) VALUES(?,?,?,?)
        """, [
            (1, "Desayunito", "Huevos, tostadas, café y jugo", 50.00),
            (2, "Almuercito", "Pollo a la plancha, arroz y bebida", 80.00),
            (3, "Ensaladita", "Ensalada de pollo, sopa y bebida", 60.00),
            (4, "Comidita", "Sándwich de pollo, papas fritas y bebida", 70.00),
            (5, "Postrecito", "Postre del día y malteada", 80.00),
        ])  # catálogo de la guía
    # Bitácora inicial (ejemplos con fechas dadas)
    cur.execute("SELECT COUNT(1) FROM ventas")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO ventas(id_venta, fecha, id_paquete) VALUES(?,?,?)
        """, [
            (1, "2020-01-15 13:00:00", 3),
            (2, "2020-01-15 14:00:00", 1),
            (3, "2020-01-15 15:00:00", 3),
            (4, "2020-01-15 16:00:00", 4),
            (5, "2020-01-15 18:00:00", 5),
        ])  # formato ISO8601 válido para TEXT [web:29][web:26]
    conn.commit()
    conn.close()

def listar_paquetes(cur):
    cur.execute("SELECT id_paquete, nombre FROM paquetes ORDER BY id_paquete")
    return cur.fetchall()  # solo ID y nombre para Opción 1

def registrar_ventas():
    while True:
        cls()  # limpiar consola [web:27]
        conn = conn_db()
        cur = conn.cursor()
        print("Paquetes disponibles:")
        for pid, nom in listar_paquetes(cur):
            print(f"- {pid}: {nom}")
        print()
        elec = input("¿Qué paquete se ha vendido? (ID) o escribe 'cancelar': ").strip()
        if elec.lower() == "cancelar":
            conn.close()
            cls()
            return
        if not elec.isdigit():
            input("Entrada inválida. Enter para continuar...")
            conn.close()
            continue
        pid = int(elec)
        cur.execute("SELECT 1 FROM paquetes WHERE id_paquete = ?", (pid,))
        if cur.fetchone() is None:
            input("ID no encontrado. Enter para continuar...")
            conn.close()
            continue
        # Registrar venta con timestamp actual desde Python o DEFAULT
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ISO8601 [web:26][web:29]
        cur.execute("INSERT INTO ventas(fecha, id_paquete) VALUES(?,?)", (ahora, pid))
        conn.commit()
        conn.close()
        # El bucle repite para permitir múltiples registros como indica el flujo

def reporte_diario():
    cls()
    conn = conn_db()
    cur = conn.cursor()
    # Fecha actual (solo día)
    hoy = datetime.now().strftime("%Y-%m-%d")  # prefijo del día [web:26]
    print("Reporte diario")
    print("---------------------------")
    cur.execute("""
        SELECT p.nombre, v.fecha
        FROM ventas v
        JOIN paquetes p ON p.id_paquete = v.id_paquete
        WHERE substr(v.fecha,1,10) = ?
        ORDER BY v.id_venta
    """, (hoy,))
    filas = cur.fetchall()
    total = 0.0
    if not filas:
        print("No hay ventas registradas hoy.")
    else:
        for nombre, fecha in filas:
            print(f"- {nombre}\t{fecha}")
    # total del día
    cur.execute("""
        SELECT COALESCE(SUM(p.precio),0)
        FROM ventas v
        JOIN paquetes p ON p.id_paquete = v.id_paquete
        WHERE substr(v.fecha,1,10) = ?
    """, (hoy,))
    total = cur.fetchone()[0] or 0.0
    print("\nTOTAL\t{:.2f}".format(total))
    conn.close()
    input("\nPresiona Enter para volver al menú...")

def menu():
    bootstrap()
    while True:
        cls()
        print("Menú inicial")
        print("1) Sistema de ventas")
        print("2) Reporte diario")
        print("3) Salir")
        op = input("Selecciona una opción: ").strip()
        if op == "1":
            registrar_ventas()
        elif op == "2":
            reporte_diario()
        elif op == "3":
            cls()
            break
        else:
            input("Opción inválida. Enter para continuar...")

if __name__ == "__main__":
    menu()
