import importlib
import io
from typing import List, Union, Tuple

from starlette.responses import StreamingResponse
from tortoise.models import Model
from tortoise.queryset import QuerySetSingle

from fastgenerateapi import BaseView
from fastgenerateapi.api_view.mixin.response_mixin import ResponseMixin


class PdfUtil:

    async def export_pdf(
            self,
            model: Model,
            fields_list: List[List[Union[str, Tuple[str]]]],
            data: List[List[str]],
            # rpc_param: Union[Dict[str, Dict[str, List[str]]], Type[RPCParam], None] = None,
            font: str = "msyh",
            font_path: str = None,
            modules: str = "fpdf"
    ) -> StreamingResponse:
        """
        fields_list: [["名字", ("name", "名字"), (数据库字段， 字段中文名)], [第二行]]

        """
        limit_modules = ["fpdf"]
        if modules not in limit_modules:
            return ResponseMixin.error(msg=f"export xlsx modules only import {'、'.join(limit_modules)}")
        try:
            pdf = importlib.import_module(modules).FPDF()
        except Exception:
            return ResponseMixin.error(msg=f"please pip install {modules}")
        pdf.add_page()
        pdf.add_font(font, '', font_path if font_path else f"../font/{font}.ttf", True)
        pdf.set_font(font, '', 8)
        if data:
            for data_row in data:
                data_row_width = 180 / len(data_row)
                for data_col in data_row:
                    pdf.cell(data_row_width, 8, data_col)
                pdf.ln(10)
        else:
            async def write(model_single_obj):
                fields_data = []
                for fields in fields_list:
                    for field in fields:
                        if type(field) == tuple:
                            fields_data.append(field[0])
                model_data = await BaseView.getattr_model(model_single_obj, fields_data)
                # model_data = await self.setattr_model_rpc(self.model_class, model_data, rpc_param)
                for fields in fields_list:
                    cell_width = 180 / len(fields)
                    for field in fields:
                        if type(field) == str:
                            msg = f"{field[1]}"
                        else:
                            msg = f"{field[1]} {getattr(model_data, field[0]) if getattr(model_data, field[0]) else ''}"
                        pdf.cell(cell_width, 8, msg)
                    pdf.ln(10)

            if type(model) == QuerySetSingle:
                await write(model)
            else:
                for model_obj in model:
                    await write(model_obj)
                    pdf.add_page()
        byte_string = pdf.output(dest="S").encode('latin-1')
        bytes_io = io.BytesIO(byte_string)

        return ResponseMixin.stream(bytes_io, is_pdf=True)



