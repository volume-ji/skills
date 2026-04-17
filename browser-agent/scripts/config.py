import os
from e2b import Sandbox

# ========== 配置 ==========
# 可通过环境变量设置，或在此处直接修改
E2B_DOMAIN = os.getenv("E2B_DOMAIN", "ap-guangzhou.tencentags.com")
E2B_API_KEY = os.getenv("E2B_API_KEY", "")
E2B_ags_template = os.getenv("E2B_AGS_TEMPLATE", "")

# os.environ["E2B_DOMAIN"] = E2B_DOMAIN
# os.environ["E2B_API_KEY"] = E2B_API_KEY
