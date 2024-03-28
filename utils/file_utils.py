import zipfile
from io import BytesIO
from os import path, getcwd
from pathlib import Path
from typing import Union

import aiofiles
from aiofiles import os


async def extract_maps_from_osz_bytes(b: BytesIO) -> bool:
    with zipfile.ZipFile(b) as r:
        for i in r.infolist():
            if not i.filename.endswith('.osu'):
                continue

            f = r.read(i.filename)
            for line in BytesIO(f).readlines():
                sline = line.decode('utf8')

                if 'BeatmapID' not in sline:
                    continue

                beatmap_id = sline.split(':')[1].strip()
                async with aiofiles.open(path.join(getcwd(), 'osu', 'beatmaps', f'{beatmap_id}.osu'),
                                         'wb+') as nf:
                    await nf.write(f)
                break
    return True


async def path_exists(filepath: Union[Path, str]) -> bool:
    try:
        await aiofiles.os.stat(str(filepath))
    except OSError:
        return False
    except ValueError:
        return False
    return True
