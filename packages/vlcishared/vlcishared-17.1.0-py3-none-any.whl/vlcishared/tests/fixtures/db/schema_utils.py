from sqlalchemy import text

from vlcishared.env_variables.secrets import get_secret


def copiar_tablas(connection, esquema_origen, esquema_destino):
    """
    Copia todas las tablas del esquema original al de test. Se ejecuta una vez por sesión.
    Usa la misma conexión que el resto de los tests.
    """
    tablas = (
        connection.execute(
            text(
                """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = :esquema
            """
            ),
            {"esquema": esquema_origen},
        )
        .scalars()
        .all()
    )

    for tabla in tablas:
        connection.execute(
            text(
                f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_tables WHERE tablename = '{tabla}' AND schemaname = '{esquema_destino}'
                ) THEN
                    EXECUTE 'CREATE TABLE {esquema_destino}.{tabla} (LIKE {esquema_origen}.{tabla} INCLUDING ALL)';
                END IF;
            END
            $$;
        """
            )
        )

    connection.commit()


def copiar_funciones_y_procedimientos(connection, esquema_origen, esquema_destino):

    funciones = (
        connection.execute(
            text(
                """
            SELECT p.oid
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = :esquema
            """
            ),
            {"esquema": esquema_origen},
        )
        .scalars()
        .all()
    )

    for oid in funciones:
        definicion = connection.execute(text("SELECT pg_get_functiondef(:oid)"), {"oid": oid}).scalar()

        if not definicion:
            continue

        definicion = definicion.replace(f"{esquema_origen}.", f"{esquema_destino}.")

        try:
            connection.execute(text(definicion))
        except Exception as e:
            print(f"Error creando función/procedimiento {oid}: {e}")

    connection.commit()


def borrar_tablas(connection, esquema):
    tablas = (
        connection.execute(
            text(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = :esquema
                """
            ),
            {"esquema": esquema},
        )
        .scalars()
        .all()
    )
    for tabla in tablas:
        connection.execute(text(f"DROP TABLE IF EXISTS {esquema}.{tabla} CASCADE"))
    connection.commit()


def borrar_funciones_y_procedimientos(connection, esquema):
    funciones = connection.execute(
        text(
            """
            SELECT
                p.proname,
                pg_get_function_identity_arguments(p.oid) AS args,
                p.prokind
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = :esquema
            """
        ),
        {"esquema": esquema},
    ).fetchall()

    for nombre, args, tipo in funciones:
        drop_type = "PROCEDURE" if tipo == "p" else "FUNCTION"
        try:
            connection.execute(text(f'DROP {drop_type} IF EXISTS {esquema}."{nombre}"({args}) CASCADE'))
        except Exception as e:
            print(f"Error borrando {drop_type.lower()} {nombre}({args}): {e}")
            connection.rollback()

    connection.commit()
