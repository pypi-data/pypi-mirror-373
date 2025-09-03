import os
from ..string import zjoin
import cv2
from typing import Iterator


class ImageLoader:

    def __init__(self, dir: str, exts=[".jpg", ".jpeg", ".png", ".bmp", ".tif"], recursive=False) -> None:
        dir = os.path.abspath(dir)
        self.dir = dir
        self.exts = exts

        fnames = next(os.walk(self.dir))[2]
        self.paths = []
        self.names = []
        for fname in fnames:
            if os.path.splitext(fname)[-1].lower() not in self.exts:
                continue
            self.names.append(fname)
            self.paths.append(zjoin(self.dir, fname))

        self.recursive = recursive

    def walk(self):
        pass

    def load(self, read=True) -> Iterator[tuple[str, str, cv2.typing.MatLike]]:
        """
        return name, path , cv2.imread(path)
        """
        for name, path in zip(self.names, self.paths):
            if read:
                yield name, path, cv2.imread(path)
            else:
                yield name, path, None
