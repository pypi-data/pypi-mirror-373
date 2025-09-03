########################################################################################################################
# IMPORTS

import logging

import pandas as pd
from soda.sampler.sample_context import SampleContext
from soda.sampler.sampler import Sampler

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)


class CustomSampler(Sampler):
    def store_sample(self, sampler_context: SampleContext):
        rows = sampler_context.sample.get_rows()
        schema_columns = [column.name for column in sampler_context.sample.get_schema().columns]
        df = pd.DataFrame(rows, columns=schema_columns)

        check_name = sampler_context.check_name

        if not df.empty:
            logger.info(f'"{check_name}" head:\n%s', df.head(10))
        else:
            logger.info(f'"{check_name}" returned empty.')
