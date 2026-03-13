import logging  # Main logging API
import logging.config  # allows you to configure logging via dictionary.


LOGGING_CONFIG = {

    #This is required for dictConfig.
    "version": 1,

    # Controls whether loggers from external libraries will be disabled.
    # False = Libraries cannot continue generating logs.
    "disable_existing_loggers": False,

    "formatters": {

        # formatter Defines how the log will be displayed.
        # "% horário | %nivel_log | %nome_modulo | %mensagem"
        # Exemplo:
        # 2026-03-13 20:14:03 | INFO | services.trello_service | Criando card
        "standard": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        }
    },

    # Handlers determine where the logs go.
    "handlers": {

        "console": {
            # Logs appear in the terminal
            # Levels displayed:: INFO, WARNING, ERROR
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO"
        },

        "file": {
            # All logs are saved to a file.
            # include DEBUG
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "formatter": "standard",
            "level": "DEBUG"
        }
    },

    # controls the application loggers
    "loggers": {

        # "" represents the ROOT LOGGER (all modules)
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",

            # prevent logs from being duplicated
            "propagate": False
        }
    }
}


import os
import logging.config

# ... (seu dicionário LOGGING_CONFIG continua igual)

def setup_logging():
    #Get absolute path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(base_dir, "logs")
    log_file = os.path.join(log_dir, "app.log")

    #Create logs path
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Force the dictionary to use the absolute path we just created.
    LOGGING_CONFIG["handlers"]["file"]["filename"] = log_file

    # 4.Config Logs
    logging.config.dictConfig(LOGGING_CONFIG)
