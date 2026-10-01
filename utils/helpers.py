import base64
from fastapi import HTTPException, status


def decode_photo(path, encoded_string):
    with open(path, "wb") as f:
        try:
            f.write(base64.b64decode(encoded_string.encode("utf-8")))
        except Exception as ex:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid photo encoding"
            )
