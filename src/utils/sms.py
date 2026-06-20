"""短信服务 - 阿里云号码认证 SendSmsVerifyCode"""
import random
import logging

from alibabacloud_dypnsapi20170525.client import Client as DypnsapiClient
from alibabacloud_dypnsapi20170525 import models as dypnsapi_models
from alibabacloud_tea_openapi import models as open_api_models

from configs.settings import settings
from db.redis_client import get_redis

logger = logging.getLogger("sms")


def _create_client() -> DypnsapiClient:
    """创建阿里云号码认证客户端"""
    config = open_api_models.Config(
        access_key_id=settings.ali_access_key_id,
        access_key_secret=settings.ali_access_key_secret,
    )
    config.endpoint = "dypnsapi.aliyuncs.com"
    return DypnsapiClient(config)


def _generate_mock_code() -> str:
    """Mock 模式：本地生成验证码"""
    return "".join(str(random.randint(0, 9)) for _ in range(settings.ali_sms_code_length))


def send_verification_code(phone: str) -> str:
    """发送验证码，返回生成的 code

    - Mock 模式：本地随机生成，打印到控制台
    - 生产模式：调用阿里云 SendSmsVerifyCode，由阿里云生成验证码并下发短信
    """
    if settings.sms_mock:
        code = _generate_mock_code()
        redis = get_redis()
        key = f"sms:code:{phone}"
        redis.setex(key, settings.ali_sms_valid_time, code)
        logger.info(f"[SMS MOCK] 验证码发送至 {phone}：{code}")
        return code

    # 生产模式：调用号码认证 API
    sign_name = settings.ali_sms_sign_name.strip()
    template_code = settings.ali_sms_template_code.strip()
    scheme_name = settings.ali_sms_scheme_name.strip() if settings.ali_sms_scheme_name else None

    logger.info(
        f"SendSmsVerifyCode 请求参数：phone={phone}, sign_name={sign_name!r}, "
        f"template_code={template_code!r}, scheme_name={scheme_name!r}, "
        f"code_length={settings.ali_sms_code_length}"
    )

    client = _create_client()
    req_kwargs: dict = dict(
        phone_number=phone,
        sign_name=sign_name,
        template_code=template_code,
        template_param='{"code":"##code##","min":"5"}',
        code_length=settings.ali_sms_code_length,
        valid_time=settings.ali_sms_valid_time,
        code_type=1,               # 1=纯数字
        duplicate_policy=1,        # 1=覆盖旧验证码
        return_verify_code=True,   # 返回生成的验证码
    )
    if scheme_name:
        req_kwargs["scheme_name"] = scheme_name

    request = dypnsapi_models.SendSmsVerifyCodeRequest(**req_kwargs)
    response = client.send_sms_verify_code(request)
    body = response.body

    if body.code != "OK":
        logger.error(
            f"短信发送失败：code={body.code}, message={body.message}, "
            f"request_id={body.request_id}"
        )
        raise RuntimeError(f"短信发送失败：{body.message}")

    # 阿里云返回的验证码
    code = body.model.verify_code
    logger.info(
        f"短信发送成功，BizId: {body.model.biz_id}, "
        f"RequestId: {body.request_id}"
    )

    # 将验证码存入 Redis，供后续校验
    redis = get_redis()
    key = f"sms:code:{phone}"
    redis.setex(key, settings.ali_sms_valid_time, code)

    return code


def verify_code(phone: str, code: str) -> bool:
    """校验验证码，校验通过后删除"""
    redis = get_redis()
    key = f"sms:code:{phone}"
    stored = redis.get(key)
    if stored and stored == code:
        redis.delete(key)
        return True
    return False
