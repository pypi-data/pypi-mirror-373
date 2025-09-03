# mypackage/config.py
import os
import logging

class Config:
    def __init__(self, logger):
        self.logger = logger
        self._log_level = 0
        self.vars = ['LOG_LEVEL']
        
        self._update_logger_level()

    @property
    def LOG_LEVEL(self):
        return self._log_level

    @LOG_LEVEL.setter
    def LOG_LEVEL(self, value):
        self._log_level = value
        self._update_logger_level()

    def _update_logger_level(self):
        """Update logger according to current LOG_LEVEL."""
        if self._log_level == 0:
            # Remove all handlers and add NullHandler
            self.logger.handlers = []
            self.logger.addHandler(logging.NullHandler())
        else:
            log_level_map = {1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
            self.logger.setLevel(log_level_map.get(self._log_level, logging.WARNING))

            # Add console handler if none exists
            if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
                console_handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(name)s[%(asctime)s](%(levelname)s): %(message)s', datefmt='%H:%M:%S'
                )
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
            self.logger.propagate = False
        
    def update_from_environ(self, prefix: str):
        """
        Update config with environment variables of the form PREFIX_ENV_VAR
        """
        prefix = prefix.upper()
        
        for name in self.vars:
            env_var = f'{prefix}_{name.upper()}'
            if env_var in os.environ:
                val = os.environ[env_var]
                # type conversion based on current value type
                current_val = getattr(self, name)
                if isinstance(current_val, bool):
                    val = val.lower() in ("1", "true", "yes")
                elif isinstance(current_val, int):
                    val = int(val)
                elif isinstance(current_val, float):
                    val = float(val)
                setattr(self, name, val)
    
    def add_var(self, name, value):
        setattr(self, name, value)
        self.vars.append(name)
        
    def __repr__(self):
        globals_dict = {key: getattr(self, key) for key in self.vars}
        items_str = ", ".join(f"{k}={v!r}" for k, v in globals_dict.items())
        return f"{self.__class__.__name__}({items_str})"

package_name = __name__.split('.')[0].strip('_')
logger = logging.getLogger(package_name)
config = Config(logger)
