from .loader import app 
from .routers.routes import ScheduleGetRoute, GetGroupRoute 
GetGroupRoute(app)
ScheduleGetRoute(app)
app.run("0.0.0.0", 5500)