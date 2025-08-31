import importlib
import os
import warnings

from aider.dump import dump  # noqa: F401

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

AIDER_SITE_URL = "https://aider.devplus.co.kr"
AIDER_APP_NAME = "Aider(@Horizon)"

os.environ["OR_SITE_URL"] = AIDER_SITE_URL
os.environ["OR_APP_NAME"] = AIDER_APP_NAME
os.environ["LITELLM_MODE"] = "PRODUCTION"

# `import litellm` takes 1.5 seconds, defer it!

VERBOSE = False


class LazyLiteLLM:
    lazy_module = None

    def __getattr__(self, name):
        if name == "_lazy_module":
            return super()
        self.load_litellm()
        return getattr(self.lazy_module, name)

    def load_litellm(self):
        if self.lazy_module is not None:
            return

        if VERBOSE:
            print("Loading litellm...")

        self.lazy_module = importlib.import_module("litellm")

        self.lazy_module.suppress_debug_info = True
        self.lazy_module.set_verbose = False
        self.lazy_module.drop_params = True
        self.lazy_module._logging._disable_debugging()


litellm = LazyLiteLLM()

__all__ = [litellm]
