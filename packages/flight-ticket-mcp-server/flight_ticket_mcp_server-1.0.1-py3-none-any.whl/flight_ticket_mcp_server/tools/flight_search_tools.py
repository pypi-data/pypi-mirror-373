"""
Flight Search Tools - 航班路线查询工具

提供根据出发地、目的地和出发日期查询航班路线的功能
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import random
import logging
import time
import re

# 初始化日志器
logger = logging.getLogger(__name__)

# 导入DrissionPage（可选）
try:
    from DrissionPage import ChromiumPage, ChromiumOptions
    DRISSION_PAGE_AVAILABLE = True
except ImportError:
    logger.warning("DrissionPage未安装，航班路线查询功能将不可用")
    ChromiumPage = None
    ChromiumOptions = None
    DRISSION_PAGE_AVAILABLE = False

# 导入城市字典
try:
    from ..utils.cities_dict import get_airport_code, get_city_name
except ImportError:
    logger.warning("城市字典未找到，航班路线查询功能将不可用")
    get_airport_code = None
    get_city_name = None











# =================== 航班路线查询功能 ===================

class FlightRouteSearcher:
    """航班路线查询器"""
    
    def __init__(self, headless=True):
        """
        初始化浏览器
        
        Args:
            headless: 是否使用无头模式
        """
        if not DRISSION_PAGE_AVAILABLE:
            raise ImportError("DrissionPage库未安装，无法使用航班路线查询功能")
        
        self.base_url = "https://flights.ctrip.com/online/list/oneway-{}-{}?_=1&depdate={}&cabin=Y_S_C_F"
        
        if headless:
            co = ChromiumOptions()
            co.headless()
            self.page = ChromiumPage(co)
        else:
            self.page = ChromiumPage()
        
        logger.info("航班路线查询器初始化完成")
    
    def search_flights(self, departure_city: str, destination_city: str, departure_date: str) -> List[Dict[str, Any]]:
        """
        搜索航班
        
        Args:
            departure_city: 出发城市
            destination_city: 目的地城市
            departure_date: 出发日期 (YYYY-MM-DD格式)
            
        Returns:
            航班信息列表
        """
        logger.info(f"开始搜索航班：{departure_city} -> {destination_city}, 日期：{departure_date}")
        
        # 获取机场代码
        departure_code = get_airport_code(departure_city)
        destination_code = get_airport_code(destination_city)
        
        if not departure_code or not destination_code:
            logger.warning(f"无法找到机场代码：出发地={departure_city}, 目的地={destination_city}")
            return []
        
        # 验证日期格式
        try:
            datetime.strptime(departure_date, '%Y-%m-%d')
        except ValueError:
            logger.warning(f"日期格式错误: {departure_date}")
            return []
        
        # 构建搜索URL
        search_url = self.base_url.format(departure_code, destination_code, departure_date)
        
        logger.info(f"搜索URL: {search_url}")
        logger.info(f"出发地：{get_city_name(departure_city)} ({departure_code.upper()})")
        logger.info(f"目的地：{get_city_name(destination_city)} ({destination_code.upper()})")
        
        try:
            # 访问页面
            self.page.get(search_url)
            logger.info("页面加载完成，等待内容渲染...")
            # 智能滚动加载更多内容
            self._intelligent_scroll_for_content()

            # 智能等待页面加载完成
            self._wait_for_page_ready()

            # 等待关键元素出现
            self._wait_for_flight_content()




            # 解析航班信息
            flights = self._parse_flights()

            logger.info(f"搜索完成，找到 {len(flights)} 条航班信息")
            return flights

        except Exception as e:
            logger.error(f"搜索航班失败: {str(e)}", exc_info=True)
            return []

    def _intelligent_scroll_for_content(self):
        """智能滚动以加载更多航班内容"""
        print("🔄 智能滚动加载航班内容...")

        try:
            # 先向下滚动几次，加载初始内容
            scroll_distances = [500, 800, 1200]

            for i, distance in enumerate(scroll_distances, 1):
                self.page.scroll(distance)
                print(f"📜 第{i}次向下滚动 {distance}px")
                time.sleep(1.5)  # 等待内容加载

                # 检查是否有新的航班元素加载出来
                flight_elements = self.page.eles('css:.flight-item', timeout=1)
                print(f"   当前页面航班元素数量：{len(flight_elements)}")

            # 滚动回到顶部，确保能看到所有航班
            print("🔝 滚动回到页面顶部")
            self.page.scroll(-2000)  # 向上滚动回到顶部
            time.sleep(1)

        except Exception as e:
            print(f"⚠️ 智能滚动过程中出错：{e}")
    def _wait_for_flight_content(self, timeout=30):
        """等待航班内容加载"""
        print("⏳ 等待航班内容加载...")

        # 方法1：等待航班容器出现
        flight_container = self.page.ele('css:.body-wrapper', timeout=timeout)
        if flight_container:
            print("✅ 找到航班容器")

            # 方法2：等待航班列表出现
            flight_items = self.page.ele('css:.flight-item', timeout=10)
            if flight_items:
                print("✅ 航班列表加载完成")
            else:
                print("⚠️ 等待航班列表超时，尝试其他解析方法...")

                # 等待可能的加载指示器消失
                self._wait_for_loading_complete()
        else:
            print("❌ 航班容器未找到")
    def _wait_for_page_ready(self, timeout=30):
        """智能等待页面完全加载"""
        print("⏳ 等待页面完全加载...")

        # 方法1：等待 document.readyState 为 complete
        start_time = time.time()
        while time.time() - start_time < timeout:
            ready_state = self.page.run_js("return document.readyState")
            if ready_state == "complete":
                print("✅ 页面DOM加载完成")
                break
            time.sleep(0.5)
        else:
            print("⚠️ 页面加载超时，继续执行...")

        # 方法2：等待jQuery加载完成（如果页面使用jQuery）
        if self._wait_for_jquery_ready():
            print("✅ jQuery加载完成")

        # 方法3：等待Ajax请求完成
        if self._wait_for_ajax_complete():
            print("✅ Ajax请求完成")

    def _wait_for_ajax_complete(self, timeout=10):
        """等待Ajax请求完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # 检查是否有活跃的Ajax请求
                ajax_complete = self.page.run_js("""
                    if (typeof XMLHttpRequest !== 'undefined') {
                        return XMLHttpRequest.active === 0 || XMLHttpRequest.active === undefined;
                    }
                    return true;
                """)
                if ajax_complete:
                    return True
            except:
                pass
            time.sleep(0.2)
        return False

    def _wait_for_jquery_ready(self, timeout=10):
        """等待jQuery加载完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                jquery_active = self.page.run_js("return typeof jQuery !== 'undefined' && jQuery.active === 0")
                if jquery_active:
                    return True
            except:
                pass
            time.sleep(0.2)
        return False
    def _wait_for_loading_complete(self, timeout=15):
        """等待加载指示器消失"""
        print("⏳ 等待加载指示器消失...")

        # 常见的加载指示器选择器
        loading_selectors = [
            '.loading',
            '.spinner',
            '.loader',
            '#loading',
            '[data-loading]',
            '.fa-spinner',
            '.loading-overlay'
        ]

        for selector in loading_selectors:
            try:
                # 等待加载指示器消失
                start_time = time.time()
                while time.time() - start_time < timeout:
                    loader = self.page.ele(f'css:{selector}', timeout=1)
                    if not loader:
                        break
                    time.sleep(0.5)
                else:
                    continue
                print(f"✅ 加载指示器 {selector} 已消失")
                break
            except:
                continue

    def _parse_flights(self) -> List[Dict[str, Any]]:
        """解析航班信息"""
        flights = []

        try:
            # 查找航班容器
            flight_list = self.page.ele('css:.body-wrapper')
            if not flight_list:
                logger.warning("未找到航班容器")
                return []

            # 查找航班项
            flight_containers = flight_list.eles('css:.flight-item')
            if not flight_containers:
                logger.warning("未找到航班项")
                return []

            logger.info(f"找到 {len(flight_containers)} 个航班容器")

            # 选取存在航班号的10个航班
            valid_flights_count = 0
            for i, container in enumerate(flight_containers):
                if valid_flights_count >= 10:  # 已找到10个有效航班，停止搜索
                    break

                try:
                    flight_info = self._parse_flight_container(container, i + 1)
                    if flight_info and flight_info.get('航班号') and flight_info.get('航班号') != '未知':
                        # 只有当航班号存在且不是'未知'时才添加
                        flights.append(flight_info)
                        valid_flights_count += 1
                        logger.debug(f"成功解析航班 {valid_flights_count}: {flight_info.get('航班号')}")
                    else:
                        logger.debug(f"航班容器 {i+1} 无有效航班号，跳过")

                except Exception as e:
                    logger.error(f"解析航班容器 {i+1} 出错: {str(e)}")
                    continue

            logger.info(f"成功找到 {valid_flights_count} 个有航班号的航班")
            return flights
            
        except Exception as e:
            logger.error(f"解析航班信息失败: {str(e)}", exc_info=True)
            return []
    
    def _parse_flight_container(self, container, index: int) -> Optional[Dict[str, Any]]:
        """
        解析单个航班容器
        
        Args:
            container: 航班容器元素
            index: 航班序号
            
        Returns:
            航班信息字典
        """
        flight_info = {'序号': index}
        
        try:
            # 解析航空公司
            airline_span = container.ele('css:.airline-name span', timeout=1)
            if airline_span:
                flight_info['航空公司'] = airline_span.text.strip()
            
            # 解析航班号
            plane_no_span = container.ele('css:.plane-No', timeout=1)
            if plane_no_span:
                plane_text = plane_no_span.text.strip()
                # 提取航班号（如MU6863）
                flight_match = re.search(r'([A-Z]{2}\d{3,4})', plane_text)
                if flight_match:
                    flight_info['航班号'] = flight_match.group(1)
            
            # 解析出发时间
            depart_time = container.ele('css:.depart-box .time', timeout=1)
            if depart_time:
                flight_info['出发时间'] = depart_time.text.strip()
            
            # 解析出发机场
            depart_airport = container.ele('css:.depart-box .name', timeout=1)
            if depart_airport:
                flight_info['出发机场'] = depart_airport.text.strip()
            
            # 解析出发航站楼
            depart_terminal = container.ele('css:.depart-box .terminal', timeout=1)
            if depart_terminal:
                flight_info['出发航站楼'] = depart_terminal.text.strip()
            
            # 解析到达时间
            arrive_time = container.ele('css:.arrive-box .time', timeout=1)
            if arrive_time:
                arrival_text = arrive_time.text.strip()
                # 处理跨天信息
                if '+1天' in arrival_text:
                    flight_info['到达时间'] = arrival_text.replace('+1天', ' +1天')
                else:
                    flight_info['到达时间'] = arrival_text
            
            # 解析到达机场
            arrive_airport = container.ele('css:.arrive-box .name', timeout=1)
            if arrive_airport:
                flight_info['到达机场'] = arrive_airport.text.strip()
            
            # 解析到达航站楼
            arrive_terminal = container.ele('css:.arrive-box .terminal', timeout=1)
            if arrive_terminal:
                flight_info['到达航站楼'] = arrive_terminal.text.strip()
            
            # 解析价格
            price_span = container.ele('css:.price', timeout=1)
            if price_span:
                price_text = price_span.text.strip()
                # 处理价格格式
                if '¥' in price_text:
                    flight_info['价格'] = price_text
                else:
                    # 提取数字价格
                    price_match = re.search(r'(\d+)', price_text)
                    if price_match:
                        flight_info['价格'] = f"¥{price_match.group(1)}"
            
            # 检查是否有足够的信息
            if any(key in flight_info for key in ['航班号', '出发时间', '价格']):
                return flight_info
            else:
                logger.debug(f"航班 {index} 缺少必要信息")
                return None
                
        except Exception as e:
            logger.error(f"解析航班容器 {index} 详细信息失败: {str(e)}")
            return None
    
    def close(self):
        """关闭浏览器"""
        if hasattr(self, 'page'):
            self.page.quit()
            logger.info("浏览器已关闭")


def searchFlightRoutes(departure_city: str, destination_city: str, departure_date: str) -> Dict[str, Any]:
    """
    根据出发地、目的地和出发日期查询航班路线
    
    Args:
        departure_city: 出发城市名称或机场代码
        destination_city: 目的地城市名称或机场代码
        departure_date: 出发日期 (YYYY-MM-DD格式)
        
    Returns:
        包含航班查询结果的字典
    """
    logger.info(f"开始查询航班路线: {departure_city} -> {destination_city}, 日期: {departure_date}")
    
    try:
        # 验证输入参数
        if not departure_city or not destination_city or not departure_date:
            logger.warning("参数不完整")
            return {
                "status": "error",
                "message": "出发地、目的地和出发日期都不能为空",
                "error_code": "INVALID_PARAMS"
            }
        
        # 检查依赖是否可用
        if not DRISSION_PAGE_AVAILABLE:
            logger.error("DrissionPage库未安装")
            return {
                "status": "error",
                "message": "DrissionPage库未安装，无法进行航班搜索",
                "error_code": "DRISSION_PAGE_NOT_AVAILABLE"
            }
        
        if not get_airport_code or not get_city_name:
            logger.error("城市字典未找到")
            return {
                "status": "error",
                "message": "城市字典未找到，无法进行航班搜索",
                "error_code": "CITIES_DICT_NOT_AVAILABLE"
            }
        
        # 验证日期格式
        try:
            flight_date = datetime.strptime(departure_date, "%Y-%m-%d")
            logger.debug(f"日期解析成功: {flight_date}")
        except ValueError:
            logger.warning(f"日期格式错误: {departure_date}")
            return {
                "status": "error",
                "message": "日期格式不正确，请使用YYYY-MM-DD格式",
                "error_code": "INVALID_DATE_FORMAT"
            }
        
        # 检查日期是否为过去的日期
        if flight_date.date() < datetime.now().date():
            logger.warning(f"查询过去的日期: {departure_date}")
            return {
                "status": "error",
                "message": "不能查询过去的日期",
                "error_code": "PAST_DATE"
            }
        
        # 验证城市/机场代码
        if not get_airport_code(departure_city):
            logger.warning(f"无效的出发地: {departure_city}")
            return {
                "status": "error",
                "message": f"无效的出发地: {departure_city}",
                "error_code": "INVALID_DEPARTURE_CITY"
            }
        
        if not get_airport_code(destination_city):
            logger.warning(f"无效的目的地: {destination_city}")
            return {
                "status": "error",
                "message": f"无效的目的地: {destination_city}",
                "error_code": "INVALID_DESTINATION_CITY"
            }
        
        # 创建搜索器并搜索
        searcher = FlightRouteSearcher(headless=True)
        
        try:
            flights = searcher.search_flights(departure_city, destination_city, departure_date)
            
            # 格式化结果
            result = {
                "status": "success",
                "departure_city": departure_city,
                "destination_city": destination_city,
                "departure_date": departure_date,
                "departure_airport": get_city_name(departure_city),
                "destination_airport": get_city_name(destination_city),
                "flight_count": len(flights),
                "flights": flights,
                "formatted_output": _format_route_result(flights, departure_city, destination_city, departure_date),
                "query_time": datetime.now().isoformat()
            }
            
            # 添加统计信息
            if flights:
                prices = []
                airlines = {}
                
                for flight in flights:
                    # 提取价格
                    if '价格' in flight and flight['价格'] != '未知':
                        price_str = flight['价格'].replace('¥', '').replace('起', '')
                        if price_str.isdigit():
                            prices.append(int(price_str))
                    
                    # 统计航空公司
                    airline = flight.get('航空公司', '未知')
                    airlines[airline] = airlines.get(airline, 0) + 1
                
                if prices:
                    result["price_statistics"] = {
                        "min_price": min(prices),
                        "max_price": max(prices),
                        "avg_price": sum(prices) // len(prices)
                    }
                
                if airlines:
                    result["airline_statistics"] = airlines
            
            logger.info(f"航班路线查询成功: 找到 {len(flights)} 条航班")
            return result
            
        finally:
            searcher.close()
            
    except Exception as e:
        logger.error(f"查询航班路线失败: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"查询航班路线失败: {str(e)}",
            "error_code": "SEARCH_FAILED"
        }


def _format_route_result(flights: List[Dict[str, Any]], departure_city: str, destination_city: str, departure_date: str) -> str:
    """
    格式化航班路线查询结果
    
    Args:
        flights: 航班列表
        departure_city: 出发城市
        destination_city: 目的地城市
        departure_date: 出发日期
        
    Returns:
        格式化后的字符串
    """
    if not flights:
        return f"😔 未找到 {departure_city} -> {destination_city} 在 {departure_date} 的航班"
    
    output = []
    output.append(f"✈️ 航班查询结果")
    output.append(f"📍 {get_city_name(departure_city)} -> {get_city_name(destination_city)}")
    output.append(f"📅 {departure_date}")
    output.append(f"🔢 共找到 {len(flights)} 条航班")
    output.append("")
    
    # 显示航班列表
    for i, flight in enumerate(flights, 1):
        output.append(f"【{i}】{flight.get('航空公司', '未知')} {flight.get('航班号', '未知')}")
        output.append(f"    🛫 {flight.get('出发时间', '未知')} {flight.get('出发机场', '未知')} {flight.get('出发航站楼', '')}")
        output.append(f"    🛬 {flight.get('到达时间', '未知')} {flight.get('到达机场', '未知')} {flight.get('到达航站楼', '')}")
        output.append(f"    💰 {flight.get('价格', '未知')}")
        output.append("")
    
    return "\n".join(output) 