from typing import MutableMapping


async def get_flag_svg_url(country_code: str) -> str:
    return f'https://cdn.kcak11.com/CountryFlags/countries/{country_code}.svg'


async def process_query_type(
        query: str,
        kwargs: MutableMapping[str, object],
        types: tuple[str, str] = ('name', 'id'),
) -> str:
    if (qtype := kwargs.pop("qtype", types[0] if isinstance(query, str) else types[1])) not in types:
        raise ValueError('Incorrect querry type specified. Valid options are: "name" or "id"')
    return str(qtype)
