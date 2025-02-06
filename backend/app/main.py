"""
FastAPI Main Application Entry Point

This file serves as the main entry point for the FastAPI application.
It contains:
- Application initialization and configuration
- CORS middleware setup
- Global exception handlers
- Health check endpoints
- Database connection test endpoints
- API router inclusion for different versions

Dependencies:
- FastAPI framework
- SQLAlchemy for database operations
- Various internal modules from app package

Author: Minh An
Last Modified: 21 Jan 2025
Version: 2.0.0
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import API_V1_STR, API_V2_STR, PROJECT_NAME
from app.api.api_v1.api import api_router as api_v1_router
from typing import Dict


description = """
🚀 Tài Liệu API

## Tính Năng
* Quản Lý Người Dùng
* Quản Lý Mục
* Các Phép Toán
"""

app = FastAPI(
    title=PROJECT_NAME,
    description=description,
    version="2.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Hỗ Trợ API",
        "url": "http://example.com/support",
        "email": "support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Xử lý các tác vụ khởi động ứng dụng

    Chức năng:
    - Khởi tạo kết nối cơ sở dữ liệu
    - Thiết lập bộ nhớ đệm nếu cần
    - Khởi tạo các dịch vụ bên ngoài

    Raises:
        Exception: Ghi log các lỗi xảy ra trong quá trình khởi động
    """
    try:
        # Bạn có thể khởi tạo tài nguyên ở đây
        pass
    except Exception as e:
        print(f"Lỗi khởi động: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Xử lý các tác vụ khi tắt ứng dụng

    Chức năng:
    - Đóng kết nối cơ sở dữ liệu
    - Giải phóng tài nguyên
    - Lưu trạng thái nếu cần

    Raises:
        Exception: Ghi log các lỗi xảy ra trong quá trình tắt
    """
    try:
        # Bạn có thể dọn dẹp tài nguyên ở đây
        pass
    except Exception as e:
        print(f"Lỗi khi tắt: {e}")


@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """
    Kiểm tra trạng thái hoạt động của API

    Returns:
        Dict[str, str]: Từ điển chứa trạng thái và phiên bản API
            - status: Trạng thái hoạt động hiện tại
            - version: Số phiên bản API

    Example:
        Response: {"status": "hoạt động", "version": "2.0.0"}
    """
    return {
        "status": "hoạt động",
        "version": "2.0.0"
    }



# Xử lý ngoại lệ
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Xử lý các ngoại lệ HTTP

    Args:
        request: Request gây ra ngoại lệ
        exc: Đối tượng ngoại lệ HTTP

    Returns:
        JSONResponse: Phản hồi JSON chứa thông tin lỗi
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Xử lý các ngoại lệ chung

    Args:
        request: Request gây ra ngoại lệ
        exc: Đối tượng ngoại lệ

    Returns:
        JSONResponse: Phản hồi JSON chứa thông báo lỗi chung
    """
    return JSONResponse(
        status_code=500,
        content={"message": "Lỗi máy chủ nội bộ"},
    )


# Bao gồm các router
app.include_router(
    api_v1_router,
    prefix=API_V1_STR,
    tags=["API"]
)
