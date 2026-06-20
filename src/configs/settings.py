import os
from pathlib import Path
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=ROOT / ".env", override=False)


class Settings:
    def __init__(self) -> None:
        self.mysql_url = os.getenv("MYSQL_URL")
        self.mysql_db = os.getenv("MYSQL_DB")
        self.jwt_secret = os.getenv("JWT_SECRET", "change_me")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.token_expire_minutes = int(os.getenv("TOKEN_EXPIRE_MINUTES", "120"))
        self.storage_path = os.getenv("STORAGE_PATH", "storage")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_geo_key = os.getenv("REDIS_GEO_KEY", "pub_geo")
        self.amap_key = os.getenv("AMAP_KEY")
        self.amap_geocode_url = "https://restapi.amap.com/v3/geocode/geo"
        self.amap_walk_url = "https://restapi.amap.com/v5/direction/walking"
        self.amap_drive_url = "https://restapi.amap.com/v5/direction/driving"
        self.llm_api_url = os.getenv("LLM_API_URL")
        self.llm_api_key = os.getenv("LLM_API_KEY")
        self.llm_model = os.getenv("LLM_MODEL", "deepseek-v4-flash")
        self.amap_reverse_geocode_url = "https://restapi.amap.com/v3/geocode/regeo"
        self.sms_mock = os.getenv("SMS_MOCK", "true").lower() == "true"
        # 阿里云短信（号码认证 SendSmsVerifyCode）
        self.ali_access_key_id = os.getenv("ALI_ACCESS_KEY_ID", "")
        self.ali_access_key_secret = os.getenv("ALI_ACCESS_KEY_SECRET", "")
        self.ali_sms_sign_name = os.getenv("ALI_SMS_SIGN_NAME", "")
        self.ali_sms_template_code = os.getenv("ALI_SMS_TEMPLATE_CODE", "")
        self.ali_sms_scheme_name = os.getenv("ALI_SMS_SCHEME_NAME", "")
        self.ali_sms_code_length = int(os.getenv("ALI_SMS_CODE_LENGTH", "6"))
        self.ali_sms_valid_time = int(os.getenv("ALI_SMS_VALID_TIME", "300"))




settings = Settings()
