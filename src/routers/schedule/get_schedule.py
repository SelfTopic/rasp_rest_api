from flask import Flask, request, jsonify, send_file
from src.services import ScheduleParserService, ValidateRequestService

def route(app: Flask) -> None:

    @app.route("/schedule/<day>/<group>")
    def schedule_get(day: str, group: str):

        validate_request_service = ValidateRequestService()

        is_valid_day = validate_request_service.is_valid_day(day)

        if not is_valid_day:
            return jsonify({ "err": True, "message": "Day not valid type" })
        
        headers = request.headers
        secret_token = headers.get("Token-Self", default=None)
        print(f"Headers: {headers}")

        if not secret_token:
            return jsonify({ "err": True, "message": "Auth failed" })

        if not validate_request_service.is_valid_token(token=secret_token):
            return jsonify({ "err": True, "message": "Auth failed" })
        
        schedule_parser = ScheduleParserService(group_name=group)

        schedule = schedule_parser.generate_schedule_images()

        if not schedule:
            return jsonify({ "err": True, "message": "Error generate photo" })
        
        if day == "today":
            return send_file(f"../images/{schedule[0]}", mimetype="image/png")
        
        elif day == "tommorow":
            return send_file(f"../images/{schedule[1]}", mimetype="image/png")
        
        else: 
            return jsonify({ "err": True, "message": "Day type is not valid"})

    return None