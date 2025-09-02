from django.dispatch import receiver
from django.utils.translation import gettext as _
from rest_framework.reverse import reverse
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.signals.instance_buttons import add_extra_button


class NewsButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        buttons = set()
        buttons.add(bt.HyperlinkButton(key="open_link", label=_("Open News"), icon=WBIcon.LINK.icon))
        if self.request.user.is_superuser and (pk := self.view.kwargs.get("pk")):
            buttons.add(
                bt.ActionButton(
                    method=RequestType.PATCH,
                    identifiers=("wbnews:newsrelationship",),
                    endpoint=reverse("wbnews:news-refreshrelationship", args=[pk]),
                    action_label=_("Reset relationships"),
                    label=_("Reset relationships"),
                    icon=WBIcon.REGENERATE.icon,
                    title=_("Reset relationships"),
                )
            )
        return buttons

    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()


class NewsRelationshipButtonConfig(ButtonViewConfig):
    pass


@receiver(add_extra_button)
def add_new_extra_button(sender, instance, request, view, pk=None, **kwargs):
    if instance and pk and view:
        content_type = view.get_content_type()
        endpoint = f'{reverse("wbnews:newsrelationship-list", args=[], request=request)}?content_type={content_type.id}&object_id={pk}'
        return bt.WidgetButton(endpoint=endpoint, label="News", icon=WBIcon.NEWSPAPER.icon)
