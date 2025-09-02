from django.core.exceptions import BadRequest
from django.http import HttpResponse
from import_export.formats.base_formats import CSV
from import_export.formats.base_formats import XLS
from import_export.formats.base_formats import XLSX
from import_export.resources import ModelResource
from import_export.signals import post_export

from csu.timezones import adjust_dt
from csu.timezones import now

EXPORT_FORMATS = {
    "XLSX": XLSX,
    "XLS": XLS,
    "CSV": CSV,
}


class RenderExportViewMixin:
    export_resource_class: type[ModelResource]
    export_formats = ("XLSX", "XLS", "CSV")
    export_filename_prefix = "export"
    export_filename_time = "%Y-%m-%d_%H%M"

    def get_export_filename_prefix(self):
        return self.export_filename_prefix

    def render_to_response(self, context, **response_kwargs):
        params = self.request.GET
        if params.get("action") == "export":
            file_format: str = params["format"]
            if file_format not in self.export_formats:
                raise BadRequest
            file_format_instance = EXPORT_FORMATS[file_format]()
            filters_repr = "".join(
                f"-{key}={value.replace(':', '')}"
                for key, raw_value in params.items()
                if key not in ("action", "format")
                for value in (raw_value.strip(),)
                if value
            )
            object_list = context["object_list"]
            data = self.export_resource_class().export(object_list)
            file_dt = adjust_dt(now()).strftime(self.export_filename_time)
            file_prefix = self.get_export_filename_prefix()
            file_content = file_format_instance.export_data(data)
            file_ext = file_format_instance.get_extension()
            if not file_format_instance.is_binary():
                file_content = file_content.encode()
            content_type = file_format_instance.get_content_type()
            response = HttpResponse(file_content, content_type=content_type)
            response["Content-Disposition"] = f'attachment; filename="{file_prefix}-{file_dt}{filters_repr}.{file_ext}"'
            post_export.send(sender=None, model=self.export_resource_class._meta.model)
            return response
        else:
            return super().render_to_response(context, **response_kwargs)
