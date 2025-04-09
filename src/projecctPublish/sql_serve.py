# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：web
@File ：sql_serve.py
@Time ：2024/11/7 15:14 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@sql_serve.py功能简介：

"""
from src.config import database_table
from src.mysql_tool import DatabaseConnector
from mysql.connector import Error


class DatabaseServe:
    """
    打包数据库服务
    """

    #     """
    #     创建保存数据的数据服务
    #      CREATE TABLE diyhome_new_4_packages (
    #     id INT PRIMARY KEY AUTO_INCREMENT,
    #     packager VARCHAR(255) ,
    #     start_time VARCHAR(255) ,
    #     end_time VARCHAR(255) ,
    #     resource_version VARCHAR(255),
    #     rule_version VARCHAR(255),
    #     product_version VARCHAR(255),
    #     status VARCHAR(255)
    # );

    # INSERT INTO diyhome_new_4_packages (
    #         packager, start_time, end_time,
    #         resource_version, rule_version,
    #         product_version, status
    #     ) VALUES (
    #         'John Doe',
    #         '2024-11-07 08:00:00',
    #         '2024-11-08 08:00:00',
    #         'v1.2.3',
    #         'v1.0',
    #         'v2.0',
    #         'active'
    #     );

    #     """
    def __init__(self):
        self.connector = DatabaseConnector(host="10.8.110.248", user="root", password="Jd123456",
                                           database="packaging")
        self.connector.connect()
        self.database_columns = ['packager', 'start_time', 'end_time', 'resource_version', 'rule_version',
                                 'product_version', 'status', 'environment']
        self.select_columns = ['序号', '打包人', '打包开始时间', '打包结束时间', '资源包版本', '规则包版本',
                               '产品包版本', '打包状态', '打包环境']
        # self.table = 'diyhome3packages' # 3.0
        self.table = database_table  # 4.0

    def insert_data(self, values):
        try:
            self.connector.insert_data(table=self.table, columns=self.database_columns, values_list=values)
            return self.select_data(page=-1)[0]
            # cursor.execute("SELECT LAST_INSERT_ID()")
            # print(self.connector.connection.lastrowid)
        except Exception as e:
            print(e)

    def select_data(self, page=False):
        return self.connector.read_mysql_use_pandas(table=self.table, limit=page, close=True).astype(str).to_dict(
            'records')

    def updata_data(self, data: dict, datab_id=None, condition=None):
        try:
            if condition is not None:
                return self.connector.update_data(table=self.table,
                                                  data=data,
                                                  # {'end_time': "2023-12-04 15:05:17", "resource_version": "1111",
                                                  #       'rule_version': '1231'},
                                                  condition=condition, close=True)
            elif datab_id is not None:
                return self.connector.update_data(table=self.table,
                                                  data=data,
                                                  # {'end_time': "2023-12-04 15:05:17", "resource_version": "1111",
                                                  #       'rule_version': '1231'},
                                                  condition=f' id={datab_id} ', close=True)
        except Exception as e:
            print(e)

    def add_or_updata_user(self, user_name, account_name, account_password):
        """
        添加或更新用户信息
        :param user_name:
        :param account_name:
        :param account_password:
        :return:
        """
        # """
        # CREATE TABLE users (
        #     id INT AUTO_INCREMENT PRIMARY KEY,  -- 自增的用户 ID
        #     user_name VARCHAR(100) NOT NULL,    -- 用户姓名
        #     account_name VARCHAR(50) NOT NULL UNIQUE,  -- 账户名，唯一
        #     account_password VARCHAR(255) NOT NULL  -- 账户密码
        # );
        # INSERT INTO users (user_name, account_name, account_password)
        #     VALUES ('张三', 'zhangsan', 'encrypted_password');
        #
        # """
        try:
            cursor = self.connector.connection.cursor()
            # 1. 检查账户是否已经存在
            cursor.execute("SELECT * FROM users WHERE account_name = %s", (account_name,))
            existing_user = cursor.fetchone()

            if existing_user:
                # 2. 如果账户存在，检查密码是否一致
                stored_password = existing_user[3]  # 假设密码在第 4 列（索引为 3）
                if stored_password == account_password:
                    print("密码一致，账户无需更改")
                else:
                    # 3. 如果密码不一致，更新密码
                    cursor.execute("""
                                UPDATE users
                                SET account_password = %s
                                WHERE account_name = %s
                            """, (account_password, account_name))
                    self.connector.connection.commit()
                    print("密码已更新")
            else:
                # 4. 如果账户不存在，插入新用户
                cursor.execute("""
                            INSERT INTO users (user_name, account_name, account_password)
                            VALUES (%s, %s, %s)
                        """, (user_name, account_name, account_password))
                self.connector.connection.commit()
                print("新用户已添加")
        except Error as e:
            print("数据库错误:", e)
        finally:
            if self.connector.connection.is_connected():
                self.connector.close()
                self.connector.connection.close()


if __name__ == '__main__':
    pass
    a = DatabaseServe()
    a.add_or_updata_user('胡邦国', '11031840', '1234567')
