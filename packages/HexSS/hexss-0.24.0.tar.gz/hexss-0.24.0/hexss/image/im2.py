from pathlib import Path
from typing import Optional, Tuple, List, Sequence, Self, Union

import hexss
from hexss.box import Box

hexss.check_packages('numpy', 'opencv-python', auto_install=True)

import numpy as np
import cv2


class Image2:
    def __init__(self, image: np.ndarray) -> None:
        self.image: np.ndarray = image  # BGR only, shape=(H,W,3) only

    @property
    def size(self) -> Tuple[int, int]:
        return self.image.shape[1::-1]

    def crop(
            self,
            xyxy: Optional[Union[Tuple[float, float, float, float], List[float], np.ndarray]] = None,
            xywh: Optional[Union[Tuple[float, float, float, float], List[float], np.ndarray]] = None,
            xyxyn: Optional[Union[Tuple[float, float, float, float], List[float], np.ndarray]] = None,
            xywhn: Optional[Union[Tuple[float, float, float, float], List[float], np.ndarray]] = None,
            points: Optional[Sequence[Tuple[float, float]]] = None,
            pointsn: Optional[Sequence[Tuple[float, float]]] = None,
            shift: Tuple[float, float] = (0, 0)
    ) -> Self:
        box = Box(self.size, xyxy=xyxy, xywh=xywh, xyxyn=xyxyn, xywhn=xywhn, points=points, pointsn=pointsn)
        box.move(*shift, normalized=False)
        if box.type == 'box':
            x1, y1, x2, y2 = box.xyxy
            return self.image[y1:y2, x1:x2]
        elif box.type == 'polygon':
            mask = np.zeros(self.image.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [box.points_int32()], 255)
            masked = cv2.bitwise_and(self.image, self.image, mask=mask)
            x, y, w, h = cv2.boundingRect(box.points_int32())
            return  masked[y:y + h, x:x + w]

    def resize(
            self,
            size: Optional[Tuple[int, int]] = None,
            fx: Optional[float] = None,
            fy: Optional[float] = None,
            interpolation: int = cv2.INTER_LINEAR,
    ) -> Self:
        """
        Example:
            resize((600,400))
            resize(fx=0.8) # 80%
        """
        if size is None:
            size = (0, 0)
        if fx is not None and fy is None:
            fy = fx
        self.image = cv2.resize(self.image, dsize=size, fx=fx, fy=fy, interpolation=interpolation)
        return self

    def copy(self) -> Self:
        return Image2(self.image.copy())

    def save(self, filename: Union[Path, str]) -> Self:
        filename = Path(filename)
        filename.parent.mkdir(exist_ok=True)
        cv2.imwrite(str(filename), self.image)
        return self
