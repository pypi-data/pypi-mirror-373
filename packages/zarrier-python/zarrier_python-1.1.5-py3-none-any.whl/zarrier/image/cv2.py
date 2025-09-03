import cv2


def put_text(img, text, point, font_scale=1, color=(0, 0, 255), thickness=5):
    """不支持中文, 注意，point为文字中心坐标"""
    size = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=font_scale, thickness=thickness)
    return cv2.putText(img, text, (int(point[0] - size[0][0]//2), point[1] + size[0][1]//2), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=font_scale, color=color, thickness=thickness)



