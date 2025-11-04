# -*- coding: utf-8 -*-
import logging


def configure_logging() -> None:
    if logging.getLogger().handlers:
        # Já configurado por outro módulo
        return

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log', encoding='utf-8')
        ]
    )


