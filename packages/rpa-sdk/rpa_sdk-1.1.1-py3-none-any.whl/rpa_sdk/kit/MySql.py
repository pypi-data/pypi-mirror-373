import re
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Tuple, List, Union, Dict, Any

from dateutil.relativedelta import relativedelta

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

try:
    import pymysql
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False
    pymysql = None


class DatabaseManager:
    """数据库连接管理类"""

    def __init__(self, host, port, user, password, database):
        self.db_config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'autocommit': True
        }

        # 只有在有pymysql时才设置cursorclass
        if HAS_PYMYSQL:
            self.db_config['cursorclass'] = pymysql.cursors.DictCursor

    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文"""
        if not HAS_PYMYSQL:
            raise ImportError("pymysql 模块未安装，无法创建数据库连接")

        conn = pymysql.connect(**self.db_config)
        try:
            yield conn
        finally:
            conn.close()

    def read_sql(self, sql: str) -> Union['pd.DataFrame', List[Dict[str, Any]]]:
        """执行SQL查询并返回DataFrame或字典列表

        Args:
            sql: 要执行的SQL查询语句

        Returns:
            pd.DataFrame 或 List[Dict]: 包含查询结果的DataFrame（如果有pandas）或字典列表

        Raises:
            pymysql.Error: 数据库操作异常时抛出
            ImportError: 如果没有安装必要的依赖

        Example:
            result = db.read_sql("SELECT * FROM users")
        """
        if not HAS_PYMYSQL:
            raise ImportError("pymysql 模块未安装，无法执行数据库操作")

        if not isinstance(sql, str):
            raise TypeError("SQL语句必须是字符串类型")

        if not sql.strip():
            raise ValueError("SQL语句不能为空")

        try:
            with self.get_connection() as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    result = cursor.fetchall()

                    if HAS_PANDAS:
                        return pd.DataFrame(result)
                    else:
                        return list(result)  # 返回字典列表
        except Exception as e:
            if HAS_PYMYSQL and isinstance(e, pymysql.Error):
                raise  # 直接抛出原始数据库异常
            else:
                raise RuntimeError(f"数据库操作失败: {str(e)}")

    def get_region(self, area_id: str) -> str:
        """
        根据区域ID获取区域名称
        Args:
            area_id: 区域ID (对应bs_area表id字段)
        Returns:
            str: 区域名称，未找到返回None

        Raises:
            ValueError: 参数格式错误
            pymysql.Error: 数据库操作异常

        Example:
            region_name = db.getRegion("440118000000")
        """
        # 防御性校验
        if not isinstance(area_id, str):
            raise ValueError("区域ID必须是字符串类型")

        # 使用参数化查询
        sql = """
            SELECT name 
            FROM bs_area 
            WHERE id = %s
            AND status = 1  -- 假设状态1为有效数据
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (area_id,))
                    result = cursor.fetchone()
                    return result['name'] if result else None

        except pymysql.Error as e:
            raise pymysql.Error(f"查询区域失败: {str(e)}") from e

    def get_doctor(self, area_name: str) -> str:
        """
        根据区域ID获取区域名称
        Args:
            area_name: 区域name (对应bs_area表id字段)
        Returns:
            str: 区域名称，未找到返回None

        Raises:
            ValueError: 参数格式错误
            pymysql.Error: 数据库操作异常

        Example:
            region_name = db.get_doctor("凤宁居委会")
        """
        # 防御性校验
        if not isinstance(area_name, str):
            raise ValueError("区域ID必须是字符串类型")

        # 使用参数化查询
        sql = """
            SELECT doctor 
            FROM bs_area 
            WHERE name = %s
            AND status = 1  -- 假设状态1为有效数据
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (area_name,))
                    result = cursor.fetchone()
                    return result['doctor'] if result else None

        except pymysql.Error as e:
            raise pymysql.Error(f"查询区域失败: {str(e)}") from e

    def update_tag(
            self,
            table_name: str,
            key_field: str,
            key_value: str,
            tag:str
                   ):
        """
        更新指定记录的tag字段

        Args:
            table_name: 表名（需通过白名单校验）
            key_field: 主键字段名
            key_value: 主键值
            tag: 人群标识
        Returns:
            int: 受影响的行数

        Raises:
            ValueError: 参数校验失败
            pymysql.Error: 数据库操作异常

        Example:
            db.update_tag(
                table_name="bs_archives",
                key_field="idcard",
                key_id=6275,
                tag="高血压“,
            )
        """
        sql = f"""
            UPDATE {table_name}
            SET tag = %s
            WHERE {key_field} = %s
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    affected_rows = cursor.execute(sql, (tag, key_value))
                    # 显式提交（虽然autocommit=True，但确保事务）
                    conn.commit()
                    return affected_rows
        except pymysql.Error as e:
            conn.rollback()  # 显式回滚
            raise pymysql.Error(f"更新失败: {str(e)}") from e



    def get_abo_hr(self, physical_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        根据体检ID (physical_id) 从 bu_report_data 表中查询ABO血型和Rh(D)血型。
        Args:
            physical_id: 体检ID字符串。

        Returns:
            一个元组 (abo_blood_type, rh_blood_type)。
            如果对应的血型信息未找到，则该值为 None。
            例如: ('A', '阳性'), (None, '阴性'), ('B', None), (None, None)

        Raises:
            ValueError: 如果 physical_id 不是字符串或为空。
            pymysql.Error: 如果在数据库查询过程中发生错误。

        Example:
            abo, hr = db.get_abo_hr("some_physical_id_123")
            if abo:
                print(f"ABO血型: {abo}")
            if hr:
                print(f"Rh(D)血型: {hr}")
        """
        if not isinstance(physical_id, str):
            raise ValueError("体检ID (physical_id) 必须是字符串类型。")
        if not physical_id.strip():
            raise ValueError("体检ID (physical_id) 不能为空。")

        abo_type: Optional[str] = None
        rh_type: Optional[str] = None

        # SQL 查询语句，使用 IN 子句匹配两种血型名称
        # 参数化查询 (%s) 用于防止SQL注入
        sql = """
               SELECT name, value 
               FROM bu_report_data 
               WHERE physical_id = %s AND name IN ('ABO血型', 'Rh(D)血型')
           """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (physical_id,))
                    results = cursor.fetchall()  # fetchall() 因为 DictCursor 返回字典列表

                    # 遍历查询结果，提取ABO和Rh(D)血型的值
                    for row in results:
                        if row['name'] == 'ABO血型':
                            abo_type = row['value']
                        elif row['name'] == 'Rh(D)血型':
                            rh_type = row['value']

                    return abo_type, rh_type
        except pymysql.Error as e:
            # 在发生数据库错误时，可以记录日志并抛出自定义异常或原始异常
            # logger.error(f"Database error fetching blood types for physical_id {physical_id}: {e}")
            raise pymysql.Error(f"查询血型失败 (physical_id: {physical_id}): {str(e)}") from e
        except Exception as e:
            # 捕获其他可能的意外错误
            # logger.error(f"Unexpected error fetching blood types for physical_id {physical_id}: {e}")
            raise RuntimeError(f"获取血型时发生未知错误 (physical_id: {physical_id}): {str(e)}") from e


    def get_referral_reason(self, idcard: str, date: str, disease_type: str) -> Optional[str]:
        """
        获取指定身份证号在给定日期之前最近一次随访的转诊原因（动态计算）
        Args:
            idcard: 身份证号
            date: 查询日期 (YYYY-MM-DD)
            disease_type: 疾病类型 ('高血压' 或 '糖尿病')

        Returns:
            str: 转诊原因字符串（多个原因用分号分隔）
            None: 无转诊原因

        Raises:
            ValueError: 参数无效
            pymysql.Error: 数据库错误
        """
        # 参数校验
        if not idcard or not date or not disease_type:
            raise ValueError("身份证号、日期和疾病类型不能为空")

        if disease_type not in ['高血压', '糖尿病']:
            raise ValueError("疾病类型必须是 '高血压' 或 '糖尿病'")

        # 日期格式校验（简化版）
        if not re.match(r'\d{4}-\d{2}-\d{2}', date):
            raise ValueError("日期格式不正确，请使用 'YYYY-MM-DD' 格式")

        # 查询并计算转诊原因
        sql = """
            SELECT fn_check_referral(visit_id, %s) AS referral_reason
            FROM bu_visit_data
            WHERE idcard = %s
            AND visitDate <= %s
            ORDER BY visitDate DESC
            LIMIT 1
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (disease_type, idcard, date))
                    result = cursor.fetchone()

                    if result and result['referral_reason']:
                        return result['referral_reason']
                    return None
        except pymysql.Error as e:
            raise pymysql.Error(f"查询转诊原因失败: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"获取转诊原因时发生错误: {str(e)}") from e


    def get_next_visit_bp(self,date,idcard,age,sbp, dbp,all_visit_data):
        """
        血压随访日期计算
        返回格式: YYYY-MM-DD
        逻辑说明：
        1. 首先判断prev_transfer_bp状态值，如果状态值是1 ，并且控制不满意, 直接转诊。prev_transfer_bp是1 并且控制满意, 修改数据库的转诊状态改成0 下次随访时间三个月后，如果是0 .就继续下一步
        2. 判断是否达到危急值，如果达到危急值。就立即转诊，并且追加一次14天随访。并且给这个人标记状态，状态值1。后续除非控制满意，状态值归0，否则每次都转诊并且下次随访三个月后
        3. 判断历史追加次数。如果本次是第一次。就立即转诊。并且标记状态值1 .
        4.  控制不满意。历史追加次数小于1。就追加一次14天随访。
        5. 控制满意。 就增加三个月随访
        6. 65岁以下患者：血压≥140/90mmHg需14天内随访
        7. 65岁及以上患者：血压≥150/90mmHg需14天内随访
        8. 达标患者3个月后随访
        """

        # 连接数据库
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 查询转诊状态
                    sql = f"SELECT prev_transfer_bp FROM bs_archives WHERE idcard = %s"
                    cursor.execute(sql, (idcard,))
                    result = cursor.fetchone()

                    if result:
                        prev_transfer_bp = result['prev_transfer_bp']
                    else:
                        prev_transfer_bp = 0  # 默认不转诊

                    # 血压判断阈值
                    if age < 65:
                        threshold = (140, 90)
                    else:
                        threshold = (150, 90)
                    print("血压sbp"+str(sbp)+"血压dpb"+str(dbp))
                    # 判断是否控制满意
                    is_satisfied = not (sbp >= threshold[0] or dbp >= threshold[1])

                    # 首先判断转诊状态
                    if prev_transfer_bp == 1:
                        if not is_satisfied:
                            print("prev_transfer_bp是1 并且控制不满意, 直接转诊,下次随访三个月后")
                            #这里要增加判断。如果历史转诊是1，并且这次是第一次追加控制不满意，继续追加，但是不转诊
                            delta = relativedelta(months=3)
                            return (date + delta).strftime("%Y-%m-%d")
                        else:
                            print("prev_transfer_bp是1 并且控制满意, 修改数据库的转诊状态改成0 ,下次随访三个月后")
                            # 更新转诊状态
                            sql = f"UPDATE bs_archives SET prev_transfer_bp = 0 WHERE idcard = %s"
                            cursor.execute(sql, (self.idcard,))
                            conn.commit()
                            delta = relativedelta(months=3)
                            return (date + delta).strftime("%Y-%m-%d")
                    else:
                        if is_satisfied:
                            print("prev_transfer_bp是0 并且控制满意, 下次随访三个月后")
                            delta = relativedelta(months=3)
                            return (date + delta).strftime("%Y-%m-%d")


                    # 1. 排序数据
                    def date_sort_key(item):
                        date_str = item['随访日期']
                        if not date_str:
                            return datetime.min  # 空日期排在最后
                        try:
                            return datetime.strptime(date_str, '%Y-%m-%d')
                        except ValueError:
                            return datetime.min  # 日期格式不正确，也排在最后

                    # 排序 all_visit_data
                    sorted_all_visit_data = sorted(all_visit_data, key=date_sort_key, reverse=True)  # 降序排序


                    # 2. 读取和计数，获取最近一次普通随访日期
                    last_normal_visit_date = None
                    read_count = 0
                    for item in sorted_all_visit_data:

                        if item['状态'] == '已访' and item['类型'] == '普通':
                            read_count += 1
                            try:
                                last_normal_visit_date = datetime.strptime(item['随访日期'], "%Y-%m-%d").date()
                                print(last_normal_visit_date)
                                break  # 找到 '类型': '普通' 的行，退出循环
                            except (ValueError, TypeError):
                                print("随访日期格式错误或为空，跳过")

                    print(f"读取了 {read_count} 行，直到找到 '类型': '普通' 的行。")

                    # 3. 计算从最近一次普通随访到现在的追加次数
                    additional_count = read_count - 1
                    print("总共"+str(additional_count)+"个追加")
                    if additional_count < 2:
                        # 判断是否达到危急值
                        if sbp >= 180 or dbp >= 110:
                            print("达到危急值, 立即转诊, 追加一次14天随访")
                            # 更新转诊状态
                            sql = f"UPDATE bs_archives SET prev_transfer_bp = 1 WHERE idcard = %s"
                            cursor.execute(sql, (self.idcard,))
                            conn.commit()
                            delta = relativedelta(days=14)
                            return (date + delta).strftime("%Y-%m-%d")
                        if sbp >= threshold[0] or dbp >= threshold[1]:
                            print("血压控制不满意, 历史追加次数小于或者等于1, 追加一次14天随访")
                            delta = relativedelta(days=14)
                        else:
                            print("血压控制满意, 增加三个月随访")
                            delta = relativedelta(months=3)
                        return (date + delta).strftime("%Y-%m-%d")
                    else:
                        print("从最近一次普通随访开始，追加次数大于1, 状态值设置为1,控制不满意，不论是否危急值，追加三个月")
                        # 更新转诊状态

                        sql = f"UPDATE bs_archives SET prev_transfer_bp = 1 WHERE idcard = %s"
                        cursor.execute(sql, (idcard,))
                        conn.commit()
                        delta = relativedelta(months=3)
                        return (date + delta).strftime("%Y-%m-%d")

        except pymysql.MySQLError as e:
            print(f"数据库操作失败: {e}")
            return ""
        except Exception as e:
            raise RuntimeError(f"获取转诊原因时发生错误: {str(e)}") from e


    def get_next_visit_dm(self,idcard,date,fbs,pbs,all_visit_data):
        """
        糖尿病随访日期计算
        返回格式: YYYY-MM-DD
        逻辑说明：
        1. 首先判断prev_transfer_dm状态值，如果状态值是1 ，直接转诊。下次随访时间三个月后，如果是0 .就继续下一步
        2. 判断是否达到危急值,如果达到危急值。就立即转诊，并且追加一次14天随访。并且给这个人标记状态，状态值1。后续除非控制满意，状态值归0，否则每次都转诊并且下次随访三个月后
        3. 判断历史追加次数。如果本次是第二次。就立即转诊。并且标记状态值1 .
        4.  控制不满意。历史追加次数小于2。就追加一次14天随访。
        5. 控制满意。 就增加三个月随访
        6. 血糖≥16.7mmol/L → 14天内随访 (危急值)
        7. 空腹血糖≥7.0mmol/L 或 随机血糖≥11.1mmol/L → 14天内随访
        8. 达标患者 → 3个月后随访
        """
        # Database Connection Settings (Same)

        # 连接数据库
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 查询转诊状态
                    sql = f"SELECT prev_transfer_dm FROM bs_archives WHERE idcard = %s"
                    cursor.execute(sql, (idcard,))
                    result = cursor.fetchone()

                    if result:
                        prev_transfer_dm = result['prev_transfer_dm']
                    else:
                        prev_transfer_dm = 0  # 默认不转诊

                    # 首先判断转诊状态
                    if prev_transfer_dm == 1:
                        # 判断是否控制满意
                        is_satisfied = (pbs < 11.1 if pbs > 0 else fbs < 7.0) if (pbs > 0 or fbs > 0) else True

                        if not is_satisfied:
                            print("prev_transfer_dm是1 并且控制不满意, 直接转诊,下次随访三个月后")
                            delta = relativedelta(months=3)
                            return (date + delta).strftime("%Y-%m-%d")
                        else:
                            print("prev_transfer_dm是1 并且控制满意, 修改数据库的转诊状态改成0 ,下次随访三个月后")
                            # 更新转诊状态
                            sql = f"UPDATE bs_archives SET prev_transfer_dm = 0 WHERE idcard = %s"
                            cursor.execute(sql, (idcard,))
                            conn.commit()
                            delta = relativedelta(months=3)
                            return (date + delta).strftime("%Y-%m-%d")
                    else:
                        is_satisfied = (pbs < 11.1 if pbs > 0 else fbs < 7.0) if (pbs > 0 or fbs > 0) else True
                        if is_satisfied:
                            print("prev_transfer_dm是0 并且控制满意, 下次随访三个月后")
                            delta = relativedelta(months=3)
                            return (date + delta).strftime("%Y-%m-%d")


                        # 1. 排序数据

                    def date_sort_key(item):
                        date_str = item['随访日期']
                        if not date_str:
                            return datetime.min  # 空日期排在最后
                        try:
                            return datetime.strptime(date_str, '%Y-%m-%d')
                        except ValueError:
                            return datetime.min  # 日期格式不正确，也排在最后

                        # 排序 all_visit_data

                    sorted_all_visit_data = sorted(all_visit_data, key=date_sort_key, reverse=True)  # 降序排序

                    # 排序 self.all_data (假设存在且需要排序)
                    sorted_self_all_data = sorted(self.all_data, key=date_sort_key, reverse=True)

                    # 2. 读取和计数，获取最近一次普通随访日期
                    last_normal_visit_date = None
                    read_count = 0
                    for item in sorted_all_visit_data:

                        if item['状态'] == '已访' and item['类型'] == '普通':
                            read_count += 1
                            try:
                                last_normal_visit_date = datetime.strptime(item['随访日期'], "%Y-%m-%d").date()
                                print(last_normal_visit_date)
                                break  # 找到 '类型': '普通' 的行，退出循环
                            except (ValueError, TypeError):
                                print("随访日期格式错误或为空，跳过")

                    print(f"读取了 {read_count} 行，直到找到 '类型': '普通' 的行。")
                    # 3. 计算从最近一次普通随访到现在的追加次数
                    additional_count = read_count - 1
                    print("总共"+str(additional_count)+"个追加")
                    print("血糖pbs"+str(pbs)+"血糖fbs"+str(fbs))
                    is_satisfied = (pbs < 11.1 if pbs > 0 else fbs < 7.0) if (pbs > 0 or fbs > 0) else True
                    if additional_count < 2:
                        # 判断是否达到危急值
                        if fbs >= 16.7:
                            print("第二次追加前达到危急值, 立即转诊, 14天随访, 状态值设置为1")
                            # 更新转诊状态
                            sql = f"UPDATE bs_archives SET prev_transfer_dm = 1 WHERE idcard = %s"
                            cursor.execute(sql, (idcard,))
                            conn.commit()
                            delta = relativedelta(days=14)
                            return (date + delta).strftime("%Y-%m-%d")
                        if not is_satisfied:
                            print("血糖控制不满意, 历史追加次数小于或者等于1, 追加一次14天随访")

                            delta = relativedelta(days=14)
                        else:
                            print("血糖控制满意, 增加三个月随访")
                            delta = relativedelta(months=3)
                        return (date + delta).strftime("%Y-%m-%d")
                    else:
                        print("从最近一次普通随访开始，追加次数大于1,控制不满意，不论是否危急值，下次随访三个月后, 状态值设置为1")
                        # 更新转诊状态
                        sql = f"UPDATE bs_archives SET prev_transfer_dm = 1 WHERE idcard = %s"
                        cursor.execute(sql, (idcard,))
                        conn.commit()
                        delta = relativedelta(months=3)
                        return (date + delta).strftime("%Y-%m-%d")
                # # 3. 计算从最近一次普通随访到现在的追加次数
                # additional_count = read_count - 1
                # print("总共" + str(additional_count) + "个追加")
                #
                # # 4. 判断历史追加次数
                # if additional_count >= 2:
                #     print("从最近一次普通随访开始，追加次数大于等于2, 立即转诊, 状态值设置为1")
                #     # 更新转诊状态
                #     sql = f"UPDATE {self.DB_TABLE} SET prev_transfer_bp = 1 WHERE idcard = %s"
                #     cursor.execute(sql, (self.idcard,))
                #     connection.commit()
                #     delta = relativedelta(months=3)
                #     return (visit_date + delta).strftime("%Y-%m-%d")
                # # 判断是否控制满意
                #
                #
                # if not is_satisfied:
                #     print("控制不满意, 历史追加次数小于2, 追加一次14天随访")
                #     delta = relativedelta(days=14)
                # else:
                #     print("控制满意, 增加三个月随访")
                #     delta = relativedelta(months=3)
                #
                # return (visit_date + delta).strftime("%Y-%m-%d")

        except pymysql.MySQLError as e:
            print(f"数据库操作失败: {e}")
            return ""
        except Exception as e:
            raise RuntimeError(f"获取转诊原因时发生错误: {str(e)}") from e
