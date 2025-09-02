from django.apps import apps
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.views.generic import View


class SelectJSView(View):
    # @method_decorator(require_GET)
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        field = request.GET.get("field", "")
        model_ref = request.GET.get("model", "")

        if not query or not field or not model_ref:
            return JsonResponse({"results": []})

        try:
            app_label, model_name = model_ref.split(".")
            model = apps.get_model(app_label, model_name)

            # Build filter for case-insensitive search
            filter_kwargs = {f"{field}__icontains": query}
            results = model.objects.filter(**filter_kwargs)[
                :10
            ]  # Limit to 10 results

            # Format results as JSON
            results_json = [
                {"id": obj.pk, "text": str(obj)} for obj in results
            ]

            return JsonResponse({"results": results_json})
        except (ValueError, LookupError):
            return JsonResponse({"results": []})
