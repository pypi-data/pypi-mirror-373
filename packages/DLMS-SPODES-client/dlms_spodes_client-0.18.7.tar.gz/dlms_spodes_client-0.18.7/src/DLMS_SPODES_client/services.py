from .client import Client, Network, IDFactory, c_pf
import csv
from itertools import count
from .settings import settings


_h: dict[str, [str]] = dict(settings.from_csv.header_names)
"""header names"""


class IpAddress:
    __value: list[int]

    def __init__(self, value: str = '127.0.0.1'):
        self.__value = list()
        for el1 in value.split('.'):
            if el1.isdigit():
                el = int(el1)
                if 0 <= el <= 255:
                    self.__value.append(el)
                else:
                    raise ValueError(F'Wrong digit in value: {el}, must be 0..255')
            else:
                raise ValueError(F'Value is not digit: {el1}')
        if len(self.__value) != 4:
            raise ValueError(F'Length of Ip address {value} must be 4, got {len(self.__value)}')

    @classmethod
    def is_valid(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False

    def __str__(self):
        return '.'.join(map(str, self.__value))


def get_client_from_csv(
        file_name: str,
        id_factory: IDFactory = None,
        universal: bool = False
) -> list[Client]:
    """file in utf-8 format"""
    da: str
    with open(file_name, 'r', encoding="utf-8-sig") as csv_file:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(csv_file.readline(1024))
        csv_file.seek(0)
        reader = csv.reader(csv_file, dialect=dialect)
        first_row: list[str] = next(reader)
        if any(map(IpAddress.is_valid, first_row)):  # search ip_address in first row
            # header is absence
            raise ValueError('Не найден заголовок таблицы')
        else:  # header is exist
            # search column by name
            column_name_count = count()
            field_names: list[str] = list()
            for index, cell in enumerate(first_row):
                for column in _h:
                    if any(map(cell.lower().startswith, _h[column])):
                        field_names.append(_h[column][0])
                        break
                else:
                    field_names.append(F'unknown{next(column_name_count)}')
            if all(map(lambda name: name in field_names, ('ip',))):
                csv_file.seek(0)
                reader = csv.DictReader(csv_file, fieldnames=field_names, dialect=dialect)
                next(reader)
                res: list[Client] = list()
                for i in reader:
                    if IpAddress.is_valid(i['ip']):
                        res.append(c := Client(
                            media=Network(
                                host=i.get("ip", "127.0.0.1"),
                                port="8888"
                            ),
                            id_=id_factory.create() if id_factory else None,
                            universal=universal
                        ))
                        c.com_profile.parameters.inactivity_time_out = int(i.get("timeout", 120))  # todo: work only for HDLC, make better
                        c.secret = bytes(i.get('secret', '0000000000000000'), 'utf-8')
                        if m_id := i.get('m_id'):
                            c.m_id.set(m_id)
                        if port := i.get('port'):
                            c.media.port = port
                        if sap := i.get('sap'):
                            c.SAP.set(sap)
                        if (
                            (da := i.get('da'))
                            and da.isdigit()
                        ):
                            c.com_profile.parameters.device_address = int(da)
                        if name := i.get("name"):
                            c.name = name
                return res
