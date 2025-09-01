"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import argparse
import json
import os
import sys
from io import StringIO
from pathlib import Path

from lxml import etree
from openpyxl.reader.excel import load_workbook
from validataclass.exceptions import ValidationError

from parkapi_sources import ParkAPISources
from parkapi_sources.models import StaticParkingSiteInput, RealtimeParkingSiteInput

sys.path.append(str(Path(Path(__file__).parent.parent, 'src')))  # noqa: E402

from parkapi_sources.converters.base_converter.push import CsvConverter, JsonConverter, XlsxConverter, XmlConverter
from parkapi_sources.util import DefaultJSONEncoder

DATA_TYPES = {
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'csv': 'text/csv',
    'xml': 'application/xml',
    'json': 'application/json',
}


def main():
    parser = argparse.ArgumentParser(
        prog='ParkAPI-Sources Test Script',
        description='This script helps to develop ParkAPI-Sources converter',
    )
    parser.add_argument('source_uid')
    parser.add_argument('file_path')
    args = parser.parse_args()
    source_uid: str = args.source_uid
    file_path: Path = Path(args.file_path)

    if not file_path.is_file():
        sys.exit('Error: please add a file as second argument.')

    file_ending = None
    for ending in DATA_TYPES:
        if file_path.name.endswith(f'.{ending}'):
            file_ending = ending

    if file_ending is None:
        sys.exit(f'Error: invalid ending. Allowed endings are: {", ".join(DATA_TYPES.keys())}')

    config = dict(os.environ)
    config['STATIC_GEOJSON_BASE_PATH'] = Path(Path(__file__).parent.parent, 'data')

    parkapi_sources = ParkAPISources(config=config, converter_uids=[source_uid])
    parkapi_sources.check_credentials()

    if file_ending == 'xlsx':
        converter: XlsxConverter = parkapi_sources.converter_by_uid  # type: ignore
        workbook = load_workbook(filename=str(file_path.absolute()))
        parking_site_inputs, import_parking_site_exceptions = converter.handle_xlsx(workbook)

    elif file_ending == 'csv':
        converter: CsvConverter = get_converter(source_uid, CsvConverter)  # type: ignore
        with file_path.open() as csv_file:
            csv_data = StringIO(csv_file.read())
        parking_site_inputs, import_parking_site_exceptions = converter.handle_csv_string(csv_data)

    elif file_ending == 'xml':
        converter: XmlConverter = get_converter(source_uid, XmlConverter)  # type: ignore
        with file_path.open('br') as xml_file:
            root_element = etree.fromstring(xml_file.read(), parser=etree.XMLParser(resolve_entities=False))  # noqa: S320
        parking_site_inputs, import_parking_site_exceptions = converter.handle_xml(root_element)

    else:
        converter: JsonConverter = get_converter(source_uid, JsonConverter)  # type: ignore
        with file_path.open() as json_file:
            data = json.load(json_file)
        parking_site_inputs, import_parking_site_exceptions = converter.handle_json(data)

    print('### data ###')  # noqa: T201
    for parking_site_input in parking_site_inputs:
        print(json.dumps(filter_none(parking_site_input.to_dict()), indent=2, cls=DefaultJSONEncoder))  # noqa: T201

    print(f'parking_site_errors: {import_parking_site_exceptions}')  # noqa: T201

    # Additional re-validation if mapping was set up correctly
    for parking_site_input in parking_site_inputs:
        parking_site_dict = json.loads(json.dumps(filter_none(parking_site_input.to_dict()), cls=DefaultJSONEncoder))
        try:
            if isinstance(parking_site_input, StaticParkingSiteInput):
                converter.static_parking_site_validator.validate(parking_site_dict)
            elif isinstance(parking_site_input, RealtimeParkingSiteInput):
                converter.realtime_parking_site_validator.validate(parking_site_dict)
        except ValidationError as e:
            print(f'Invalid mapped dataset found: {parking_site_dict}: {e.to_dict()}')


def filter_none(data: dict) -> dict:
    return {key: value for key, value in data.items() if value is not None}


if __name__ == '__main__':
    main()
