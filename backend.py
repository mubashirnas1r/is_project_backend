import os
import base64
from PIL import Image
from stegano import lsb
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse

os.makedirs('encryption_images',exist_ok=True)
os.makedirs('decryption_images',exist_ok=True)

async def string_to_binary(string):
    binary_data = ''.join(format(ord(char), '08b') for char in string)
    return binary_data

# async def hide_text(image_path, secret_text, output_path):
#     image = Image.open(image_path)
#     binary_text = await string_to_binary(secret_text)

#     data_index = 0
#     img_data = list(image.getdata())

#     for pixel_index in range(len(img_data)):
#         pixel = list(img_data[pixel_index])

#         for i in range(3):
#             if data_index < len(binary_text):
#                 pixel[i] = pixel[i] & ~1 | int(binary_text[data_index])
#                 data_index += 1

#         img_data[pixel_index] = tuple(pixel)

#     new_image = Image.new(image.mode, image.size)
#     new_image.putdata(img_data)
#     new_image.save(output_path)

async def extract_length(input_string):
    import re
    match = re.match(r'\d+', input_string)
    if match:
        return int(match.group())
    else:
        return None
# async def reveal_text(image_path):
#     image = Image.open(image_path)
#     img_data = list(image.getdata())

#     binary_text = ''
#     for pixel_index in range(len(img_data)):
#         pixel = img_data[pixel_index]

#         for i in range(3):
#             binary_text += str(pixel[i] & 1)

#     decoded_text = ''.join(chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8))
#     return decoded_text
async def hide_text_in_image(image_path, text_to_hide, output_path):
    secret = lsb.hide(image_path, text_to_hide)
    secret.save(output_path)

async def reveal_text_from_image(image_path):
    secret = lsb.reveal(image_path)
    return secret
async def encrypt(message, key):
    cipher = AES.new(key, AES.MODE_CBC)
    encrypted_message = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    encrypted_message = base64.b64encode(encrypted_message).decode('utf-8')
    return iv+encrypted_message

async def decrypt(iv, encrypted_message, key):
    iv = base64.b64decode(iv)
    encrypted_message = base64.b64decode(encrypted_message)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = unpad(cipher.decrypt(encrypted_message), AES.block_size)
    return decrypted_message.decode('utf-8')

app = FastAPI()
origins = [
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/v1/encrypt")
async def encrypt_message(
    message: str = Form(...),
    password: str = Form(...),
    image: UploadFile = File(...),
):
    if len(password) != 16 and len(password) != 32:
        return JSONResponse(content={
            'success':False,
            'message':'Password must be of length either 16 or 32 characters.'
            },
            status_code=403
        )
      
    password = password.encode('utf-8')
    incoming_image_path = f"encryption_images/{image.filename}"
    with open(incoming_image_path, "wb") as f:
        f.write(image.file.read())
    output_path = f"encryption_images/encrypted_{image.filename}"[:-3]+"png"
    
    encrypted_message = await encrypt(message, password)
    encrypted_message = f"{str(len(encrypted_message))}_{encrypted_message}"
    await hide_text_in_image(incoming_image_path, encrypted_message, output_path)
    os.remove(incoming_image_path)
    response_headers = {
        'Content-Disposition': f'attachment; filename=encrypted_{image.filename[:-3]}png',
    }
    return FileResponse(output_path,status_code=200,filename="encrypted_"+image.filename[:-3]+"png",headers=response_headers)

@app.post("/v1/decrypt")
async def decrypt_message(
    password: str = Form(...),
    image: UploadFile = File(...),
):
    if len(password) != 16 and len(password) != 32:
        return JSONResponse(content={
            'success':False,
            'message':'Password must be of length either 16 or 32 characters'
            },
            status_code=403
        )
    password = password.encode('utf-8')
    incoming_image_path = f"decryption_images/{image.filename}"
    with open(incoming_image_path, "wb") as f:
        f.write(image.file.read())
    try:
        decoded_text = await reveal_text_from_image(incoming_image_path)
        start = len(str(await extract_length(decoded_text)))+1
        end = await extract_length(decoded_text)+int(len(str(await extract_length(decoded_text))))+1
    except:
        return JSONResponse(content={
            'success':False,
            'message':'No Encryption found in the provided image!'
            },
            status_code=404
        )
    try:
        decrypted_message = await decrypt(decoded_text[start:end][:24],decoded_text[start:end][24:],password)
        os.remove(incoming_image_path)
        return JSONResponse(content={
            "success":True,
            "message":decrypted_message
            },
            status_code=200
        )
    except:
        return JSONResponse(content={
            'success':False,
            'message':"Incorrect password for the found encryption! Please Enter a valid password."
            },
            status_code=401
        )