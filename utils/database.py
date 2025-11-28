import logging
import os

import asyncpg

from config.environments import Environment

MASTER_DSN = f"postgres://{Environment.POSTGRES_USER}:{Environment.POSTGRES_PASSWORD}@{Environment.POSTGRES_HOST}:{Environment.POSTGRES_PORT}/{Environment.POSTGRES_DB}"

ROOT_DSN = f"postgres://{Environment.POSTGRES_USER}:{Environment.POSTGRES_PASSWORD}@{Environment.POSTGRES_HOST}:{Environment.POSTGRES_PORT}/postgres"

master_pool = None


# ===============================
#  Load SQL from /schemas/
# ===============================
def load_schema(schema_file: str) -> str:
    schema_path = os.path.join("schemas", schema_file)

    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        return f.read()


# ===============================
#  MASTER DB SCHEMA ENSURER
# ===============================
async def initialize_master_schema():
    """
    Ensures the master database has the required 'colonies' table.
    Uses schemas/master_schema.sql if present.
    """
    schema_file = "master_schema.sql"
    try:
        sql = load_schema(schema_file)
    except FileNotFoundError:
        logging.warning(f"No {schema_file} found. Skipping master DB schema initialization.")
        return

    logging.info("Initializing master database schema...")

    pool = await get_master_pool()
    async with pool.acquire() as conn:
        try:
            await conn.execute(sql)
            logging.info("Master schema initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing master schema: {e}")
            raise


# ===============================
#  MASTER POOL INITIALIZATION
# ===============================
async def init_master_pool():
    """
    Creates asyncpg pool AND ensures the master DB is initialized.
    """
    global master_pool

    if master_pool is None:
        logging.info(f"Creating master DB pool -> {MASTER_DSN}")

        master_pool = await asyncpg.create_pool(
            dsn=MASTER_DSN,
            min_size=Environment.POSTGRES_MIN_POOL_SIZE,
            max_size=Environment.POSTGRES_MAX_POOL_SIZE,
            timeout=Environment.POSTGRES_TIMEOUT,
            command_timeout=Environment.POSTGRES_COMMAND_TIMEOUT,
            max_inactive_connection_lifetime=Environment.POSTGRES_MAX_INACTIVE_CONNECTION_LIFETIME,
        )

        # Ensure master schema exists
        await initialize_master_schema()

    return master_pool


async def get_master_pool():
    if master_pool is None:
        return await init_master_pool()
    return master_pool


# ===============================
#  COLONY DATABASE CREATION
# ===============================
async def create_colony_database(db_name: str):
    logging.info(f"Creating new colony DB -> {db_name}")

    conn = await asyncpg.connect(dsn=ROOT_DSN)

    try:
        await conn.execute(f'CREATE DATABASE "{db_name}"')
        await initialize_colony_schema(db_name)
        logging.info(f"Database created successfully -> {db_name}")
    finally:
        await conn.close()


# ===============================
#  COLONY SCHEMA INITIALIZATION
# ===============================
async def initialize_colony_schema(db_name: str, schema_file: str = "colony_schema.sql"):
    sql = load_schema(schema_file)

    colony_dsn = f"postgres://{Environment.POSTGRES_USER}:{Environment.POSTGRES_PASSWORD}@{Environment.POSTGRES_HOST}:{Environment.POSTGRES_PORT}/{db_name}"

    logging.info(f"Applying schema {schema_file} to DB {db_name}")

    conn = await asyncpg.connect(colony_dsn)

    try:
        await conn.execute(sql)
        logging.info(f"Schema initialized for {db_name}")
    except Exception as e:
        logging.error(f"Error applying schema to {db_name}: {e}")
        raise
    finally:
        await conn.close()
