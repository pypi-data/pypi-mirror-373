########################################################################################################################
# IMPORTS

import re
import unicodedata
import inflection

########################################################################################################################
# FUNCTIONS

def process_task_name(task_id):
    task_id = ''.join(
        f"_{unicodedata.name(c)}_" if not c.isalnum() else c for c in task_id 
        if c.isalnum() or (unicodedata.category(c) not in ('Cc', 'Cf', 'Cs', 'Co', 'Cn'))
    )
    task_id = inflection.parameterize(task_id, separator='_')
    task_id = task_id.lower()
    task_id = task_id.strip('_')
    task_id = re.sub(r'_+', '_', task_id)
    if task_id[0].isdigit():
        task_id = 'task_' + task_id
    return task_id
