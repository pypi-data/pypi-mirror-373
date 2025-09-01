import pandas as pd
import json
from datetime import datetime
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()  # Convert to string
        return super().default(obj)
