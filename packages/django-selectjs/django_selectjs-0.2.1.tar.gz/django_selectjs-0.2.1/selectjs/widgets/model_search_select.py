from django import forms


class ModelSearchSelectWidget(forms.Select):
    template_name = "widgets/model_search_select.html"

    def __init__(
        self,
        attrs=None,
        model=None,
        search_field="name",
        api_endpoint=None,
        min_length=3,
    ):
        super().__init__(attrs)
        self.model = model
        self.search_field = search_field
        self.api_endpoint = api_endpoint
        self.min_length = min_length

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["model"] = self.model._meta.model_name
        context["widget"]["app_label"] = self.model._meta.app_label
        context["widget"]["search_field"] = self.search_field
        context["widget"]["api_endpoint"] = self.api_endpoint
        context["widget"]["min_length"] = self.min_length
        if value:
            try:
                obj = self.model.objects.get(pk=value)
                context["widget"]["selected_text"] = str(obj)
            except self.model.DoesNotExist:
                context["widget"]["selected_text"] = ""
        else:
            context["widget"]["selected_text"] = ""
        return context

    class Media:
        css = {"all": ("css/model_search_select.css",)}
        js = ("js/model_search_select.js",)
