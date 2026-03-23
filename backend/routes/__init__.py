# Import all route modules to make them available when importing from routes
# This fixes the import error in main.py where 'from routes import predictions' etc. was failing

from . import predictions
from . import alerts
from . import recommendations
from . import feature
from . import vitals
from . import adherence
from . import noshow
from . import deterioration_risk
from . import escalation
from . import chatbot