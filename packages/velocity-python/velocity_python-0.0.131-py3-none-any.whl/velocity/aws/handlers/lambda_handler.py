import json
from velocity.aws.handlers.base_handler import BaseHandler
from velocity.aws.handlers.response import Response
from . import context

# TODO: helpers import needs to be resolved - may need to pass table name instead
# from some_app import helpers


class LambdaHandler(BaseHandler):
    def __init__(self, aws_event, aws_context, context_class=context.Context):
        super().__init__(aws_event, aws_context, context_class)

        # LambdaHandler-specific initialization
        requestContext = aws_event.get("requestContext") or {}
        identity = requestContext.get("identity") or {}
        headers = aws_event.get("headers") or {}
        auth = identity.get("cognitoAuthenticationProvider")
        self.session = {
            "authentication_provider": identity.get("cognitoAuthenticationProvider"),
            "authentication_type": identity.get("cognitoAuthenticationType"),
            "cognito_user": identity.get("user"),
            "is_desktop": headers.get("CloudFront-Is-Desktop-Viewer") == "true",
            "is_mobile": headers.get("CloudFront-Is-Mobile-Viewer") == "true",
            "is_smart_tv": headers.get("CloudFront-Is-SmartTV-Viewer") == "true",
            "is_tablet": headers.get("CloudFront-Is-Tablet-Viewer") == "true",
            "origin": headers.get("origin"),
            "path": aws_event.get("path"),
            "referer": headers.get("Referer"),
            "source_ip": identity.get("sourceIp"),
            "user_agent": identity.get("userAgent"),
            "sub": auth.split(":")[-1] if auth else None,
        }
        if self.session.get("is_mobile"):
            self.session["device_type"] = "mobile"
        elif self.session.get("is_desktop"):
            self.session["device_type"] = "desktop"
        elif self.session.get("is_tablet"):
            self.session["device_type"] = "tablet"
        elif self.session.get("is_smart_tv"):
            self.session["device_type"] = "smart_tv"
        else:
            self.session["device_type"] = "unknown"

    def serve(self, tx):
        response = Response()
        body = self.aws_event.get("body")
        postdata = {}
        if isinstance(body, str) and len(body) > 0:
            try:
                postdata = json.loads(body)
            except (json.JSONDecodeError, TypeError):
                postdata = {"raw_body": body}
        elif isinstance(body, dict):
            postdata = body
        elif isinstance(body, list) and len(body) > 0:
            try:
                new = "\n".join(body)
                postdata = json.loads(new)
            except (json.JSONDecodeError, TypeError):
                postdata = {"raw_body": body}

        req_params = self.aws_event.get("queryStringParameters") or {}
        local_context = self.ContextClass(
            aws_event=self.aws_event,
            aws_context=self.aws_context,
            args=req_params,
            postdata=postdata,
            response=response,
            session=self.session,
            log=lambda message, function=None: self.log(message, function),
        )

        # Determine action from postdata or query parameters
        action = postdata.get("action") or req_params.get("action")
        
        # Get the list of actions to execute
        actions = self.get_actions_to_execute(action)
        
        # Use BaseHandler's execute_actions method
        try:
            self.execute_actions(tx, local_context, actions)
        except Exception as e:
            self.handle_error(tx, local_context, e)
            
        return local_context.response().render()

    def track(self, tx, data={}, user=None):
        data = data.copy()
        data.update(
            {
                "source_ip": self.session["source_ip"],
                "referer": self.session["referer"],
                "user_agent": self.session["user_agent"],
                "device_type": self.session["device_type"],
                "sys_modified_by": self.session["email_address"],
            }
        )
        # TODO: Fix undefined helpers reference
        # tx.table(helpers.get_tracking_table(user or self.session)).insert(data)

    def OnActionDefault(self, tx, context):
        context.response().set_body(
            {"event": self.aws_event, "postdata": context.postdata()}
        )

    def OnActionTracking(self, tx, context):
        self.track(tx, context.payload().get("data", {}))
