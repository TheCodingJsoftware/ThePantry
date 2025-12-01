import logging
import os
import uuid

import asyncpg
import bcrypt

from config.environments import Environment
from handlers.base import BaseHandler
from handlers.require_role import require_role
from utils.database import create_colony_database, get_master_pool


class ColonyItemsPageHandler(BaseHandler):
    @require_role("admin")
    async def get(self, *args, **kwargs):
        colony_identifier = self.request.path.strip("/").lower()
        colony_identifier = colony_identifier.replace("/settings", "").replace("/items", "")
        logging.info(f"Fetching colony page for identifier: {colony_identifier}")

        pool = await get_master_pool()
        async with pool.acquire() as conn:
            colony_record = await conn.fetchrow(
                """
                SELECT id, colony_name, theme_color, banner_file
                FROM colonies
                WHERE colony_name = $1
                """,
                colony_identifier,
            )

        if not colony_record:
            self.set_status(404)
            self.finish(f"Colony '{colony_identifier}' not found.")
            return

        raw_role = self.get_secure_cookie("role")
        role = raw_role.decode("utf-8") if raw_role else None

        self.render_template(
            "colony_items.html",
            colony_name=colony_record["colony_name"],
            theme_color=colony_record["theme_color"],
            banner_file=colony_record["banner_file"],
            role=role,
        )

    @require_role("admin")
    async def post(self, *args, **kwargs):
        try:
            # ====================================================
            # Identify the colony from the request path
            # /api/colony/{colony}/items
            # ====================================================
            colony_identifier = self.request.path.strip("/").split("/")[2].lower()
            logging.info(f"[ADD ITEM] Colony: {colony_identifier}")

            # ====================================================
            # Fetch colony record to get database_name
            # ====================================================
            master_pool = await get_master_pool()
            async with master_pool.acquire() as conn:
                colony = await conn.fetchrow(
                    """
                    SELECT id, database_name
                    FROM colonies
                    WHERE colony_name = $1
                    """,
                    colony_identifier,
                )

            if not colony:
                self.set_status(404)
                return self.finish({"error": "Colony not found"})

            colony_db = colony["database_name"]

            # ====================================================
            # COLONY DB connection
            # ====================================================
            colony_dsn = f"postgres://{Environment.POSTGRES_USER}:{Environment.POSTGRES_PASSWORD}@{Environment.POSTGRES_HOST}:{Environment.POSTGRES_PORT}/{colony_db}"
            colony_conn = await asyncpg.connect(colony_dsn)

            # ====================================================
            # FORM FIELDS
            # ====================================================
            name = self.get_body_argument("name")
            description = self.get_body_argument("description", None)
            points_per_item = int(self.get_body_argument("points_per_item", "1"))
            website_url = self.get_body_argument("website_url", None)
            category = self.get_body_argument("category", None)
            tags_raw = self.get_body_argument("tags", "")

            is_active = self.get_body_argument("is_active", "true") == "true"
            max_allowed_raw = self.get_body_argument("max_allowed", "")
            default_quantity = int(self.get_body_argument("default_quantity", "1"))

            tags = [t.strip() for t in tags_raw.split(",") if t.strip()] or None
            max_allowed = int(max_allowed_raw) if max_allowed_raw else None

            # ====================================================
            # Thumbnail upload
            # ====================================================
            thumb_meta = self.request.files.get("thumbnail")
            thumbnail_filename = None

            if thumb_meta:
                fileinfo = thumb_meta[0]
                original_name = fileinfo["filename"]
                ext = os.path.splitext(original_name)[1]

                thumbnail_filename = f"{uuid.uuid4().hex}{ext}"

                save_dir = f"{Environment.DATA_PATH}/uploaded_thumbnails/"
                os.makedirs(save_dir, exist_ok=True)

                save_path = os.path.join(save_dir, thumbnail_filename)

                with open(save_path, "wb") as f:
                    f.write(fileinfo["body"])

                logging.info(f"Thumbnail saved: {thumbnail_filename}")

            # ====================================================
            # Insert Item
            # ====================================================
            sql = """
                INSERT INTO colony_items (
                    name, description, points_per_item,
                    thumbnail_path,
                    website_url, category, tags,
                    is_active, max_allowed, default_quantity
                )
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                RETURNING id
            """

            new_id = await colony_conn.fetchval(
                sql,
                name,
                description,
                points_per_item,
                thumbnail_filename,
                website_url,
                category,
                tags,  # TEXT[]
                is_active,
                max_allowed,
                default_quantity,
            )

            await colony_conn.close()

            return self.finish({"success": True, "item_id": new_id})

        except Exception as e:
            logging.exception("Error in ColonyItemsPostHandler:")
            self.set_status(400)
            return self.finish({"error": str(e)})


class ColonyItemsAPIUpdateHandler(BaseHandler):
    @require_role("admin")
    async def post(self, colony_name: str, *args, **kwargs):
        try:
            colony_identifier = colony_name.lower()
            logging.info(f"[UPDATE ITEM] Colony: {colony_identifier}")

            # --------------------------------------------------
            # Fetch colony DB name
            # --------------------------------------------------
            master_pool = await get_master_pool()
            async with master_pool.acquire() as conn:
                colony = await conn.fetchrow(
                    """
                    SELECT database_name
                    FROM colonies
                    WHERE colony_name = $1
                    """,
                    colony_identifier,
                )

            if not colony:
                self.set_status(404)
                return self.finish({"error": "Colony not found"})

            colony_db = colony["database_name"]

            colony_dsn = f"postgres://{Environment.POSTGRES_USER}:{Environment.POSTGRES_PASSWORD}@{Environment.POSTGRES_HOST}:{Environment.POSTGRES_PORT}/{colony_db}"

            colony_conn = await asyncpg.connect(colony_dsn)

            # --------------------------------------------------
            # FORM FIELDS
            # --------------------------------------------------
            item_id = int(self.get_body_argument("id"))

            name = self.get_body_argument("name")
            description = self.get_body_argument("description", None)
            points_per_item = int(self.get_body_argument("points_per_item"))

            website_url = self.get_body_argument("website_url", None)
            category = self.get_body_argument("category", None)
            tags_raw = self.get_body_argument("tags", "")

            is_active = self.get_body_argument("is_active", "true") == "true"
            max_allowed_raw = self.get_body_argument("max_allowed", None)
            default_quantity = int(self.get_body_argument("default_quantity", "1"))

            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
            max_allowed = int(max_allowed_raw) if max_allowed_raw not in (None, "", "null") else None

            # --------------------------------------------------
            # OPTIONAL THUMBNAIL UPLOAD
            # --------------------------------------------------
            thumb_meta = self.request.files.get("thumbnail")
            thumbnail_filename = None

            if thumb_meta:
                fileinfo = thumb_meta[0]
                original_name = fileinfo["filename"]
                ext = os.path.splitext(original_name)[1]

                thumbnail_filename = f"{uuid.uuid4().hex}{ext}"

                save_dir = f"{Environment.DATA_PATH}/uploaded_thumbnails/"
                os.makedirs(save_dir, exist_ok=True)

                save_path = os.path.join(save_dir, thumbnail_filename)

                with open(save_path, "wb") as f:
                    f.write(fileinfo["body"])

                logging.info(f"[UPDATE ITEM] New thumbnail saved: {thumbnail_filename}")

            # --------------------------------------------------
            # UPDATE SQL
            # --------------------------------------------------
            sql = """
                UPDATE colony_items
                SET
                    name = $1,
                    description = $2,
                    points_per_item = $3,
                    website_url = $4,
                    category = $5,
                    tags = $6,
                    is_active = $7,
                    max_allowed = $8,
                    default_quantity = $9,
                    updated_at = NOW(),
                    thumbnail_path = COALESCE($10, thumbnail_path)
                WHERE id = $11
            """

            await colony_conn.execute(
                sql,
                name,
                description,
                points_per_item,
                website_url,
                category,
                tags,
                is_active,
                max_allowed,
                default_quantity,
                thumbnail_filename,  # only overwrites if provided
                item_id,
            )

            await colony_conn.close()

            return self.finish({"success": True})

        except Exception as e:
            logging.exception("Error in ColonyItemsAPIUpdateHandler:")
            self.set_status(400)
            return self.finish({"error": str(e)})


class ColonyItemsAPIGetHandler(BaseHandler):
    @require_role("admin")
    async def get(self, colony_name: str, *args, **kwargs):
        try:
            colony_identifier = colony_name.lower()
            logging.info(f"[GET ITEMS] Colony: {colony_identifier}")

            # ------------------------------
            # Fetch colony DB name
            # ------------------------------
            master_pool = await get_master_pool()
            async with master_pool.acquire() as conn:
                colony = await conn.fetchrow(
                    """
                    SELECT database_name
                    FROM colonies
                    WHERE colony_name = $1
                    """,
                    colony_identifier,
                )

            if not colony:
                self.set_status(404)
                return self.finish({"error": "Colony not found"})

            colony_db = colony["database_name"]

            # ------------------------------
            # Connect to colony DB
            # ------------------------------
            colony_dsn = f"postgres://{Environment.POSTGRES_USER}:{Environment.POSTGRES_PASSWORD}@{Environment.POSTGRES_HOST}:{Environment.POSTGRES_PORT}/{colony_db}"

            colony_conn = await asyncpg.connect(colony_dsn)

            # ------------------------------
            # Query items
            # ------------------------------
            rows = await colony_conn.fetch(
                """
                SELECT id, name, description, points_per_item,
                       thumbnail_path, website_url,
                       category, tags,
                       is_active, max_allowed, default_quantity,
                       created_at, updated_at
                FROM colony_items
                ORDER BY name ASC
                """
            )

            await colony_conn.close()

            # Convert tags arrays to Python lists
            items = []
            for r in rows:
                items.append(
                    {
                        "id": r["id"],
                        "name": r["name"],
                        "description": r["description"],
                        "points_per_item": r["points_per_item"],
                        "thumbnail_path": r["thumbnail_path"],
                        "website_url": r["website_url"],
                        "category": r["category"],
                        "tags": r["tags"] or [],
                        "is_active": r["is_active"],
                        "max_allowed": r["max_allowed"],
                        "default_quantity": r["default_quantity"],
                        "created_at": r["created_at"].isoformat(),
                        "updated_at": r["updated_at"].isoformat(),
                    }
                )

            return self.finish({"success": True, "items": items})

        except Exception as e:
            logging.exception("Error in ColonyItemsAPIGetHandler:")
            self.set_status(400)
            return self.finish({"error": str(e)})
