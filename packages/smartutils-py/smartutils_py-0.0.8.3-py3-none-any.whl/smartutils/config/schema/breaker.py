from pydantic import BaseModel


class BreakerConf(BaseModel):
    # --- 熔断器配置 ---
    breaker_enabled: bool = False  # 是否启用熔断
    breaker_fail_max: int = 5  # 连续失败几次开启熔断
    breaker_reset_timeout: int = 30  # 熔断多少秒后半开
    # breaker_success_threshold: int = 3  # 半开时多少次成功才关闭熔断，当前库不支持，默认1次成功就关闭
