from flask import Flask, jsonify
from src.services import ScheduleParserService, ValidateRequestService

def route(app: Flask) -> None:

    @app.route("/schedule/<group>")
    def schedule_get_group(group: str):

        schedule_parser_service = ScheduleParserService(group)
        real_group = schedule_parser_service.find_group_schedule_url(group)
        
        return jsonify({ "group": real_group })
    
    return None