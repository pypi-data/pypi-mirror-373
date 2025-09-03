from .WriterNonCDC import WriterNonCDC
from .WriterCDC import WriterCDC


def factory(env, struct, migrator_redshift_connector, update_by_cdc, logger):
    if update_by_cdc is False:
        return WriterNonCDC(
            env=env,
            struct=struct,
            migrator_redshift_connector=migrator_redshift_connector,
            logger=logger,
        )
    else:
        return WriterCDC(
            env=env,
            struct=struct,
            migrator_redshift_connector=migrator_redshift_connector,
            logger=logger,
        )
