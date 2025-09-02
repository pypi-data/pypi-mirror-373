from fastapi import HTTPException


NOT_FOUND = HTTPException(status_code=404, detail="数据不存在")






