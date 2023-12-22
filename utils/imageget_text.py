import cv2
import easyocr
import asyncio

semaphore = asyncio.Semaphore(1)


async def image_to_text_async(path, lang):
    image = cv2.imread(path)
    reader = easyocr.Reader([lang], gpu=False)
    text = reader.readtext(image)
    await asyncio.sleep(1)
    output = ''
    for i in text:
        output += f'\n {i[-2]}'
    return output


# async def process_images(paths, lang):
#     tasks = [image_to_text_async(path, lang) for path in paths]
#     results = await asyncio.gather(*tasks)
#     return results
