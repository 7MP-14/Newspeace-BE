DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.mysql',
        'NAME' : 'joon_db',
        'USER' : 'admin',
        'PASSWORD' : 'admin12345',
        'HOST' : 'joon-sql-db-1.cvtb5zj20jzi.ap-northeast-2.rds.amazonaws.com',
        'PORT' : 3306,
        'OPTIONS' : {
            'init_command' : "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}