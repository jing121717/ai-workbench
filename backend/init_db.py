#!/usr/bin/env python
"""初始化数据库并创建默认管理员账号"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.db.session import engine, Base
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.db.session import get_db


def init_database():
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成 ✓")

    db = next(get_db())
    try:
        repo = UserRepository(db)
        existing = repo.get_by_username("admin")
        if existing:
            print(f"管理员账号 admin 已存在 (id={existing.id})")
        else:
            user = repo.create(
                username="admin",
                password="Admin@123456",
                nickname="超级管理员",
            )
            user.is_superuser = True
            db.commit()
            print(f"管理员账号创建成功！")
            print(f"  用户名：admin")
            print(f"  密码：Admin@123456")
    finally:
        db.close()

    print("\n初始化完成 ✓")


if __name__ == "__main__":
    init_database()
