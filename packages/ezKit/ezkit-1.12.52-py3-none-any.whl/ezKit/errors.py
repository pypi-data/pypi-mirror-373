# 内部错误: 1000
internal_error = {
    "type": {
        "code": 1001,
        "message": "type error",
    },
}

# HTTP错误: 2000
http_error = {
    "request_data": {
        "code": 2001,
        "message": "HTTP request data error",
    },
}

# 数据库错误: 3000
database_error = {
    "create": {
        "code": 3001,
        "message": "Database create data error",
    },
    "read": {
        "code": 3002,
        "message": "Database read data error",
    },
    "update": {
        "code": 3003,
        "message": "Database update data error",
    },
    "delete": {
        "code": 3004,
        "message": "Database delete data error",
    },
    "no_data": {
        "code": 3005,
        "message": "Database no data found",
    },
}

# SQLAlchemy错误: 4000
sqlalchemy_error = {
    "statement": {
        "code": 4001,
        "message": "SQLAlchemy statement error",
    },
    "params": {
        "code": 4002,
        "message": "SQLAlchemy params error",
    },
    "statement_params": {
        "code": 4003,
        "message": "SQLAlchemy statement or params error",
    },
    "build_statement": {
        "code": 4004,
        "message": "SQLAlchemy build statement error",
    },
    "build_params": {
        "code": 4005,
        "message": "SQLAlchemy build params error",
    },
    "build_where": {
        "code": 4006,
        "message": "SQLAlchemy build WHERE error",
    },
}
