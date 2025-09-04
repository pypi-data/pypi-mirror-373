import typing as t

from meili_sdk.exceptions import ValidationError
from meili_sdk.models.base import BaseModel


class Trigger(BaseModel):
    uuid: t.Optional[str] = None
    verbose_name: str
    token: t.Optional[str] = None
    url: t.Optional[str] = None
    use_http: t.Optional[bool] = True
    point: t.Optional[str] = None
    task_preset: t.Optional[str] = None
    use_ip_authentication: t.Optional[bool] = False
    use_token_authentication: t.Optional[bool] = False
    ip_whitelist: t.Optional[t.List[str]] = None
    action: str

    def validate_action(self):
        if self.action not in ["location_confirm", "location_fail", "task_launch"]:
            raise ValidationError(f"Invalid action {self.action}")
        return self.action

    def validate(self):
        super().validate()

        if not self.point and not self.task_preset:
            raise ValidationError("Neither point nor task_preset were defined")
