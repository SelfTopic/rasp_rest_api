from .loader import app 
from .routers.routes import ScheduleGetRoute, GetGroupRoute 
GetGroupRoute(app)
ScheduleGetRoute(app)
app.run("localhost", 5500)