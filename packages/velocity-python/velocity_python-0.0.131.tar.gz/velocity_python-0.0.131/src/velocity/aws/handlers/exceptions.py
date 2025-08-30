class AppError(Exception):
    pass


class AccessError(AppError):
    pass


class AlertError(AppError):
    def get_payload(self):
        data = self.args[0]
        if isinstance(data, str):
            return {"message": data}
        elif isinstance(data, dict):
            return data
        return {"message": "No message was supplied to AlertError"}
