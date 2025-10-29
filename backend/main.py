import os
import asyncio
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Supabase
from supabase import create_client, Client

# Pyrogram (userbot)
from pyrogram import Client as PyroClient
from pyrogram.enums import ParseMode


class ActivateRequest(BaseModel):
    tg_id: int
    ref_code: Optional[str] = None


def get_env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required env: {name}")
    return value


def create_app() -> FastAPI:
    # Load env from backend/.env
    load_dotenv()

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    supabase_url = get_env("SUPABASE_URL", "")
    supabase_key = get_env("SUPABASE_KEY", "")
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    pyro_session = os.getenv("PYROGRAM_SESSION")  # StringSession (recommended)

    supabase: Client = create_client(supabase_url, supabase_key)

    async def set_user_bio(ref_code: str) -> None:
        """
        Update current user (userbot) BIO via Pyrogram.
        Requires PYROGRAM_SESSION (StringSession) + API_ID/API_HASH in env.
        """
        if not (api_id and api_hash and pyro_session):
            # No session provided — skip gracefully in MVP
            return

        async with PyroClient(
            name="synapse-userbot",
            api_id=int(api_id),
            api_hash=api_hash,
            session_string=pyro_session,
            parse_mode=ParseMode.DISABLED,
        ) as userbot:
            bio_text = f"Генерирую B2B-лиды... t.me/SynapseBot?start={ref_code}"
            await userbot.update_profile(bio=bio_text)

    @app.post("/activate")
    async def activate(payload: ActivateRequest):
        tg_id = payload.tg_id
        input_ref_code = (payload.ref_code or "").strip() or None

        # Upsert user by tg_id
        try:
            upsert_resp = (
                supabase.table("users")
                .upsert({"tg_id": tg_id}, on_conflict="tg_id")
                .select("*")
                .execute()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB upsert error: {e}")

        if not upsert_resp.data:
            raise HTTPException(status_code=500, detail="DB upsert returned no data")

        user_row = upsert_resp.data[0]

        # If ref_code provided, credit referrer and link
        if input_ref_code:
            try:
                ref_q = (
                    supabase.table("users")
                    .select("*")
                    .eq("ref_code", input_ref_code)
                    .limit(1)
                    .execute()
                )
                if ref_q.data:
                    referrer = ref_q.data[0]
                    ref_ai_accounts = int(referrer.get("ai_accounts", 1)) + 3
                    supabase.table("users").update({"ai_accounts": ref_ai_accounts}).eq("id", referrer["id"]).execute()
                    # Link new user to referrer (store referrer's tg_id as spec says bigint)
                    supabase.table("users").update({"referrer_id": referrer.get("tg_id")}).eq("id", user_row["id"]).execute()
            except Exception:
                # Do not fail activation if referral credit failed
                pass

        # Ensure we have a ref_code for the user (select again to capture defaults)
        try:
            fresh = (
                supabase.table("users")
                .select("*")
                .eq("id", user_row["id"])
                .single()
                .execute()
            )
            user_row = fresh.data
        except Exception:
            pass

        user_ref_code = user_row.get("ref_code") or "direct"

        # Update user BIO via userbot (best-effort)
        try:
            await set_user_bio(user_ref_code)
        except Exception:
            # Do not fail activation if BIO update failed
            pass

        return {"ok": True, "message": "Триал активирован!", "ref_code": user_ref_code}

    return app


app = create_app()


